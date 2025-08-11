def extract_json_content(text):
    start_marker = '```json'
    end_marker = '```'

    # Find the start position after the json marker
    start_pos = text.find(start_marker)
    if start_pos == -1:
        return text
    start_pos += len(start_marker)

    # Find the end position
    end_pos = text.find(end_marker, start_pos)
    if end_pos == -1:
        return text[start_pos:]  # Return rest of string if no end marker

    # Extract and return the content between markers
    return text[start_pos:end_pos].strip()


class LLM_interface:

    def __init__(self):
        pass

    def ask(self, prompt, be_json=False):
        raise NotImplementedError

    def swap_model(self, model_name):
        raise NotImplementedError
