"""
widgets.py — Custom widgets for TimeTracker v2
Modern light theme with smooth animations and rich visuals.
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, pyqtProperty, QPointF
)
from PyQt6.QtGui import (
    QColor, QPainter, QBrush, QPen, QLinearGradient,
    QFont, QPainterPath, QRadialGradient
)

from style import (
    BG_SURFACE, BG_HOVER, BG_BASE, BORDER, BORDER_MED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_LIGHT, ACCENT_DARK, ACCENT_GREEN,
    ACCENT_RED, ACCENT_BLUE, FONT_MONO, FONT_DISPLAY,
    RADIUS, RADIUS_SM, PROJECT_COLORS
)
from tracker import fmt_seconds


def add_shadow(widget, blur=16, offset=(0, 2), color=(0, 0, 0, 18)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(*offset)
    shadow.setColor(QColor(*color))
    widget.setGraphicsEffect(shadow)


class Card(QFrame):
    """Rounded white card with subtle shadow."""

    def __init__(self, parent=None, padding=20):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SURFACE};
                border-radius: {RADIUS}px;
                border: 1px solid {BORDER};
            }}
        """)
        add_shadow(self)


class StatCard(QWidget):
    """
    Dashboard stat card: icon  label  big value  sub-label
    With a colored left accent bar.
    """

    def __init__(self, label: str, icon: str = "⏱",
                 color: str = ACCENT, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._value_secs = 0

        self.setMinimumHeight(100)
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_SURFACE};
                border-radius: {RADIUS}px;
                border: 1px solid {BORDER};
            }}
        """)
        add_shadow(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 18px;
            background: {color}18;
            border-radius: 8px;
            padding: 5px 7px;
            border: none;
        """)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(icon_lbl)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600; "
            f"letter-spacing: 1px; border: none; background: transparent;"
        )
        top.addWidget(lbl)
        top.addStretch()
        layout.addLayout(top)

        self._value_label = QLabel("00:00:00")
        self._value_label.setStyleSheet(f"""
            font-family: {FONT_MONO};
            font-size: 24px;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            border: none;
            background: transparent;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(self._value_label)

    def set_value(self, seconds: int) -> None:
        self._value_secs = seconds
        self._value_label.setText(fmt_seconds(seconds))

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 16, 4, self.height() - 32, 2, 2)


class TimerRing(QWidget):
    """
    Circular progress ring that fills based on elapsed time vs a daily goal.
    Shows the timer value in the center.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self._progress = 0.0      # 0.0 – 1.0
        self._color = QColor(ACCENT)
        self._bg_color = QColor(BORDER)
        self._text = "00:00:00"
        self._sub = ""
        self._running = False

        # Subtle pulse animation when running
        self._pulse_size = 0.0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_tick)

    def set_running(self, running: bool):
        self._running = running
        if running:
            self._pulse_timer.start(50)
        else:
            self._pulse_timer.stop()
            self._pulse_size = 0.0
            self.update()

    def _pulse_tick(self):
        import math, time
        t = time.time()
        self._pulse_size = (math.sin(t * 2.5) + 1) / 2  # 0.0–1.0
        self.update()

    def set_value(self, seconds: int, project_color: str = None):
        self._text = fmt_seconds(seconds)
        if project_color:
            self._color = QColor(project_color)
        # Progress: fill ring over 8-hour day goal
        self._progress = min(1.0, seconds / (8 * 3600))
        self.update()

    def set_idle(self):
        self._text = "00:00:00"
        self._sub = ""
        self._progress = 0.0
        self.update()

    def set_sub(self, text: str):
        self._sub = text
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        ring_w = 14
        r = min(w, h) / 2 - ring_w - 8

        # Pulse glow when running
        if self._running and self._pulse_size > 0:
            glow = QRadialGradient(cx, cy, r + ring_w + 20)
            c = QColor(self._color)
            c.setAlphaF(0.10 * self._pulse_size)
            glow.setColorAt(0, c)
            c2 = QColor(self._color)
            c2.setAlphaF(0)
            glow.setColorAt(1, c2)
            p.setBrush(QBrush(glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), r + ring_w + 20, r + ring_w + 20)

        # Background ring
        p.setPen(QPen(QColor(BORDER), ring_w, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        from PyQt6.QtCore import QRectF
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        p.drawEllipse(rect)

        # Progress arc
        if self._progress > 0:
            grad_pen_color = self._color
            pen = QPen(grad_pen_color, ring_w, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            span = int(-self._progress * 360 * 16)
            p.drawArc(rect, 90 * 16, span)

        # Center text — timer
        p.setPen(QColor(TEXT_PRIMARY))
        font = QFont("DM Mono, Consolas")
        font.setPixelSize(28)
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(
            QRectF(cx - r, cy - 22, r * 2, 36),
            Qt.AlignmentFlag.AlignCenter, self._text
        )

        # Sub-text — project name
        if self._sub:
            p.setPen(QColor(TEXT_MUTED))
            font2 = QFont("DM Sans, Segoe UI")
            font2.setPixelSize(12)
            p.setFont(font2)
            p.drawText(
                QRectF(cx - r, cy + 14, r * 2, 20),
                Qt.AlignmentFlag.AlignCenter, self._sub
            )


class ProjectRow(QWidget):
    """
    Animated project list row with smooth hover reveal of actions.
    """

    start_requested  = pyqtSignal(int)
    rename_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, project_id: int, name: str, color: str,
                 total_seconds: int = 0, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self._color = color
        self._is_active = is_active

        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(12)

        # Color pill
        self._dot = ColorPill(color)
        layout.addWidget(self._dot)

        # Name + sub-label
        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        self.name_label = QLabel(name)
        self._refresh_name_style(is_active)
        text_col.addWidget(self.name_label)

        if is_active:
            self._sub = QLabel("Recording now")
            self._sub.setStyleSheet(
                f"color: {ACCENT_GREEN}; font-size: 11px; "
                f"font-weight: 500; border: none; background: transparent;"
            )
            text_col.addWidget(self._sub)
        else:
            self._sub = None

        layout.addLayout(text_col, 1)

        # Time label
        self.time_label = QLabel(fmt_seconds(total_seconds))
        self.time_label.setStyleSheet(f"""
            font-family: {FONT_MONO};
            font-size: 13px;
            color: {TEXT_SECONDARY};
            font-weight: 500;
            border: none;
            background: transparent;
            min-width: 68px;
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.time_label)

        # Actions (hidden until hover)
        self._actions = QWidget()
        act_row = QHBoxLayout(self._actions)
        act_row.setContentsMargins(0, 0, 0, 0)
        act_row.setSpacing(2)

        self._btn_start  = self._action_btn("▶", ACCENT, "Start timer")
        self._btn_rename = self._action_btn("✎", TEXT_MUTED, "Rename")
        self._btn_delete = self._action_btn("✕", ACCENT_RED, "Delete")

        self._btn_start.clicked.connect(lambda: self.start_requested.emit(self.project_id))
        self._btn_rename.clicked.connect(lambda: self.rename_requested.emit(self.project_id))
        self._btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.project_id))

        for btn in (self._btn_start, self._btn_rename, self._btn_delete):
            act_row.addWidget(btn)

        self._actions.setVisible(False)
        layout.addWidget(self._actions)

        self._update_bg(False)

    def _action_btn(self, text: str, color: str, tip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("btn_icon")
        btn.setToolTip(tip)
        btn.setFixedSize(28, 28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {color};
                border-radius: 6px;
                font-size: 13px;
                padding: 0;
            }}
            QPushButton:hover {{
                background: {color}18;
            }}
        """)
        return btn

    def _refresh_name_style(self, active: bool):
        color = ACCENT if active else TEXT_PRIMARY
        weight = "600" if active else "500"
        self.name_label.setStyleSheet(
            f"font-size: 13px; font-weight: {weight}; color: {color}; "
            f"border: none; background: transparent;"
        )

    def _update_bg(self, hovered: bool):
        if hovered:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {BG_HOVER};
                    border-radius: {RADIUS_SM}px;
                }}
            """)
        else:
            bg = f"{ACCENT}0A" if self._is_active else "transparent"
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg};
                    border-radius: {RADIUS_SM}px;
                }}
            """)

    def enterEvent(self, e):
        self._update_bg(True)
        self._actions.setVisible(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._update_bg(False)
        self._actions.setVisible(False)
        super().leaveEvent(e)

    def update_time(self, seconds: int):
        self.time_label.setText(fmt_seconds(seconds))

    def set_active(self, active: bool):
        self._is_active = active
        self._refresh_name_style(active)
        self._update_bg(False)


class ColorPill(QWidget):
    """Rounded rectangle color indicator."""

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(6, 32)

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 3, 3)


