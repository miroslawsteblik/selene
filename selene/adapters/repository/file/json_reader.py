# adapters/file/json_writer.py
import json
import logging
from pathlib import Path
from typing import Any, Dict


class JSONWriter:
    """Adapter for writing JSON files."""

    def __init__(self, file_path: str, encoding: str = "utf-8", indent: int = 2):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.indent = indent
        self._logger = logging.getLogger(__name__)

    def write(self, data: Dict[str, Any]) -> None:
        """Write data to JSON file."""
        self._logger.debug(f"Writing JSON file: {self.file_path}")

        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "w", encoding=self.encoding) as file:
            json.dump(data, file, indent=self.indent, ensure_ascii=False)

        self._logger.info(f"Successfully wrote JSON file: {self.file_path}")
