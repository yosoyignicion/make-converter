import os
import json
from core.extractor import extract
from core.parser import parse_meta, parse_conversation, load_images, load_thumbnail, load_canvas_fig


class TestParser:
    def setup_method(self):
        self.extract_dir = None

    def _extract(self, oc_make_path):
        self.extract_dir = extract(oc_make_path)
        return self.extract_dir

    def teardown_method(self):
        if self.extract_dir and os.path.isdir(self.extract_dir):
            import shutil
            shutil.rmtree(self.extract_dir, ignore_errors=True)

    def test_parse_meta(self, oc_make_path):
        d = self._extract(oc_make_path)
        meta = parse_meta(d)
        assert meta["name"] == "TestFixture"
        assert meta["background_hex"].startswith("#")
        assert meta["canvas_size"]["width"] > 0
        assert meta["thumbnail_size"]["width"] > 0
        assert "exported_at" in meta

    def test_parse_conversation(self, oc_make_path):
        d = self._extract(oc_make_path)
        conv = parse_conversation(d)
        assert len(conv) > 0
        roles = {m["role"] for m in conv}
        assert "user" in roles
        assert "assistant" in roles
        first = conv[0]
        assert "timestamp" in first
        assert "text" in first

    def test_parse_conversation_first_message(self, oc_make_path):
        d = self._extract(oc_make_path)
        conv = parse_conversation(d)
        first_user = next(m for m in conv if m["role"] == "user")
        assert len(first_user["text"]) > 0
        assert first_user["model"] is not None

    def test_load_images(self, oc_make_path):
        d = self._extract(oc_make_path)
        images = load_images(d)
        assert len(images) >= 1
        for img in images:
            assert "filename" in img
            assert len(img["data"]) > 0

    def test_load_thumbnail(self, oc_make_path):
        d = self._extract(oc_make_path)
        thumb = load_thumbnail(d)
        assert thumb is not None
        assert len(thumb) > 0

    def test_load_canvas_fig(self, oc_make_path):
        d = self._extract(oc_make_path)
        fig = load_canvas_fig(d)
        assert fig is not None
        assert len(fig) > 0
