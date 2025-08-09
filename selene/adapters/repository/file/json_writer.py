from pathlib import Path
from typing import Dict, List


class WriterInterface:
    """Interface for writing data to files."""

    def write(self, file_path: str, headers: List[str], data: List[Dict]) -> None:
        """Write data to a file."""
        pass


class JSONWriter(WriterInterface):
    """Writer for JSON files."""

    def write(self, file_path: str, headers: List[str], data: List[Dict]) -> None:
        """Write data to a JSON file."""
        import json

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=2)
