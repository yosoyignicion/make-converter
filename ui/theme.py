import customtkinter as ctk


DARK_BG = "#050508"
FROST_BG = "#0c0c14"
CARD_BG = "#0a0a12"
BORDER = "#1a1a24"
TEXT = "#e8e8ed"
TEXT_MUTED = "#6a6a80"
ACCENT = "#ff003c"
ACCENT_HOVER = "#e00035"
GREEN = "#00e676"
SUCCESS_BG = "#0a1a0a"


def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = FROST_BG
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ACCENT
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = ACCENT_HOVER
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = "#ffffff"
    ctk.ThemeManager.theme["CTkButton"]["corner_radius"] = 24
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = CARD_BG
    ctk.ThemeManager.theme["CTkEntry"]["border_color"] = BORDER
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = TEXT
    ctk.ThemeManager.theme["CTkEntry"]["corner_radius"] = 12
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = TEXT
    ctk.ThemeManager.theme["CTkRadioButton"]["fg_color"] = ACCENT
    ctk.ThemeManager.theme["CTkRadioButton"]["hover_color"] = ACCENT_HOVER
    ctk.ThemeManager.theme["CTkProgressBar"]["fg_color"] = CARD_BG
    ctk.ThemeManager.theme["CTkProgressBar"]["progress_color"] = ACCENT
    ctk.ThemeManager.theme["CTkTextbox"]["fg_color"] = CARD_BG
    ctk.ThemeManager.theme["CTkTextbox"]["border_color"] = BORDER
    ctk.ThemeManager.theme["CTkTextbox"]["text_color"] = TEXT
