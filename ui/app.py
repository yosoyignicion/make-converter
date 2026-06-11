import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui.theme import FROST_BG, CARD_BG, BORDER, TEXT, TEXT_MUTED, ACCENT
from ui.components import DropZone, FormatSelector, StatusBar
from core.assembler import assemble, AssembleError
from exporters.html_exporter import HTMLExporter
from exporters.json_exporter import JSONExporter
from exporters.md_exporter import MDExporter


APP_NAME = "make-converter — figma solution"
WINDOW_SIZE = "680x560"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(600, 480)
        self.configure(fg_color=FROST_BG)

        self._databag = None
        self._source_path = None

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=48)
        header.grid(row=0, column=0, padx=20, pady=(16, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="make-converter  ·  .make  →  HTML / JSON / MD",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        )
        title.pack(side="left")

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=0)
        content.grid_rowconfigure(1, weight=0)
        content.grid_rowconfigure(2, weight=0)
        content.grid_rowconfigure(3, weight=0)
        content.grid_rowconfigure(4, weight=1)

        # Drop zone
        self.dropzone = DropZone(content, on_file_drop=self._on_file_selected)
        self.dropzone.grid(row=0, column=0, sticky="ew", pady=(0, 12), ipady=20)

        # Info frame
        self.info_frame = ctk.CTkFrame(content, fg_color=CARD_BG, border_color=BORDER, border_width=1, corner_radius=12)
        self.info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_remove()

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=TEXT,
            justify="left",
        )
        self.info_label.grid(row=0, column=0, padx=16, pady=12, sticky="w")

        # Format selector
        self.format_selector = FormatSelector(content)
        self.format_selector.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # Export button
        self.export_btn = ctk.CTkButton(
            content,
            text="EXPORTAR",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            command=self._on_export,
            state="disabled",
        )
        self.export_btn.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        # Progress
        self.progress = ctk.CTkProgressBar(content, height=4, mode="indeterminate")
        self.progress.grid(row=4, column=0, sticky="ew", pady=(0, 0))
        self.progress.grid_remove()

        # Status bar
        self.status = StatusBar(self)
        self.status.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="ew")

    def _on_file_selected(self, path: str):
        self._source_path = path
        self._databag = None
        self.export_btn.configure(state="disabled")
        self.info_frame.grid_remove()

        self.status.set("Analizando archivo...")
        self.progress.grid()
        self.progress.start()
        self.update()

        def process():
            try:
                db = assemble(path)
                self._databag = db
                self.after(0, self._show_info, db)
            except AssembleError as e:
                self.after(0, self._show_error, str(e))

        threading.Thread(target=process, daemon=True).start()

    def _show_info(self, db: dict):
        self.progress.stop()
        self.progress.grid_remove()

        lines = [
            f"Diseño: {db['design']['name']}",
            f"Mensajes: {db['stats']['total_messages']}  ·  "
            f"Usuario: {db['stats']['user_messages']}  ·  "
            f"AI: {db['stats']['assistant_iterations']}  ·  "
            f"Tools: {db['stats']['tool_calls']}",
            f"Assets: {db['stats']['total_images']} imágenes  ·  "
            f"Lienzo: {db['design']['canvas_size']['width']}×{db['design']['canvas_size']['height']}px",
        ]
        self.info_label.configure(text="\n".join(lines))
        self.info_frame.grid()

        self.export_btn.configure(state="normal", text="EXPORTAR")
        self.status.set(f"✓ {db['stats']['total_messages']} mensajes cargados")

    def _show_error(self, msg: str):
        self.progress.stop()
        self.progress.grid_remove()
        self.status.set(msg, is_error=True)
        messagebox.showerror("Error", msg)

    def _on_export(self):
        if not self._databag:
            return

        fmt = self.format_selector.get_format()
        default_name = self._databag["design"]["name"] or "export"

        if fmt == "html":
            dir_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not dir_path:
                return
            output_path = os.path.join(dir_path, f"{default_name}.html")
            exporters = [HTMLExporter()]
        elif fmt == "json":
            dir_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not dir_path:
                return
            output_path = os.path.join(dir_path, f"{default_name}.json")
            exporters = [JSONExporter()]
        elif fmt == "md":
            dir_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not dir_path:
                return
            output_path = os.path.join(dir_path, f"{default_name}.md")
            exporters = [MDExporter()]
        else:
            dir_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not dir_path:
                return
            output_path = os.path.join(dir_path, f"{default_name}")
            exporters = [HTMLExporter(), JSONExporter(), MDExporter()]

        self.export_btn.configure(state="disabled", text="EXPORTANDO...")
        self.progress.grid()
        self.progress.start()
        self.status.set("Exportando...")
        self.update()

        def do_export():
            results = []
            errors = []
            for exporter in exporters:
                try:
                    if isinstance(exporter, HTMLExporter):
                        ext = ".html"
                    elif isinstance(exporter, JSONExporter):
                        ext = ".json"
                    else:
                        ext = ".md"
                    p = exporter.export(self._databag, output_path + ext)
                    results.append(p)
                except Exception as e:
                    errors.append(str(e))

            self.after(0, self._on_export_done, results, errors)

        threading.Thread(target=do_export, daemon=True).start()

    def _on_export_done(self, results: list[str], errors: list[str]):
        self.progress.stop()
        self.progress.grid_remove()
        self.export_btn.configure(state="normal", text="EXPORTAR")

        if errors:
            msg = "\n".join(errors)
            self.status.set("Error en exportación", is_error=True)
            messagebox.showerror("Error de exportación", msg)
        else:
            names = "\n".join(results)
            self.status.set(f"✓ Exportado: {', '.join(r.split('/')[-1] for r in results)}")
            messagebox.showinfo("Exportación completada", f"Archivos generados:\n{names}")
