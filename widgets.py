"""
widgets.py — Reusable custom widgets for TimeTracker
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush

from style import (
    BG_CARD, BG_HOVER, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_OK, ACCENT_HOT, RADIUS, FONT_SIZE_SM, FONT_SIZE_XS,
    FONT_SIZE_LG, FONT_SIZE_MD, FONT_MONO
)
from tracker import fmt_seconds


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: {RADIUS}px;
            }}
        """)


class StatBox(QWidget):
    def __init__(self, label: str, value: str = "00:00:00", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self._label = QLabel(label.upper())
        self._label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_XS}px; "
            f"font-weight: 600; letter-spacing: 1px;"
        )
        self._value = QLabel(value)
        self._value.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-family: {FONT_MONO}; "
            f"font-size: {FONT_SIZE_LG}px; font-weight: 700;"
        )
        layout.addWidget(self._label)
        layout.addWidget(self._value)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: {RADIUS}px;
            }}
        """)

    def set_value(self, seconds: int) -> None:
        self._value.setText(fmt_seconds(seconds))

    def set_raw(self, text: str) -> None:
        self._value.setText(text)


class ColorDot(QWidget):
    def __init__(self, color: str = ACCENT, size: int = 10, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._size = size
        self.setFixedSize(size, size)

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self._size, self._size)


class LiveIndicator(QWidget):
    """Pulsing dot shown while a timer is running."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self._opacity = 1.0
        self._growing = False
        self._pulse = QTimer(self)
        self._pulse.timeout.connect(self._tick)
        self._pulse.start(60)

    def _tick(self):
        step = 0.04
        if self._growing:
            self._opacity = min(1.0, self._opacity + step)
            if self._opacity >= 1.0:
                self._growing = False
        else:
            self._opacity = max(0.3, self._opacity - step)
            if self._opacity <= 0.3:
                self._growing = True
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(ACCENT_OK)
        color.setAlphaF(self._opacity)
        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, 10, 10)


class ProjectListItem(QWidget):
    """
    One row in the project list.
    Shows: dot | name | live indicator | total time | action buttons (on hover)
    """

    start_requested  = pyqtSignal(int)
    rename_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, project_id: int, name: str, color: str,
                 total_seconds: int = 0, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self._is_active = is_active

        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 8, 0)
        row.setSpacing(12)

        self.dot = ColorDot(color, size=10)
        row.addWidget(self.dot)

        self.name_label = QLabel(name)
        self._refresh_name_style(is_active)
        row.addWidget(self.name_label, 1)

        self.live_dot = LiveIndicator()
        self.live_dot.setVisible(is_active)
        row.addWidget(self.live_dot)

        self.time_label = QLabel(fmt_seconds(total_seconds))
        self.time_label.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: {FONT_SIZE_SM}px; "
            f"color: {TEXT_SECONDARY}; min-width: 72px;"
        )
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self.time_label)

        self._btn_start  = self._make_action_btn("▶", "Start timer")
        self._btn_rename = self._make_action_btn("✎", "Rename")
        self._btn_delete = self._make_action_btn("✕", "Delete")
        self._btn_delete.setStyleSheet(f"color: {ACCENT_HOT}66; background: transparent; border: none; padding: 4px 6px; border-radius: 4px;")

        self._btn_start.clicked.connect(lambda: self.start_requested.emit(self.project_id))
        self._btn_rename.clicked.connect(lambda: self.rename_requested.emit(self.project_id))
        self._btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.project_id))

        for btn in (self._btn_start, self._btn_rename, self._btn_delete):
            btn.setVisible(False)
            row.addWidget(btn)

        self._update_bg(False)

    def _make_action_btn(self, text: str, tip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("btn_icon")
        btn.setToolTip(tip)
        btn.setFixedSize(28, 28)
        return btn

    def _refresh_name_style(self, active: bool):
        color = ACCENT if active else TEXT_PRIMARY
        weight = "600" if active else "400"
        self.name_label.setStyleSheet(
            f"font-size: {FONT_SIZE_MD}px; font-weight: {weight}; color: {color};"
        )

    def _update_bg(self, hovered: bool):
        bg = BG_HOVER if hovered else "transparent"
        self.setStyleSheet(f"QWidget {{ background-color: {bg}; border-radius: 6px; }}")

    def enterEvent(self, e):
        self._update_bg(True)
        for btn in (self._btn_start, self._btn_rename, self._btn_delete):
            btn.setVisible(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._update_bg(False)
        for btn in (self._btn_start, self._btn_rename, self._btn_delete):
            btn.setVisible(False)
        super().leaveEvent(e)

    def update_time(self, seconds: int) -> None:
        self.time_label.setText(fmt_seconds(seconds))

    def set_active(self, active: bool) -> None:
        self._is_active = active
        self.live_dot.setVisible(active)
        self._refresh_name_style(active)


class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER}; border: none;")