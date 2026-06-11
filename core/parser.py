import json
import os
from pathlib import Path


class ParseError(Exception):
    pass


def parse_meta(extract_dir: str) -> dict:
    path = os.path.join(extract_dir, "meta.json")
    if not os.path.isfile(path):
        raise ParseError("meta.json no encontrado en la extracción.")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("client_meta", {})
    bg = meta.get("background_color", {})
    r, g, b = bg.get("r", 0), bg.get("g", 0), bg.get("b", 0)
    bg_hex = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    thumb_size = meta.get("thumbnail_size", {})
    canvas = meta.get("render_coordinates", {})

    return {
        "name": data.get("file_name", "Untitled"),
        "exported_at": data.get("exported_at", ""),
        "background_color": bg,
        "background_hex": bg_hex,
        "thumbnail_size": {
            "width": thumb_size.get("width", 0),
            "height": thumb_size.get("height", 0),
        },
        "canvas_size": {
            "width": canvas.get("width", 0),
            "height": canvas.get("height", 0),
        },
    }


def parse_conversation(extract_dir: str) -> list:
    path = os.path.join(extract_dir, "ai_chat.json")
    if not os.path.isfile(path):
        raise ParseError("ai_chat.json no encontrado en la extracción.")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    threads = data.get("threads", [])
    if not threads:
        return []

    messages = threads[0].get("messages", [])
    result = []

    for msg in messages:
        entry = {
            "index": msg.get("index", 0),
            "role": msg.get("role", "unknown"),
            "timestamp": msg.get("createdAt", ""),
            "text": "",
            "model": None,
        }

        parts = msg.get("parts", [])
        for part in parts:
            if part.get("partType") == "text":
                try:
                    content = json.loads(part.get("contentJson", "{}"))
                    entry["text"] = content.get("text", "")
                except (json.JSONDecodeError, TypeError):
                    entry["text"] = part.get("contentJson", "")
            elif part.get("partType") == "code-chat-model-config-version":
                try:
                    config = json.loads(part.get("contentJson", "{}"))
                    version = config.get("modelConfigVersion", "")
                    if version:
                        entry["model"] = version.split("_")[0]
                except (json.JSONDecodeError, TypeError):
                    pass

        if not entry["text"] and not entry["model"]:
            continue

        result.append(entry)

    return result


def load_images(extract_dir: str) -> list:
    images_dir = os.path.join(extract_dir, "images")
    if not os.path.isdir(images_dir):
        return []

    images = []
    for fname in sorted(os.listdir(images_dir)):
        fpath = os.path.join(images_dir, fname)
        if os.path.isfile(fpath):
            with open(fpath, "rb") as f:
                data = f.read()
            images.append({"filename": fname, "data": data, "size": len(data)})
    return images


def load_thumbnail(extract_dir: str) -> bytes | None:
    path = os.path.join(extract_dir, "thumbnail.png")
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    return None


def load_canvas_fig(extract_dir: str) -> bytes | None:
    path = os.path.join(extract_dir, "canvas.fig")
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    return None
