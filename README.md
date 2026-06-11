# make-converter — figma solution

Convierte archivos `.make` (exportación **Figma Make**) a 3 formatos de referencia: **HTML** (máxima usabilidad visual), **JSON** (integración programática), **Markdown** (base para maquetación con AI/LLMs).

## El Problema

Diseñé una interfaz en **Figma Make** y obtuve un archivo `.make`. Este formato es un ZIP que Figma guarda con el binario del diseño (`.fig`), metadatos y la conversación IA que lo generó, pero **no es legible directamente**. No podía compartir el diseño como referencia, ni pasárselo a una IA para que replicara la interfaz en código.

Necesitaba extraer toda esa información y transformarla en algo portable, legible y utilizable por herramientas como Google AI Studio, manteniendo la fidelidad del diseño original.

## La Solución

Esta app **descomprime, parsea y exporta** el `.make` en 3 formatos, cada uno con un propósito específico en el flujo de trabajo:

```
.make (ZIP Figma)
  ├──→ HTML   → Referencia visual auto-contenida (abre en navegador)
  ├──→ JSON   → Datos técnicos estructurados (integración)
  └──→ MD     → Especificación para AI (prompt maestro)
```

## ¿Qué es un archivo `.make`?

Es un **ZIP estándar** exportado por **Figma Make** — herramienta de Figma que genera diseños UI desde prompts conversacionales con IA.

```
archivo.make (ZIP)
├── canvas.fig        → binario Figma (.fig, diseño visual completo)
├── meta.json         → metadatos: colores, dimensiones, fecha
├── thumbnail.png     → previsualización del diseño
├── images/           → PNGs de assets incrustados
└── ai_chat.json      → conversación completa Figma AI (prompts + refinamientos)
```

## Los 3 Formatos de Exportación

| Formato | Tamaño | Propósito |
|---------|--------|-----------|
| **HTML** | ~400 KB | Archivo de **referencia visual** auto-contenido. Incluye conversación, miniatura, assets, y enlace de descarga del `.fig` original. Ábrelo en cualquier navegador. |
| **JSON** | ~366 KB | **Integración programática** con otras herramientas. DataBag completo con imágenes en base64 y estructura de datos cruda. |
| **Markdown** | ~11 KB | **Base para maquetación con AI**. Contiene la especificación completa del diseño extraída de la conversación, lista para usar como prompt maestro en Google AI Studio, ChatGPT, Claude, etc. |

### Markdown — Master Prompt para Replicación

El Markdown generado incluye:

- **Frontmatter** con metadatos del archivo fuente
- **Color Palette** extraída del `meta.json`
- **Original Design Prompt** — el prompt completo de Figma Make con todas las especificaciones UI/UX
- **Design Refinements** — las iteraciones del usuario que ajustaron el diseño
- **Technical Specifications** — dimensiones, colores, tipografía, componentes e interacciones extraídas del texto
- **Master Prompt Section** — bloque ready-to-paste para AI:

```
Eres un desarrollador senior experto en UI/UX.
Basándote en la siguiente especificación de diseño, genera el código completo
de la interfaz para una aplicación web en Go con templ/css.

[especificación completa del diseño]
```

> **Flujo recomendado:** Exporta `.md` → pégalo en Google AI Studio → obtén un prompt maestro detallado → replica el diseño en Go.

## Stack Tecnológico

| Capa | Tecnología | Razón |
|------|-----------|-------|
| Runtime | Python 3.12+ | Nativo en Linux Mint, sin runtime extra |
| UI | CustomTkinter 5.x | Tema oscuro moderno, widgets nativos |
| HTML gen | Jinja2 | Separación template/lógica |
| JSON gen | stdlib `json` | Zero dependencias |
| Markdown gen | stdlib `re` | Zero dependencias |
| Imágenes → base64 | stdlib `base64` | Incrustación en HTML/JSON |
| Packaging | PyInstaller → .AppImage | Single-file portable |
| Testing | pytest + `Oc.make` real | Tests con datos verdaderos |

**Dependencias:** solo `customtkinter` y `jinja2`.

## Instalación y Uso

### Desde Python (desarrollo)

```bash
cd make-converter
pip install -r requirements.txt

# GUI
python3 main.py

# CLI
python3 main.py ../Oc.make -f all -o ./output
```

### Desde el binario compilado

```bash
# CLI
./dist/make-converter ../Oc.make -f both -o ./output

# GUI (sin argumentos)
./dist/make-converter
```

### Opciones CLI

```
usage: make-converter [-h] [-o OUTPUT] [-f {html,json,md,both}] input

positional arguments:
  input                 Archivo .make de entrada

options:
  -h, --help            Muestra ayuda
  -o, --output OUTPUT   Directorio de salida (default: mismo que el input)
  -f, --format FORMAT   Formato: html, json, md, both (default: html)
```

### Ejemplos

```bash
# Exportar solo HTML (formato por defecto)
./make-converter diseno.make

# Exportar HTML + JSON + Markdown
./make-converter diseno.make -f both -o ./export

# Exportar solo Markdown (para Google AI Studio)
./make-converter diseno.make -f md -o ./prompts
```

### Packaging para Linux Mint

```bash
./build.sh                        # genera dist/make-converter
# Para .AppImage (requiere appimagetool):
appimagetool dist/make-converter dist/make-converter.AppImage
```

## Flujo de Trabajo Completo

