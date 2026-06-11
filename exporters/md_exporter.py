import os
import json
import re
from exporters.base import BaseExporter


class MDExporter(BaseExporter):
    def export(self, databag: dict, output_path: str) -> str:
        path = output_path
        if not path.endswith(".md"):
            path += ".md"

        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)

        md = self._build(databag)

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        return path

    def _build(self, db: dict) -> str:
        lines = []
        design = db["design"]
        stats = db["stats"]
        conv = db["conversation"]

        # --- Frontmatter ---
        lines.append("---")
        lines.append(f'source: "{db["source_file"]}"')
        lines.append(f'exported_at: "{db["exported_at"]}"')
        lines.append(f'design_name: "{design["name"]}"')
        lines.append(f'background: "{design["background_hex"]}"')
        lines.append(f'canvas: "{design["canvas_size"]["width"]}x{design["canvas_size"]["height"]}"')
        lines.append("---")
        lines.append("")

        # --- Title ---
        lines.append(f"# {design['name']} — Design Specification")
        lines.append("")
        lines.append(f"> Exported from `{db['source_file']}` at {db['exported_at'][:10]}")
        lines.append("")

        # --- Stats ---
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Messages:** {stats['total_messages']} ({stats['user_messages']} user, {stats['assistant_iterations']} AI, {stats['tool_calls']} tool)")
        lines.append(f"- **Canvas:** {design['canvas_size']['width']}×{design['canvas_size']['height']}px")
        lines.append(f"- **Background:** {design['background_hex']}")
        lines.append(f"- **Assets:** {stats['total_images']} images")
        lines.append("")

        # --- Color Palette ---
        bg = design.get("background_color", {})
        lines.append("## Color Palette")
        lines.append("")
        lines.append("| Token | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| Background | `{design['background_hex']}` |")
        if bg:
            lines.append(f"| Background RGB | `rgba({bg.get('r',0)*255:.0f}, {bg.get('g',0)*255:.0f}, {bg.get('b',0)*255:.0f}, {bg.get('a',1)})` |")
        lines.append("")

        # --- Design Spec from first user message ---
        lines.append("## Original Design Prompt")
        lines.append("")
        lines.append("The following is the complete design specification extracted from the Figma Make conversation:")
        lines.append("")

        first_user = next((m for m in conv if m["role"] == "user" and m["text"]), None)
        if first_user:
            text = first_user["text"]
            lines.append(text)
            lines.append("")

        # --- Refinements ---
        refinements = [m for m in conv if m["role"] == "user" and m != first_user and m["text"]]
        if refinements:
            lines.append("## Design Refinements")
            lines.append("")
            for ref in refinements:
                ts = ref["timestamp"][:19] if ref["timestamp"] else "unknown"
                lines.append(f"### Iteration @ {ts}")
                lines.append("")
                lines.append(ref["text"])
                lines.append("")

        # --- Technical Specs Extraction ---
        lines.append("## Technical Specifications")
        lines.append("")

        if first_user:
            spec_text = first_user["text"]
            specs = self._extract_specs(spec_text)
            for section, items in specs.items():
                if items:
                    lines.append(f"### {section}")
                    lines.append("")
                    for item in items:
                        lines.append(f"- {item}")
                    lines.append("")

        # --- Model Info ---
        models = set()
        for m in conv:
            if m.get("model"):
                models.add(m["model"])
        if models:
            lines.append("## AI Model")
            lines.append("")
            for model in sorted(models):
                lines.append(f"- **{model}**")
            lines.append("")

        # --- Stats breakdown ---
        lines.append("## Conversation Stats")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total messages | {stats['total_messages']} |")
        lines.append(f"| User messages | {stats['user_messages']} |")
        lines.append(f"| AI iterations | {stats['assistant_iterations']} |")
        lines.append(f"| Tool calls | {stats['tool_calls']} |")
        lines.append(f"| Image assets | {stats['total_images']} |")
        lines.append("")

        # --- Master Prompt Section ---
        lines.append("## Master Prompt para Replicación")
        lines.append("")
        lines.append("```markdown")
        lines.append("Eres un desarrollador senior experto en UI/UX.")
        lines.append("")
        lines.append("Basándote en la siguiente especificación de diseño, genera el código completo")
        lines.append("de la interfaz para una aplicación web en Go con templ/css.")
        lines.append("")

        if first_user:
            text = first_user["text"]
            shortened = text[:3000]
            lines.append(shortened)
            lines.append("")

        for ref in refinements:
            lines.append(ref["text"])
            lines.append("")

        lines.append("```")
        lines.append("")

        lines.append("---")
        lines.append(f"*Generated by make-converter (figma solution) — {db['exported_at'][:10]}*")
        lines.append("")

        return "\n".join(lines)

    def _extract_specs(self, text: str) -> dict:
        specs = {
            "Layout & Dimensions": [],
            "Colors": [],
            "Typography": [],
            "Components": [],
            "Interactions": [],
        }

        # Layout patterns
        layout_patterns = [
            (r"(\d+px\s+(?:Top\s+)?Header)", "Layout & Dimensions"),
            (r"(\d+px\s+(?:Left\s+)?(?:sidebar|Sidebar))", "Layout & Dimensions"),
            (r"(\d+px\s+wide)", "Layout & Dimensions"),
            (r"(centered\s+\w+)", "Layout & Dimensions"),
            (r"(margin[a-z\s:]+)", "Layout & Dimensions"),
        ]

        color_patterns = [
            (r"(#[0-9a-fA-F]{6})\b", "Colors"),
            (r"(rgba?\([^)]+\))", "Colors"),
            (r"(neon\s+\w+)", "Colors"),
            (r"(deep\s+\w+)", "Colors"),
            (r"(dark\s+\w+)", "Colors"),
        ]

        component_patterns = [
            (r"(\d+\.\s*[A-Z][^.]+)", "Components"),
            (r"(pill[-\s]*(?:shaped|button)?)", "Components"),
            (r"(glass[a-z\s]*)", "Components"),
            (r"(composer)", "Components"),
        ]

        for pattern, category in layout_patterns + color_patterns + component_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val = match.group(1).strip()
                if val and val not in specs[category]:
                    specs[category].append(val)

        return specs
