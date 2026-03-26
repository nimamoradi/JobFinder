import json
import os
import re

from google import genai

# Support both package layouts:
# - CodeUri: src/cv_generator (imports like 'gen_ai.*')
# - CodeUri: src (imports like 'cv_generator.gen_ai.*')
try:
    from gen_ai.llm_interface import extract_json_content, LLM_interface
except ModuleNotFoundError:
    from cv_generator.gen_ai.llm_interface import extract_json_content, LLM_interface


def escape_latex(text: str) -> str:
    """
    Escapes special LaTeX characters in a single string.
    """
    if not isinstance(text, str):
        return text

    special_chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', '\\': r'\textbackslash{}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in special_chars.keys()))
    return pattern.sub(lambda m: special_chars[m.group(0)], text)


def escape_latex_in_json(data):
    """
    Recursively walks a data structure (dict or list from a parsed JSON)
    and applies LaTeX escaping to all string values found within.
    """
    if isinstance(data, dict):
        return {key: escape_latex_in_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [escape_latex_in_json(element) for element in data]
    elif isinstance(data, str):
        return escape_latex(data)
    else:  # For int, float, bool, None, etc.
        return data


class AskGemini(LLM_interface):
    def __init__(self, model_name):
        super().__init__()
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('gemini_api_key')
        if not api_key:
            raise ValueError('Gemini API key is not set. Use GEMINI_API_KEY or gemini_api_key.')
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def ask(self, prompt, be_json=False):
        """
        Sends a prompt to the Gemini API and returns a LaTeX-safe response.

        - If be_json is False: Returns raw text with special characters escaped.
        - If be_json is True: Returns a JSON object where all internal
          string values have also been escaped for LaTeX.
        """
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
        )

        if be_json:
            parsed_json = json.loads(extract_json_content(response.text))
            return escape_latex_in_json(parsed_json)
        return escape_latex(response.text)

    def swap_model(self, model_name):
        self._model_name = model_name
