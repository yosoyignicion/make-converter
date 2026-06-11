import zipfile
import tempfile
import os
import shutil
from pathlib import Path


ZIP_MAGIC = b"PK\x03\x04"
EXPECTED_FILES = {"meta.json", "ai_chat.json", "canvas.fig"}


class ExtractError(Exception):
    pass


def is_make_file(path: str) -> bool:
    with open(path, "rb") as f:
        header = f.read(4)
    return header == ZIP_MAGIC


def extract(path: str) -> str:
    path = str(path)
    if not os.path.isfile(path):
        raise ExtractError(f"Archivo no encontrado: {path}")

    if not is_make_file(path):
        raise ExtractError(
            "Formato no soportado. Solo archivos .make (ZIP Figma Make)."
        )

    tmp_dir = tempfile.mkdtemp(prefix="ocmake_")

    try:
        with zipfile.ZipFile(path, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                raise ExtractError(
                    f"ZIP corrupto: '{bad}' tiene errores. "
                    "Re-exporta desde Figma Make."
                )
            zf.extractall(tmp_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise ExtractError(
            "Archivo ZIP inválido o corrupto. Re-exporta desde Figma Make."
        )

    extracted = set(os.listdir(tmp_dir))
    missing = EXPECTED_FILES - extracted
    if missing:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise ExtractError(
            f"Estructura .make incompleta. Faltan: {', '.join(sorted(missing))}"
        )

    return tmp_dir
