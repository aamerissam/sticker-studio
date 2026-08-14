# config.py
import os

SLOTS_PER_PAGE = 32
COLS = 8
ROWS = 4

PALETTES = {
    "male": {
        "bg": "#1F5EFF", "bg_dark": "#1447CC", "accent_hex": "#1447CC",
        "label": "Bleu", "gradient": ["#1F5EFF", "#1447CC"]
    },
    "female": {
        "bg": "#FF5FA2", "bg_dark": "#D94A8A", "accent_hex": "#D94A8A",
        "label": "Rose", "gradient": ["#FF5FA2", "#D94A8A"]
    }
}

PATTERNS = {
    "none":           {"label": "Aucun",       "icon": "◻"},
    "gradient":       {"label": "Degrade",     "icon": "◨"},
    "diagonal_lines": {"label": "Diagonales",  "icon": "▧"},
    "dots":           {"label": "Points",      "icon": "◉"},
    "hearts":         {"label": "Coeurs",      "icon": "♥"},
    "waves":          {"label": "Vagues",      "icon": "≋"},
    "crosshatch":     {"label": "Quadrillage", "icon": "▦"},
    "stars":          {"label": "Etoiles",     "icon": "✦"},
}

APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".karim_studio")
AUTOSAVE_PATH = os.path.join(APP_DATA_DIR, "autosave.json")
os.makedirs(APP_DATA_DIR, exist_ok=True)