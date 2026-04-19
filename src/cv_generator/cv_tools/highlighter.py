import re
from typing import Dict, Iterable, List, Optional, Tuple, Union


class LatexHighlighter:
    """Bold important keywords using LaTeX \textbf{} with usage limits.

    - Provide keywords (optionally with importance 1..5) in the constructor.
    - Call highlight(text) for each section's text; it returns updated text.
    - Tracks how many times each keyword has been bolded overall and prevents
      overuse (max per keyword, default 2) and limits per-text additions (default 4).
    """

    def __init__(
        self,
        keywords: Optional[Union[Iterable[str], Dict[str, int], Iterable[Tuple[str, int]]]] = None,
        max_per_text: int = 4,
        max_per_keyword: int = 2,
    ) -> None:
        # Normalize keywords -> importance map (1..5)
        self._importance: Dict[str, int] = {}
        self._patterns: Dict[str, re.Pattern] = {}
        self._order: List[str] = []
        self._max_per_text = max(0, int(max_per_text))
        self._max_per_keyword = max(1, int(max_per_keyword))
        self._counts: Dict[str, int] = {}

        if keywords is not None:
            self.add_keywords(keywords)

    @staticmethod
    def _clamp_importance(v: int) -> int:
        try:
            vi = int(v)
        except Exception:
            return 3
        return max(1, min(5, vi))

    @staticmethod
    def _word_pattern(term: str) -> str:
        # Use non-word boundaries to avoid partial matches where possible
        esc = re.escape(term)
        return rf"(?<!\w)({esc})(?!\w)"

    @staticmethod
    def _bold_spans(text: str) -> List[Tuple[int, int]]:
        spans: List[Tuple[int, int]] = []
        for m in re.finditer(r"\\textbf\{[^{}]*\}", text):
            spans.append((m.start(), m.end()))
        return spans

    @staticmethod
    def _in_spans(idx: int, spans: List[Tuple[int, int]]) -> bool:
        for s, e in spans:
            if s <= idx < e:
                return True
        return False

    def _reindex(self) -> None:
        self._patterns = {k: re.compile(self._word_pattern(k), flags=re.IGNORECASE) for k in self._importance}
        self._order = sorted(self._importance, key=lambda k: (self._importance[k], len(k)), reverse=True)
        for k in self._importance:
            self._counts.setdefault(k, 0)

    def add_keywords(
        self, keywords: Union[Iterable[str], Dict[str, int], Iterable[Tuple[str, int]]]
    ) -> None:
        if isinstance(keywords, dict):
            for k, v in keywords.items():
                if not k:
                    continue
                self._importance[k.strip()] = self._clamp_importance(v)
        else:
            for item in keywords:
                if isinstance(item, dict):
                    term = item.get("keyword") or item.get("term") or item.get("name") or item.get("skill")
                    if term:
                        self._importance[str(term).strip()] = self._clamp_importance(item.get("importance", 3))
                elif isinstance(item, tuple):
                    k, v = item
                    if not k:
                        continue
                    self._importance[str(k).strip()] = self._clamp_importance(v)
                else:
                    k = str(item)
                    if not k:
                        continue
                    self._importance[k.strip()] = 3
        self._reindex()

    # Removed: load_keywords_from_summary. Pass already-parsed keyword list in constructor or via add_keywords.

    def highlight(self, text: str) -> str:
        if not isinstance(text, str) or not text:
            return text

        added = 0
        spans = self._bold_spans(text)

        for kw in self._order:
            if added >= self._max_per_text:
                break
            if self._counts.get(kw, 0) >= self._max_per_keyword:
                continue

            pat = self._patterns[kw]

            # Find first eligible occurrence not already bolded
            m = pat.search(text)
            while m and self._in_spans(m.start(), spans):
                m = pat.search(text, m.end())

            if not m:
                continue

            # Apply bolding once for this keyword in this call
            start, end = m.start(), m.end()
            original = text[start:end]
            replacement = "\\textbf{" + original + "}"
            text = text[:start] + replacement + text[end:]
            # Update spans and counters
            delta = len(replacement) - (end - start)
            spans = [(s if s < start else s + delta, e if e < start else e + delta) for (s, e) in spans]
            spans.append((start, start + len(replacement)))
            self._counts[kw] = self._counts.get(kw, 0) + 1
            added += 1

        return text

    def usage(self) -> Dict[str, int]:
        return dict(self._counts)
