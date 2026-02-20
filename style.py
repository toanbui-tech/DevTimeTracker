"""
style.py — Design tokens and Qt stylesheet for TimeTracker.
Edit this file to retheme the entire app.
"""

BG_DARK   = "#0F1117"
BG_CARD   = "#1A1D27"
BG_HOVER  = "#22263A"
BG_INPUT  = "#13161E"

BORDER       = "#2A2D3E"
BORDER_FOCUS = "#4A9EFF"

TEXT_PRIMARY   = "#E8EAF0"
TEXT_SECONDARY = "#7B8099"
TEXT_MUTED     = "#4A4E66"

ACCENT      = "#4A9EFF"
ACCENT_HOT  = "#FF5C5C"
ACCENT_OK   = "#3DD68C"
ACCENT_WARN = "#FFB74D"

PROJECT_COLORS = [
    "#4A9EFF", "#3DD68C", "#FF7043", "#AB47BC",
    "#FFB74D", "#26C6DA", "#EF5350", "#66BB6A",
    "#FFA726", "#42A5F5",
]

FONT_FAMILY = "Segoe UI, SF Pro Display, Helvetica Neue, Arial"
FONT_MONO   = "Consolas, SF Mono, Menlo, monospace"

FONT_SIZE_XS  = 10
FONT_SIZE_SM  = 12
FONT_SIZE_MD  = 14
FONT_SIZE_LG  = 18
FONT_SIZE_XL  = 24
FONT_SIZE_2XL = 36

RADIUS    = 8
RADIUS_SM = 5

APP_STYLE = f"""
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_MD}px;
    border: none;
    outline: none;
}}
QMainWindow, QDialog {{
    background-color: {BG_DARK};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Buttons */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 8px 18px;
    font-size: {FONT_SIZE_SM}px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {TEXT_MUTED};
}}
QPushButton:pressed {{ background-color: {BORDER}; }}

QPushButton#btn_primary {{
    background-color: {ACCENT};
    color: white;
    border: none;
    font-weight: 600;
    font-size: {FONT_SIZE_MD}px;
    padding: 12px 32px;
    border-radius: {RADIUS}px;
}}
QPushButton#btn_primary:hover {{ background-color: #6AB4FF; }}
QPushButton#btn_primary:pressed {{ background-color: #2A7EDF; }}

QPushButton#btn_stop {{
    background-color: {ACCENT_HOT};
    color: white;
    border: none;
    font-weight: 600;
    font-size: {FONT_SIZE_MD}px;
    padding: 12px 32px;
    border-radius: {RADIUS}px;
}}
QPushButton#btn_stop:hover {{ background-color: #FF7676; }}

QPushButton#btn_danger {{
    color: {ACCENT_HOT};
    border-color: {ACCENT_HOT}44;
}}
QPushButton#btn_danger:hover {{
    background-color: {ACCENT_HOT}22;
    border-color: {ACCENT_HOT};
}}

QPushButton#btn_icon {{
    background: transparent;
    border: none;
    padding: 4px 6px;
    color: {TEXT_MUTED};
    border-radius: 4px;
}}
QPushButton#btn_icon:hover {{ color: {TEXT_PRIMARY}; background: {BG_HOVER}; }}

/* Inputs */
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: {FONT_SIZE_MD}px;
}}
QLineEdit:focus {{ border-color: {BORDER_FOCUS}; }}

QComboBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{ image: none; }}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT}44;
}}

QDateEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
}}
QDateEdit::drop-down {{ border: none; width: 20px; }}
QCalendarWidget {{ background-color: {BG_CARD}; color: {TEXT_PRIMARY}; }}

/* Labels */
QLabel#label_timer {{
    font-family: {FONT_MONO};
    font-size: {FONT_SIZE_2XL}px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    letter-spacing: 2px;
}}
QLabel#label_heading {{
    font-size: {FONT_SIZE_LG}px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

/* Tabs */
QTabBar {{
    background: {BG_DARK};
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 12px 24px;
    font-size: {FONT_SIZE_SM}px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{ color: {TEXT_SECONDARY}; }}
QTabWidget::pane {{
    border: none;
    border-top: 1px solid {BORDER};
}}

/* Table */
QTableWidget {{
    background-color: {BG_DARK};
    gridline-color: {BORDER};
    border: none;
    font-size: {FONT_SIZE_SM}px;
}}
QTableWidget::item {{
    padding: 10px 12px;
    border-bottom: 1px solid {BORDER};
}}
QTableWidget::item:selected {{
    background-color: {ACCENT}22;
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: {BG_DARK};
    color: {TEXT_MUTED};
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-size: {FONT_SIZE_XS}px;
    font-weight: 600;
    letter-spacing: 1px;
}}

/* Scroll area */
QScrollArea {{ border: none; }}

/* Tooltip */
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 4px 8px;
    border-radius: 4px;
}}

/* Message box */
QMessageBox {{ background-color: {BG_CARD}; }}
QMessageBox QPushButton {{ min-width: 80px; }}
"""