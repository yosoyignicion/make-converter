#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.theme import apply_theme
from ui.app import App


def cli():
    from core.assembler import assemble, AssembleError
    from exporters.html_exporter import HTMLExporter
    from exporters.json_exporter import JSONExporter
    from exporters.md_exporter import MDExporter
    import argparse

    parser = argparse.ArgumentParser(description="make-converter — figma solution: .make → HTML / JSON / MD")
    parser.add_argument("input", help="Archivo .make de entrada")
    parser.add_argument("-o", "--output", default=None, help="Directorio de salida (default: mismo que el input)")
    parser.add_argument("-f", "--format", choices=["html", "json", "md", "both"], default="html", help="Formato de exportación")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: archivo no encontrado: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output or os.path.dirname(os.path.abspath(input_path))
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    try:
        db = assemble(input_path)
    except AssembleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    exporters = []
    if args.format in ("html", "both"):
        exporters.append(HTMLExporter())
    if args.format in ("json", "both"):
        exporters.append(JSONExporter())
    if args.format in ("md", "both"):
        exporters.append(MDExporter())

    for exporter in exporters:
        ext = ".html" if isinstance(exporter, HTMLExporter) else ".json" if isinstance(exporter, JSONExporter) else ".md"
        out_path = os.path.join(output_dir, f"{base_name}{ext}")
        result = exporter.export(db, out_path)
        print(f"→ {result}")

    print("Hecho.")


def main():
    if len(sys.argv) > 1:
        cli()
    else:
        apply_theme()
        app = App()
        app.mainloop()


if __name__ == "__main__":
    main()
