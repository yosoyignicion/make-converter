# make-converter — AGENTS.md

## Commands

```bash
pip install -r requirements.txt   # deps: customtkinter, jinja2
python3 main.py                   # GUI mode (no args)
python3 main.py file.make -f both -o ./out   # CLI mode (args present)
python3 -m pytest                 # 27 tests, session-scoped synthetic fixture
python3 -m pytest -v              # verbose
./build.sh                        # PyInstaller → dist/make-converter
```

## Architecture

- `main.py` entrypoint: CLI if `len(sys.argv) > 1` else GUI (CustomTkinter).
  Uses `sys.path.insert(0, ...)` so run from any dir.
- **Core pipeline**: `extractor.py` (ZIP validation + extraction → temp dir) → `parser.py` (meta.json, ai_chat.json) → `assembler.py` (unifies into DataBag dict with base64-encoded binaries). Temp dir is cleaned up after assembly.
- **Exporters**: `BaseExporter` ABC with `export(databag, output_path) → str`. Each auto-appends its extension (`.html`, `.json`, `.md`).
- **HTML** uses Jinja2 template at `exporters/templates/reference.html`.
- **Markdown** (`MDExporter`) extracts spec via regex from first user message — no AI involved.
- **DataBag** is a plain dict passed through — no Pydantic/Zod schemas, no dataclasses.

## Tests

- `conftest.py` generates a synthetic `.make` ZIP (no real Figma file needed). Session-scoped `databag` fixture.
- Test files use class-based `setup_method`/`teardown_method` (not pytest fixtures) for clean-up.
- Run from project root. No type checker or linter configured.

## Build

- `build.sh` runs `pyinstaller --onefile --windowed`. The `--windowed` flag is harmless for CLI usage.
- `--add-data` bundles `exporters/templates/` for PyInstaller. HTML exporter resolves the template at runtime via `Path(__file__).parent / "templates"`.
- Artifacts go to `dist/`.

## Edge cases handled by core

- Non-ZIP input → `ExtractError("Solo archivos .make")`
- Corrupt ZIP → `ExtractError("ZIP corrupto")`
- Missing meta.json / ai_chat.json / canvas.fig → `ExtractError("Estructura .make incompleta")`
- Missing ai_chat.json → `ParseError`
- Missing thumbnail.png → `None` (HTML template handles gracefully)
- Missing images/ → empty list
