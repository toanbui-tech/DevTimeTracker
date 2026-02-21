"""
sidebar.py — Sidebar navigation for TimeTracker v2
Fixed left panel with app branding, nav items, and running status.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient

from style import (
    BG_SIDEBAR, TEXT_SIDEBAR, TEXT_SIDEBAR_MUTED,
    ACCENT, ACCENT_GREEN, BORDER,
    FONT_DISPLAY, FONT_MONO, SIDEBAR_WIDTH,
    TEXT_MUTED
)
from tracker import TimeTracker, fmt_seconds


NAV_ITEMS = [
    ("timer",     "⏱",  "Timer"),
    ("dashboard", "◈",  "Dashboard"),
    ("history",   "☰",  "History"),
    ("projects",  "⊞",  "Projects"),
]


class Sidebar(QWidget):
    """
    Fixed-width dark sidebar with:
    - App logo/name at top
    - Navigation buttons
    - Running session status at bottom
    """

    nav_changed = pyqtSignal(str)   # emits page name

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._current = "timer"
        self._btn_map: dict[str, QPushButton] = {}

        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: none;")

        self._build_ui()

        # Update status every second
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._update_status)
        self._tick_timer.start(1000)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Logo area ──────────────────────────────────────────────────────────
        logo_area = QWidget()
        logo_area.setFixedHeight(72)
        logo_area.setStyleSheet(f"background: transparent;")
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(20, 0, 20, 0)

        # Icon
        icon = QLabel("⏱")
        icon.setStyleSheet(f"""
            font-size: 20px;
            background: {ACCENT}22;
            border-radius: 10px;
            padding: 6px 8px;
            color: {ACCENT};
            border: none;
        """)
        icon.setFixedSize(38, 38)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(icon)
        logo_layout.addSpacing(10)

        name = QLabel("TimeTracker")
        name.setStyleSheet(f"""
            color: {TEXT_SIDEBAR};
            font-size: 15px;
            font-weight: 700;
            font-family: {FONT_DISPLAY};
            border: none;
            background: transparent;
            letter-spacing: -0.3px;
        """)
        logo_layout.addWidget(name)
        logo_layout.addStretch()

        root.addWidget(logo_area)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: rgba(255,255,255,0.06); border: none;")
        root.addWidget(div)

        root.addSpacing(12)

        # ── Nav items ──────────────────────────────────────────────────────────
        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(10, 0, 10, 0)
        nav_layout.setSpacing(2)

        for key, icon_txt, label in NAV_ITEMS:
            btn = NavButton(icon_txt, label, active=(key == self._current))
            btn.clicked.connect(lambda checked=False, k=key: self._on_nav(k))
            self._btn_map[key] = btn
            nav_layout.addWidget(btn)

        root.addWidget(nav_container)
        root.addStretch()

        # ── Running session panel ──────────────────────────────────────────────
        self._status_panel = RunningStatusPanel(self.tracker)
        self._status_panel.setVisible(False)
        root.addWidget(self._status_panel)

        # ── Version / footer ───────────────────────────────────────────────────
        footer = QLabel("v2.0")
        footer.setStyleSheet(
            f"color: {TEXT_SIDEBAR_MUTED}; font-size: 10px; "
            f"padding: 12px 20px; border: none; background: transparent;"
        )
        root.addWidget(footer)

    def _on_nav(self, key: str):
        if key == self._current:
            return
        self._current = key
        for k, btn in self._btn_map.items():
            btn.set_active(k == key)
        self.nav_changed.emit(key)

    def _update_status(self):
        self._status_panel.setVisible(self.tracker.is_running)
        if self.tracker.is_running:
            self._status_panel.update_display()

    def set_page(self, key: str):
        self._on_nav(key)


class NavButton(QWidget):
    """Custom nav button with icon + label, active state styling."""

    clicked = pyqtSignal()

    def __init__(self, icon: str, label: str, active: bool = False, parent=None):
        super().__init__(parent)
        self._active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setFixedWidth(20)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_lbl)

        self._text_lbl = QLabel(label)
        layout.addWidget(self._text_lbl)
        layout.addStretch()

        self._refresh_style()

    def set_active(self, active: bool):
        self._active = active
        self._refresh_style()

    def _refresh_style(self):
        if self._active:
            bg = f"rgba(249,115,22,0.15)"
            text_color = ACCENT
            icon_color = ACCENT
            weight = "600"
            self.setStyleSheet(f"""
                QWidget {{
                    background: {bg};
                    border-radius: 8px;
                    border: none;
                }}
            """)
        else:
            text_color = TEXT_SIDEBAR_MUTED
            icon_color = TEXT_SIDEBAR_MUTED
            weight = "400"
            self.setStyleSheet("QWidget { background: transparent; border: none; }")

        self._icon_lbl.setStyleSheet(
            f"color: {icon_color}; font-size: 16px; border: none; background: transparent;"
        )
        self._text_lbl.setStyleSheet(
            f"color: {text_color}; font-size: 13px; font-weight: {weight}; "
            f"border: none; background: transparent;"
        )

    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)

    def enterEvent(self, e):
        if not self._active:
            self.setStyleSheet("""
                QWidget { background: rgba(255,255,255,0.06); border-radius: 8px; border: none; }
            """)
        super().enterEvent(e)

    def leaveEvent(self, e):
        if not self._active:
            self.setStyleSheet("QWidget { background: transparent; border: none; }")
        super().leaveEvent(e)


class RunningStatusPanel(QWidget):
    """Small panel at the bottom of sidebar showing the live running timer."""

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self.setStyleSheet(f"""
            QWidget {{
                background: rgba(249,115,22,0.12);
                border-top: 1px solid rgba(249,115,22,0.2);
                border-left: none;
                border-right: none;
                border-bottom: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        top = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 8px; border: none; background: transparent;")
        top.addWidget(dot)
        lbl = QLabel("RECORDING")
        lbl.setStyleSheet(
            f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: 600; "
            f"letter-spacing: 1px; border: none; background: transparent;"
        )
        top.addWidget(lbl)
        top.addStretch()
        layout.addLayout(top)

        self._project_lbl = QLabel("")
        self._project_lbl.setStyleSheet(
            f"color: {TEXT_SIDEBAR}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        layout.addWidget(self._project_lbl)

        self._time_lbl = QLabel("00:00:00")
        self._time_lbl.setStyleSheet(f"""
            color: {ACCENT};
            font-family: {FONT_MONO};
            font-size: 18px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        layout.addWidget(self._time_lbl)

    def update_display(self):
        pid = self.tracker.active_project_id
        name = ""
        if pid:
            for p in self.tracker.list_projects():
                if p["id"] == pid:
                    name = p["name"]
                    break
        self._project_lbl.setText(name)
        self._time_lbl.setText(fmt_seconds(self.tracker.elapsed_seconds()))