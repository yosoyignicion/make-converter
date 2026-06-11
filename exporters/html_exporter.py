import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from exporters.base import BaseExporter


TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_NAME = "reference.html"


class HTMLExporter(BaseExporter):
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def export(self, databag: dict, output_path: str) -> str:
        path = output_path
        if not path.endswith(".html"):
            path += ".html"

        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)

        template = self.env.get_template(TEMPLATE_NAME)
        html = template.render(**databag)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        return path
