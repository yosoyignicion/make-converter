import os
import tempfile
from exporters.html_exporter import HTMLExporter


class TestHTMLExporter:
    def setup_method(self):
        self.exporter = HTMLExporter()
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _export(self, databag, name="test"):
        path = os.path.join(self.tmp, f"{name}.html")
        return self.exporter.export(databag, path)

    def test_export_creates_file(self, databag):
        path = self._export(databag)
        assert os.path.isfile(path)
        assert path.endswith(".html")

    def test_export_self_contained(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_export_contains_title(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert databag["design"]["name"] in html

    def test_export_conversation_section(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert "Conversación Figma AI" in html

    def test_export_embedded_thumbnail(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert "data:image/png;base64" in html

    def test_export_embedded_canvas_fig(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert "data:application/octet-stream" in html

    def test_export_role_css_classes(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        assert "msg-user" in html
        assert "msg-assistant" in html

    def test_export_assets_section(self, databag):
        path = self._export(databag)
        with open(path) as f:
            html = f.read()
        if databag["images"]:
            assert "Assets del Diseño" in html

    def test_export_adds_extension(self, databag):
        path = self.exporter.export(databag, os.path.join(self.tmp, "noext"))
        assert path.endswith(".html")
