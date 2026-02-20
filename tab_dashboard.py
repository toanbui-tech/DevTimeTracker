"""
tab_dashboard.py — Dashboard view
Per-project time breakdown: today / this week / this month / all-time.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer

from style import (
    BG_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_MONO, FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_LG, RADIUS
)
from widgets import ColorDot, StatBox, Card
from tracker import TimeTracker, fmt_seconds


class DashboardTab(QWidget):
    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._build_ui()
        self.refresh()

        # Refresh every second so live sessions update
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(1000)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # Overview label
        lbl = QLabel("OVERVIEW")
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600; letter-spacing: 1.5px;")
        root.addWidget(lbl)

        # Summary stat boxes
        sr = QHBoxLayout()
        sr.setSpacing(12)
        self._stat_today = StatBox("Today")
        self._stat_week  = StatBox("This Week")
        self._stat_month = StatBox("This Month")
        self._stat_total = StatBox("All Time")
        for box in (self._stat_today, self._stat_week, self._stat_month, self._stat_total):
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            box.setFixedHeight(80)
            sr.addWidget(box)
        root.addLayout(sr)

        # By project label
        lbl2 = QLabel("BY PROJECT")
        lbl2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600; letter-spacing: 1.5px;")
        root.addWidget(lbl2)

        # Scrollable project cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._projects_widget = QWidget()
        self._projects_layout = QVBoxLayout(self._projects_widget)
        self._projects_layout.setContentsMargins(0, 0, 0, 0)
        self._projects_layout.setSpacing(8)
        self._projects_layout.addStretch()

        scroll.setWidget(self._projects_widget)
        root.addWidget(scroll, 1)

    def refresh(self):
        stats = self.tracker.get_dashboard()

        self._stat_today.set_value(sum(s["today"] for s in stats))
        self._stat_week.set_value(sum(s["week"]   for s in stats))
        self._stat_month.set_value(sum(s["month"] for s in stats))
        self._stat_total.set_value(sum(s["total"] for s in stats))

        # Rebuild project rows
        while self._projects_layout.count() > 1:
            child = self._projects_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for s in sorted(stats, key=lambda x: x["total"], reverse=True):
            if s["total"] == 0:
                continue
            self._projects_layout.insertWidget(
                self._projects_layout.count() - 1,
                self._build_row(s)
            )

        if not any(s["total"] > 0 for s in stats):
            hint = QLabel("No time tracked yet. Start a timer to see stats here.")
            hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_MD}px;")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._projects_layout.insertWidget(0, hint)

    def _build_row(self, s: dict) -> QWidget:
        card = Card()
        card.setFixedHeight(72)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        dot = ColorDot(s["color"], size=10)
        layout.addWidget(dot)

        name = QLabel(s["name"])
        name.setStyleSheet(f"font-size: {FONT_SIZE_MD}px; font-weight: 500; color: {TEXT_PRIMARY};")
        layout.addWidget(name, 1)

        for label_text, seconds in [
            ("TODAY", s["today"]),
            ("WEEK",  s["week"]),
            ("MONTH", s["month"]),
            ("TOTAL", s["total"]),
        ]:
            cell = QVBoxLayout()
            cell.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: 600; letter-spacing: 1px;")
            val = QLabel(fmt_seconds(seconds))
            val.setStyleSheet(f"color: {TEXT_SECONDARY}; font-family: {FONT_MONO}; font-size: {FONT_SIZE_SM}px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            cell.addWidget(lbl)
            cell.addWidget(val)
            layout.addLayout(cell)

        return card