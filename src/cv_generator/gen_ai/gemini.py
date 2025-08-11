import json
import os

from google import genai

from gen_ai.llm_interface import extract_json_content, LLM_interface

import re

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
    else: # For int, float, bool, None, etc.
        return data
class AskGemini(LLM_interface):
    def __init__(self, model_name):
        # Load environment variables from .env file
        super().__init__()
        # Access environment variables
        api_key = os.getenv('gemini_api_key')
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    # The final, unified 'ask' method
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
            # 1. Parse the JSON string into a Python object.
            #    (Assuming you have an extract_json_content function)
            parsed_json = json.loads(extract_json_content(response.text))

            # 2. Recursively escape all string values within the parsed object
            #    and return the result.
            return escape_latex_in_json(parsed_json)
        else:
            # If raw text is expected, just escape the entire text response.
            return escape_latex(response.text)

    def swap_model(self, model_name):
        self._model_name = model_name
