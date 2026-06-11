import customtkinter as ctk
from ui.theme import CARD_BG, BORDER, TEXT, TEXT_MUTED, ACCENT, ACCENT_HOVER


class DropZone(ctk.CTkFrame):
    def __init__(self, master, on_file_drop=None, **kwargs):
        super().__init__(master, fg_color=CARD_BG, border_color=BORDER, border_width=1, corner_radius=16, **kwargs)
        self.on_file_drop = on_file_drop
        self._selected_path = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._label = ctk.CTkLabel(
            self,
            text="Arrastra tu archivo .make aquí\n o haz click para seleccionar",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=TEXT_MUTED,
            justify="center",
        )
        self._label.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.bind("<Button-1>", self._on_click)
        self._label.bind("<Button-1>", self._on_click)

    def _on_click(self, event=None):
        path = ctk.filedialog.askopenfilename(
            title="Seleccionar archivo .make",
            filetypes=[("Figma Make files", "*.make"), ("ZIP files", "*.zip"), ("Todos los archivos", "*.*")],
        )
        if path:
            self.set_file(path)

    def set_file(self, path: str):
        self._selected_path = path
        fname = path.split("/")[-1]
        self._label.configure(
            text=f"📄 {fname}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        )
        if self.on_file_drop:
            self.on_file_drop(path)

    def get_file(self) -> str | None:
        return self._selected_path

    def clear(self):
        self._selected_path = None
        self._label.configure(
            text="Arrastra tu archivo .make aquí\n o haz click para seleccionar",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=TEXT_MUTED,
        )


class FormatSelector(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(self, text="Formato de salida:", font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(anchor="w")

        self._format = ctk.StringVar(value="html")
        radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        radio_frame.pack(fill="x", pady=(6, 0))

        self._rb_html = ctk.CTkRadioButton(
            radio_frame, text="HTML (recomendado)", variable=self._format, value="html",
            font=ctk.CTkFont(size=13),
        )
        self._rb_html.pack(side="left", padx=(0, 16))

        self._rb_json = ctk.CTkRadioButton(
            radio_frame, text="JSON", variable=self._format, value="json",
            font=ctk.CTkFont(size=13),
        )
        self._rb_json.pack(side="left", padx=(0, 16))

        self._rb_md = ctk.CTkRadioButton(
            radio_frame, text="Markdown", variable=self._format, value="md",
            font=ctk.CTkFont(size=13),
        )
        self._rb_md.pack(side="left", padx=(0, 16))

        self._rb_both = ctk.CTkRadioButton(
            radio_frame, text="Todos", variable=self._format, value="both",
            font=ctk.CTkFont(size=13),
        )
        self._rb_both.pack(side="left")

    def get_format(self) -> str:
        return self._format.get()


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._label = ctk.CTkLabel(
            self, text="Listo", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
        )
        self._label.pack(side="left")

    def set(self, text: str, is_error: bool = False):
        self._label.configure(text=text, text_color="#ff003c" if is_error else TEXT_MUTED)
        self.after(5000, lambda: self._label.configure(text="Listo", text_color=TEXT_MUTED))
