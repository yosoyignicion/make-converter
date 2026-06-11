import os
import pytest
from core.extractor import extract, is_make_file, ExtractError


def test_is_make_file(oc_make_path):
    assert is_make_file(oc_make_path) is True


def test_is_make_file_rejects_random_file(tmp_path):
    f = tmp_path / "fake.txt"
    f.write_text("not a zip")
    assert is_make_file(str(f)) is False


def test_extract_creates_temp_dir(oc_make_path):
    extract_dir = extract(oc_make_path)
    try:
        assert os.path.isdir(extract_dir)
        assert os.path.isfile(os.path.join(extract_dir, "meta.json"))
        assert os.path.isfile(os.path.join(extract_dir, "ai_chat.json"))
        assert os.path.isfile(os.path.join(extract_dir, "canvas.fig"))
    finally:
        import shutil
        shutil.rmtree(extract_dir, ignore_errors=True)


def test_extract_non_zip(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    with pytest.raises(ExtractError, match="Solo archivos .make"):
        extract(str(f))


def test_extract_nonexistent():
    with pytest.raises(ExtractError, match="no encontrado"):
        extract("/no/existe/make.make")
