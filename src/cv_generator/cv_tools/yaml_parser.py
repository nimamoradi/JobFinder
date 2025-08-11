import yaml
from typing import Any, Dict, List, Optional


class Loader:
    def __init__(self, yaml_file_path: str):
        """
        Initialize the Loader with a YAML file path.

        Args:
            yaml_file_path (str): Path to the YAML file
        """
        self._yaml_file_path = yaml_file_path
        self._config_data: Dict[str, Any] = {}
        self._load_yaml()
    # will get the raw yaml file as string
    def get_raw(self):
        return str(self._config_data)

    def _load_yaml(self) -> None:
        """
        Load the YAML file and store its contents.

        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            yaml.YAMLError: If there's an error parsing the YAML file
        """
        try:
            with open(self._yaml_file_path, 'r') as file:
                self._config_data = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {self._yaml_file_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {str(e)}")

    def get_value(self, key: str) -> Optional[Any]:
        """
        Get a value from the YAML data using a key.

        Args:
            key (str): The key to look up

        Returns:
            Optional[Any]: The value associated with the key, or None if not found
        """
        return self._config_data.get(key)

    def get_nested_value(self, *keys: str) -> Optional[Any]:
        """
        Get a nested value from the YAML data using a sequence of keys.

        Args:
            *keys: Variable number of keys to traverse the nested structure

        Returns:
            Optional[Any]: The value at the specified nested location, or None if not found
        """
        current = self._config_data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return None
            else:
                return None
        return current

    def reload(self) -> None:
        """
        Reload the YAML file contents.
        """
        self._load_yaml()

    @property
    def data(self) -> Dict[str, Any]:
        """
        Get all configuration data.

        Returns:
            Dict[str, Any]: The complete configuration data
        """
        return self._config_data.copy()