```
1. Diseñas en Figma con Figma Make
         ↓
2. Exportas → archivo.make
         ↓
3. make-converter (./dist/make-converter diseno.make -f both -o ./output)
   ├── → HTML  (referencia visual, auto-contenido)
   ├── → JSON  (datos crudos, integración)
   └── → MD    (boceto + spec para AI, prompt master)
         ↓
4. Google AI Studio — prompt inicial con los 3 archivos:
   "Basado en el diseño adjunto (MD como especificación,
    HTML como referencia visual, JSON como datos técnicos),
    genera el código completo para mi app Go."
         ↓
5. Refinas con AI Studio → obtienes prompt maestro final
         ↓
6. Ese prompt maestro → tu agente/editor preferido
   → Implementación definitiva en Go con templ/css
```

## Uso con Google AI Studio (ejemplo real)

Este es el flujo que usé con el diseño **Open CenterSpace**:

### Paso 1 — Exportar los 3 formatos

```bash
./dist/make-converter Oc.make -f both -o ./output
# Genera: Oc.html, Oc.json, Oc.md
```

### Paso 2 — En Google AI Studio

```
Prompt inicial:

"Tengo un diseño de Figma Make convertido a 3 archivos:
- Oc.md (especificación principal del diseño)
- Oc.html (referencia visual auto-contenida)
- Oc.json (datos técnicos estructurados)

Usa Oc.md como guía principal de la interfaz,
Oc.html como referencia de cómo debe verse,
Oc.json para datos precisos de colores, dimensiones y assets.

Objetivo: Genera un prompt maestro detallado y preciso
que pueda usar en mi agente de código para implementar
esta interfaz en Go con templ/css.

El prompt debe incluir: paleta exacta, layout, componentes,
interacciones, y estructura de archivos del proyecto."
```

### Paso 3 — Resultado

AI Studio te devuelve un **prompte maestro refinado**. Ese prompt lo usas directamente con tu agente/editor favorito para la implementación final.

### Ejemplo de prompt agéntico final (post-AI Studio)

```markdown
Eres un desarrollador senior Go especializado en UI.
Implementa la interfaz "Open CenterSpace" con las siguientes
especificaciones verificadas:

Paleta: #050508 fondo, #0c0c14 paneles, #ff003c acento, #e8e8ed texto
Layout: Header 56px, Sidebar 320px, Chat 768px, Composer pill centrado
Componentes: glass cards con 1px border, botones pill-shaped, 
             terminal log, file tree, MCP panel, status indicators
Assets: imágenes embedidas, .fig descargable
Tech stack: Go + templ + CSS custom properties

Genera estructura de proyecto completa, componentes y estilos.
```

### Integración agéntica directa (CLI)

```bash
# Exportar spec para Claude/GPT/Gemini
./make-converter diseno.make -f both -o ./ai-prompts

# Copiar al clipboard (Linux)
cat ./ai-prompts/diseno.md | xclip -selection clipboard
```

## Arquitectura

```
┌─ Input ─────────────────────────┐
│  archivo.make (ZIP Figma Make)  │
└──────────┬──────────────────────┘
           ▼
┌─ Core Engine ────────────────────┐
│  extractor.py → valida + extrae  │
│  parser.py    → parsea JSONs     │
│  assembler.py → unifica datos    │
└──────────┬──────────────────────┘
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
┌─ HTML ───────┐  ┌─ JSON ──────┐  ┌─ MD ───────────┐
│  Auto-cont.  │  │  DataBag    │  │  Design Spec   │
│  + preview   │  │  + base64   │  │  + Master Prompt│
│  + .fig embed│  │  + crudo    │  │  + ready-to-paste│
└──────────────┘  └─────────────┘  └────────────────┘
```

## Estructura del Proyecto

```
make-converter/
├── main.py                     # Entry point: CLI + GUI
├── core/
│   ├── extractor.py            # Validación ZIP + extracción
│   ├── parser.py               # Parse meta.json, ai_chat.json
│   └── assembler.py            # Unifica en DataBag canónico
├── exporters/
│   ├── base.py                 # Abstract base exporter
│   ├── html_exporter.py        # Jinja2 template → HTML
│   ├── json_exporter.py        # json.dumps() → JSON
│   ├── md_exporter.py          # Spec extraction → Markdown
│   └── templates/
│       └── reference.html      # Template auto-contenido
├── ui/
│   ├── app.py                  # CustomTkinter main window
│   ├── components.py           # DropZone, FormatSelector, Preview
│   └── theme.py                # Estilo Open CenterSpace
├── tests/
│   ├── test_extractor.py
│   ├── test_parser.py
│   ├── test_html_exporter.py
│   └── test_json_exporter.py
├── requirements.txt
└── build.sh                    # PyInstaller → .AppImage
```

## Pipeline de Construcción

| Fase | Descripción |
|------|-------------|
| 0 | README + planificación |
| 1 | Core Engine: extractor, parser, assembler |
| 2 | Exporters: HTML + JSON |
| 3 | UI Desktop: CustomTkinter + componentes |
| 4 | Integración main.py + CLI |
| 5 | Tests con `Oc.make` real (27 tests) |
| 6 | Packaging .AppImage (18MB binary) |

## Casos Borde

- **No es ZIP** → error claro con sugerencia
- **ZIP corrupto** → error + re-exportar desde Figma
- **Sin ai_chat.json** → exporta metadata + thumbnail
- **Sin thumbnail.png** → placeholder generado
- **Sin images/** → sección gallery omitida

## Prioridades de Diseño

1. ✅ **Funcionalidad:** conversión correcta del `Oc.make` real
2. ✅ **Velocidad:** proceso completo < 2s
3. ✅ **Liviano:** app < 50MB instalada
4. ✅ **UI clara:** drag & drop, 3 clicks para exportar
5. ✅ **Auto-contenido:** HTML funcional sin internet
6. ✅ **Markdown para AI:** spec lista para Google AI Studio / ChatGPT
