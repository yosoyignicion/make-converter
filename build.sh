#!/usr/bin/env bash
set -euo pipefail

APP_NAME="make-converter"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"

echo "=== Empaquetando $APP_NAME ==="
echo ""

# Clean previous builds
rm -rf "$DIST_DIR" "$SCRIPT_DIR/build" "$SCRIPT_DIR"/*.spec

# Build with PyInstaller
echo "→ PyInstaller..."
pyinstaller \
    --onefile \
    --windowed \
    --name "$APP_NAME" \
    --add-data "$SCRIPT_DIR/exporters/templates:exporters/templates" \
    --hidden-import customtkinter \
    --hidden-import jinja2 \
    --distpath "$DIST_DIR" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    --noconfirm \
    "$SCRIPT_DIR/main.py" 2>&1 | tail -10

echo ""
echo "→ Verificando binario..."
if [ -f "$DIST_DIR/$APP_NAME" ]; then
    SIZE=$(du -h "$DIST_DIR/$APP_NAME" | cut -f1)
    FILE_TYPE=$(file "$DIST_DIR/$APP_NAME")
    echo "  Tamaño: $SIZE"
    echo "  Tipo: $FILE_TYPE"
    echo ""
    echo "✓ Build completado: $DIST_DIR/$APP_NAME"
    echo ""
    echo "Para convertir .AppImage (Linux Mint):"
    echo "  appimagetool $DIST_DIR/$APP_NAME $DIST_DIR/$APP_NAME.AppImage"
    echo ""
    echo "O ejecutar directamente:"
    echo "  $DIST_DIR/$APP_NAME <archivo.make> -f both"
else
    echo "✗ Error: no se generó el binario"
    exit 1
fi
