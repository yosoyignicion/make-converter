import os
import json
import zipfile
import pytest


@pytest.fixture(scope="session")
def oc_make_path(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("fixture")
    path = os.path.join(tmp, "test_fixture.make")

    meta = {
        "client_meta": {
            "background_color": {"r": 0.05, "g": 0.05, "b": 0.05, "a": 1},
            "thumbnail_size": {"width": 400, "height": 300},
            "render_coordinates": {"x": 0, "y": 0, "width": 1440, "height": 900},
        },
        "file_name": "TestFixture",
        "exported_at": "2026-06-11T10:00:00Z",
    }

    chat = {
        "threads": [
            {
                "id": "fixture-thread",
                "messages": [
                    {
                        "index": 0,
                        "role": "user",
                        "createdAt": "2026-06-11T10:00:00Z",
                        "parts": [
                            {
                                "partType": "text",
                                "contentJson": json.dumps(
                                    {
                                        "text": "Create a dark themed UI with #0a0a0a background."
                                    }
                                ),
                            },
                            {
                                "partType": "code-chat-model-config-version",
                                "contentJson": json.dumps(
                                    {"modelConfigVersion": "test-model_0.0.0"}
                                ),
                            },
                        ],
                    },
                    {
                        "index": 1,
                        "role": "assistant",
                        "createdAt": "2026-06-11T10:01:00Z",
                        "parts": [
                            {
                                "partType": "text",
                                "contentJson": json.dumps(
                                    {"text": "Generated design with glassmorphism."}
                                ),
                            }
                        ],
                    },
                    {
                        "index": 2,
                        "role": "user",
                        "createdAt": "2026-06-11T10:02:00Z",
                        "parts": [
                            {
                                "partType": "text",
                                "contentJson": json.dumps(
                                    {"text": "Change accent to #ff0066."}
                                ),
                            }
                        ],
                    },
                    {
                        "index": 3,
                        "role": "assistant",
                        "createdAt": "2026-06-11T10:03:00Z",
                        "parts": [
                            {
                                "partType": "text",
                                "contentJson": json.dumps(
                                    {"text": "Accent updated to #ff0066."}
                                ),
                            }
                        ],
                    },
                ],
            }
        ]
    }

    extract_dir = os.path.join(tmp, "extract")
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(os.path.join(extract_dir, "images"), exist_ok=True)

    with open(os.path.join(extract_dir, "meta.json"), "w") as f:
        json.dump(meta, f)
    with open(os.path.join(extract_dir, "ai_chat.json"), "w") as f:
        json.dump(chat, f)
    with open(os.path.join(extract_dir, "canvas.fig"), "wb") as f:
        f.write(b"fig-binary-" + bytes(128))
    with open(os.path.join(extract_dir, "thumbnail.png"), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + bytes(128))
    with open(os.path.join(extract_dir, "images", "asset1.png"), "wb") as f:
        f.write(b"png-data-1" + bytes(64))
    with open(os.path.join(extract_dir, "images", "asset2.png"), "wb") as f:
        f.write(b"png-data-2" + bytes(128))

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(extract_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, extract_dir)
                zf.write(fpath, arcname)

    return str(path)


@pytest.fixture(scope="session")
def databag(oc_make_path):
    from core.assembler import assemble
    return assemble(oc_make_path)