class MiniBarChart(QWidget):
    """
    Simple SVG-style bar chart for weekly breakdown.
    Drawn entirely with QPainter — no external libs needed.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []     # list of (label, seconds, color)
        self._max_val = 1
        self.setMinimumHeight(120)

    def set_data(self, data: list):
        """data: list of (label, seconds, color)"""
        self._data = data
        self._max_val = max((d[1] for d in data), default=1) or 1
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        n = len(self._data)
        pad_x = 8
        pad_top = 10
        pad_bottom = 28
        bar_area_h = h - pad_top - pad_bottom
        gap = 6
        bar_w = max(8, (w - pad_x * 2 - gap * (n - 1)) // n)

        for i, (label, val, color) in enumerate(self._data):
            x = pad_x + i * (bar_w + gap)
            bar_h = max(4, int(bar_area_h * val / self._max_val))
            y = pad_top + bar_area_h - bar_h

            # Background bar
            p.setBrush(QBrush(QColor(BORDER)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x, pad_top, bar_w, bar_area_h, 4, 4)

            # Value bar
            c = QColor(color)
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0, c)
            c2 = QColor(color)
            c2.setAlphaF(0.6)
            grad.setColorAt(1, c2)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)

            # Label
            p.setPen(QColor(TEXT_MUTED))
            font = QFont("DM Sans, Segoe UI")
            font.setPixelSize(10)
            p.setFont(font)
            from PyQt6.QtCore import QRectF
            p.drawText(
                QRectF(x - 4, h - pad_bottom + 6, bar_w + 8, 18),
                Qt.AlignmentFlag.AlignCenter, label
            )


class WeeklyBarChart(QWidget):
    """
    7-day bar chart showing hours worked per day.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._days = []   # list of (day_label, seconds)
        self.setMinimumHeight(160)
        self.setStyleSheet("background: transparent;")

    def set_data(self, days: list):
        self._days = days
        self.update()

    def paintEvent(self, event):
        if not self._days:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        from PyQt6.QtCore import QRectF

        w, h = self.width(), self.height()
        n = len(self._days)
        pad_l = 40
        pad_r = 12
        pad_top = 16
        pad_bot = 32
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_top - pad_bot

        max_secs = max((d[1] for d in self._days), default=1) or 1
        max_hrs = max_secs / 3600
        # Round up to nearest even hour for y-axis
        y_max = max(1, int(max_hrs) + 1)

        # Gridlines + y-axis labels
        p.setPen(QPen(QColor(BORDER), 1))
        font = QFont("DM Mono, Consolas")
        font.setPixelSize(10)
        p.setFont(font)
        for i in range(y_max + 1):
            y = pad_top + chart_h - int(chart_h * i / y_max)
            p.setPen(QPen(QColor(BORDER), 1))
            p.drawLine(pad_l, y, pad_l + chart_w, y)
            p.setPen(QColor(TEXT_MUTED))
            p.drawText(QRectF(0, y - 8, pad_l - 6, 16),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       f"{i}h")

        # Bars
        gap = 8
        bar_w = max(8, (chart_w - gap * (n - 1)) // n)
        today_idx = n - 1

        for i, (label, secs) in enumerate(self._days):
            x = pad_l + i * (bar_w + gap)
            bar_h = max(0, int(chart_h * secs / (y_max * 3600)))
            y = pad_top + chart_h - bar_h
            is_today = (i == today_idx)

            # Bar color
            color = QColor(ACCENT if is_today else ACCENT_BLUE)
            if not is_today:
                color.setAlphaF(0.55)

            if bar_h > 0:
                grad = QLinearGradient(x, y, x, y + bar_h)
                c1 = QColor(color); c1.setAlphaF(color.alphaF())
                c2 = QColor(color); c2.setAlphaF(color.alphaF() * 0.5)
                grad.setColorAt(0, c1)
                grad.setColorAt(1, c2)
                p.setBrush(QBrush(grad))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)

                # Value label on bar
                if secs > 60:
                    p.setPen(QColor(TEXT_SECONDARY))
                    font2 = QFont("DM Mono, Consolas")
                    font2.setPixelSize(9)
                    p.setFont(font2)
                    p.drawText(QRectF(x, y - 14, bar_w, 12),
                               Qt.AlignmentFlag.AlignCenter,
                               fmt_seconds(secs)[:-3])  # HH:MM only

            # Day label
            p.setPen(QColor(ACCENT if is_today else TEXT_MUTED))
            font3 = QFont("DM Sans, Segoe UI")
            font3.setPixelSize(11)
            font3.setBold(is_today)
            p.setFont(font3)
            p.drawText(QRectF(x - 4, h - pad_bot + 8, bar_w + 8, 18),
                       Qt.AlignmentFlag.AlignCenter, label)


class ProjectDonutChart(QWidget):
    """Mini donut chart showing project time distribution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._segments = []   # list of (name, seconds, color)
        self.setFixedSize(140, 140)

    def set_data(self, segments: list):
        self._segments = segments
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        outer_r = min(w, h) / 2 - 6
        inner_r = outer_r * 0.55
        ring_w = outer_r - inner_r

        total = sum(s[1] for s in self._segments) or 1
        angle = 90 * 16  # start at top

        if not self._segments:
            p.setPen(QPen(QColor(BORDER), ring_w))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2))
            return

        for name, secs, color in self._segments:
            span = int(-360 * 16 * secs / total)
            rect = QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
            p.setBrush(QBrush(QColor(color)))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.moveTo(QPointF(cx, cy))
            path.arcTo(rect, angle / 16, span / 16)
            path.lineTo(QPointF(cx, cy))
            p.drawPath(path)
            angle += span

        # Donut hole
        p.setBrush(QBrush(QColor(BG_BASE)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), inner_r, inner_r)