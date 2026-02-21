"""
style.py — Warm Modern Light Theme for TimeTracker v2
Design direction: "Warm Productivity" — clean light background,
amber/coral accents, generous whitespace, soft shadows.
"""

# ── Palette ────────────────────────────────────────────────────────────────────
BG_BASE     = "#F7F5F2"   # warm off-white background
BG_SURFACE  = "#FFFFFF"   # card / panel surfaces
BG_SIDEBAR  = "#1C1917"   # deep warm dark sidebar
BG_HOVER    = "#F0EDE8"   # hover state on light surfaces
BG_INPUT    = "#F0EDE8"   # input backgrounds

BORDER      = "#E8E3DC"   # subtle warm border
BORDER_MED  = "#D4CCC2"   # medium border

TEXT_PRIMARY   = "#1C1917"   # near-black warm
TEXT_SECONDARY = "#78716C"   # warm gray
TEXT_MUTED     = "#A8A29E"   # muted warm gray
TEXT_SIDEBAR   = "#E7E5E4"   # sidebar text
TEXT_SIDEBAR_MUTED = "#78716C"

ACCENT        = "#F97316"   # vibrant orange
ACCENT_LIGHT  = "#FFF7ED"   # orange tint bg
ACCENT_DARK   = "#EA580C"   # darker orange for hover
ACCENT_GREEN  = "#22C55E"   # success / running
ACCENT_GREEN_LIGHT = "#F0FDF4"
ACCENT_RED    = "#EF4444"   # stop / danger
ACCENT_RED_LIGHT = "#FEF2F2"
ACCENT_BLUE   = "#3B82F6"   # info / secondary
ACCENT_BLUE_LIGHT = "#EFF6FF"
ACCENT_PURPLE = "#A855F7"

PROJECT_COLORS = [
    "#F97316", "#22C55E", "#3B82F6", "#A855F7",
    "#EF4444", "#06B6D4", "#EAB308", "#EC4899",
    "#14B8A6", "#8B5CF6",
]

FONT_FAMILY  = "\"DM Sans\", \"Outfit\", \"Nunito\", \"Segoe UI\", sans-serif"
FONT_MONO    = "\"DM Mono\", \"Fira Code\", \"Consolas\", monospace"
FONT_DISPLAY = "\"Sora\", \"Outfit\", \"DM Sans\", sans-serif"

RADIUS_SM = 8
RADIUS    = 12
RADIUS_LG = 16
RADIUS_XL = 24

SHADOW_SM = "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)"
SHADOW_MD = "0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04)"
SHADOW_LG = "0 8px 32px rgba(0,0,0,0.10), 0 4px 12px rgba(0,0,0,0.05)"

SIDEBAR_WIDTH = 220

