import base64
import os
from core.extractor import extract, ExtractError
from core.parser import (
    parse_meta,
    parse_conversation,
    load_images,
    load_thumbnail,
    load_canvas_fig,
    ParseError,
)


class AssembleError(Exception):
    pass


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def assemble(make_path: str) -> dict:
    if not os.path.isfile(make_path):
        raise AssembleError(f"Archivo no encontrado: {make_path}")

    extract_dir = None
    try:
        extract_dir = extract(make_path)
        meta = parse_meta(extract_dir)
        conversation = parse_conversation(extract_dir)
        images = load_images(extract_dir)
        thumb_data = load_thumbnail(extract_dir)
        fig_data = load_canvas_fig(extract_dir)

        total_user = sum(1 for m in conversation if m["role"] == "user")
        total_assistant = sum(
            1 for m in conversation if m["role"] == "assistant"
        )
        total_tool = sum(1 for m in conversation if m["role"] == "tool")

        databag = {
            "source_file": os.path.basename(make_path),
            "exported_at": meta["exported_at"],
            "design": {
                "name": meta["name"],
                "background_hex": meta["background_hex"],
                "background_color": meta["background_color"],
                "thumbnail_size": meta["thumbnail_size"],
                "canvas_size": meta["canvas_size"],
            },
            "conversation": conversation,
            "thumbnail_b64": _b64(thumb_data) if thumb_data else None,
            "canvas_fig_b64": _b64(fig_data) if fig_data else None,
            "images": [
                {
                    "filename": img["filename"],
                    "b64": _b64(img["data"]),
                    "size": img["size"],
                }
                for img in images
            ],
            "stats": {
                "total_messages": len(conversation),
                "user_messages": total_user,
                "assistant_iterations": total_assistant,
                "tool_calls": total_tool,
                "total_images": len(images),
            },
        }

        return databag

    except (ExtractError, ParseError, OSError) as e:
        raise AssembleError(str(e))
    finally:
        if extract_dir and os.path.isdir(extract_dir):
            import shutil
            shutil.rmtree(extract_dir, ignore_errors=True)
