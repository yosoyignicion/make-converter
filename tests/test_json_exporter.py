import os
import json
import tempfile
from exporters.json_exporter import JSONExporter


class TestJSONExporter:
    def setup_method(self):
        self.exporter = JSONExporter()
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _export(self, databag, name="test"):
        path = os.path.join(self.tmp, f"{name}.json")
        return self.exporter.export(databag, path)

    def test_export_creates_file(self, databag):
        path = self._export(databag)
        assert os.path.isfile(path)

    def test_export_valid_json(self, databag):
        path = self._export(databag)
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_export_contains_all_keys(self, databag):
        path = self._export(databag)
        with open(path) as f:
            data = json.load(f)
        expected = {"source_file", "exported_at", "design", "conversation", "thumbnail_b64", "canvas_fig_b64", "images", "stats"}
        assert expected.issubset(data.keys())

    def test_export_conversation_preserved(self, databag):
        path = self._export(databag)
        with open(path) as f:
            data = json.load(f)
        assert len(data["conversation"]) == len(databag["conversation"])
        assert data["conversation"][0]["role"] == "user"

    def test_export_stats_integrity(self, databag):
        path = self._export(databag)
        with open(path) as f:
            data = json.load(f)
        s = data["stats"]
        assert s["total_messages"] == len(data["conversation"])
        assert s["total_images"] == len(data["images"])

    def test_export_adds_extension(self, databag):
        path = self.exporter.export(databag, os.path.join(self.tmp, "noext"))
        assert path.endswith(".json")

    def test_export_roundtrip(self, databag):
        path = self._export(databag)
        with open(path) as f:
            data = json.load(f)
        assert data["source_file"] == databag["source_file"]
        assert data["design"]["name"] == databag["design"]["name"]