APP_STYLE = f"""
/* ── Reset & Base ─────────────────────────────────────────────────── */
* {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    outline: none;
    border: none;
}}

QMainWindow, QWidget {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
}}

QDialog {{
    background-color: {BG_SURFACE};
    border-radius: {RADIUS}px;
}}

/* ── Scrollbars ───────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 4px 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_MED};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

/* ── Buttons ──────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {BORDER_MED};
    color: {TEXT_PRIMARY};
}}
QPushButton:pressed {{ background-color: {BORDER}; }}

QPushButton#btn_primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT_DARK});
    color: white;
    border: none;
    font-weight: 600;
    font-size: 13px;
    padding: 10px 28px;
    border-radius: {RADIUS_SM}px;
}}
QPushButton#btn_primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_DARK}, stop:1 #C2410C);
}}
QPushButton#btn_primary:pressed {{
    background: #C2410C;
}}

QPushButton#btn_stop {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_RED}, stop:1 #DC2626);
    color: white;
    border: none;
    font-weight: 600;
    font-size: 13px;
    padding: 10px 28px;
    border-radius: {RADIUS_SM}px;
}}
QPushButton#btn_stop:hover {{ background: #DC2626; }}

QPushButton#btn_ghost {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 12px;
}}
QPushButton#btn_ghost:hover {{
    background: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton#btn_icon {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    padding: 4px;
    border-radius: 6px;
    min-width: 24px;
    min-height: 24px;
}}
QPushButton#btn_icon:hover {{
    background: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton#btn_danger {{
    color: {ACCENT_RED};
    border: 1.5px solid transparent;
    background: transparent;
}}
QPushButton#btn_danger:hover {{
    background: {ACCENT_RED_LIGHT};
    border-color: {ACCENT_RED}44;
}}

QPushButton#btn_sidebar {{
    background: transparent;
    border: none;
    color: {TEXT_SIDEBAR_MUTED};
    border-radius: {RADIUS_SM}px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}}
QPushButton#btn_sidebar:hover {{
    background: rgba(255,255,255,0.08);
    color: {TEXT_SIDEBAR};
}}
QPushButton#btn_sidebar_active {{
    background: rgba(249,115,22,0.18);
    border: none;
    color: {ACCENT};
    border-radius: {RADIUS_SM}px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

/* ── Inputs ───────────────────────────────────────────────────────── */
QLineEdit {{
    background: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 9px 13px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: {ACCENT}33;
}}
QLineEdit:focus {{
    border-color: {ACCENT};
    background: {BG_SURFACE};
}}

QComboBox {{
    background: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 13px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    min-width: 140px;
}}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ image: none; border: none; }}
QComboBox QAbstractItemView {{
    background: {BG_SURFACE};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 4px;
    selection-background-color: {ACCENT_LIGHT};
    selection-color: {ACCENT_DARK};
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 6px;
}}

QDateEdit {{
    background: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 13px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QDateEdit:focus {{ border-color: {ACCENT}; }}
QDateEdit::drop-down {{ border: none; width: 20px; }}
QCalendarWidget {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}

/* ── Labels ───────────────────────────────────────────────────────── */
QLabel#label_timer {{
    font-family: {FONT_MONO};
    font-size: 48px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    letter-spacing: -1px;
}}
QLabel#label_heading {{
    font-size: 20px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    font-family: {FONT_DISPLAY};
}}
QLabel#label_subheading {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}
QLabel#label_caption {{
    font-size: 11px;
    font-weight: 600;
    color: {TEXT_MUTED};
    letter-spacing: 0.8px;
}}

/* ── Table ────────────────────────────────────────────────────────── */
QTableWidget {{
    background: {BG_SURFACE};
    gridline-color: {BORDER};
    border: none;
    border-radius: {RADIUS}px;
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 12px 14px;
    border-bottom: 1px solid {BG_BASE};
    color: {TEXT_PRIMARY};
}}
QTableWidget::item:selected {{
    background: {ACCENT_LIGHT};
    color: {ACCENT_DARK};
}}
QHeaderView::section {{
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
    padding: 12px 14px;
    border: none;
    border-bottom: 1.5px solid {BORDER};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
}}
QHeaderView {{ background: transparent; }}

/* ── Scroll Area ──────────────────────────────────────────────────── */
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* ── Tooltip ──────────────────────────────────────────────────────── */
QToolTip {{
    background: {TEXT_PRIMARY};
    color: {BG_SURFACE};
    border: none;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
}}

/* ── Message / Input Dialogs ──────────────────────────────────────── */
QMessageBox {{ background: {BG_SURFACE}; }}
QMessageBox QLabel {{ color: {TEXT_PRIMARY}; font-size: 13px; }}
QMessageBox QPushButton {{ min-width: 90px; }}
QInputDialog {{ background: {BG_SURFACE}; }}
QInputDialog QLabel {{ color: {TEXT_PRIMARY}; }}

/* ── Separator ────────────────────────────────────────────────────── */
QFrame[frameShape="4"] {{
    background: {BORDER};
    border: none;
    max-height: 1px;
}}
"""