import json
import os
from exporters.base import BaseExporter


class JSONExporter(BaseExporter):
    def export(self, databag: dict, output_path: str) -> str:
        path = output_path
        if not path.endswith(".json"):
            path += ".json"

        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(databag, f, indent=2, ensure_ascii=False)

        return path
