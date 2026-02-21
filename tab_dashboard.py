"""
tab_dashboard.py — Dashboard v2
Rich stats with weekly bar chart and project donut.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from datetime import date, timedelta

from style import (
    BG_SURFACE, BG_BASE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_BLUE, ACCENT_GREEN, ACCENT_PURPLE,
    FONT_MONO, RADIUS
)
from widgets import StatCard, WeeklyBarChart, ProjectDonutChart, ColorPill, Card, add_shadow
from tracker import TimeTracker, fmt_seconds
from database import get_sessions


class DashboardTab(QWidget):
    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._build_ui()
        self.refresh()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(1000)

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(24)

        # ── Page title ─────────────────────────────────────────────────────────
        title = QLabel("Dashboard")
        title.setObjectName("label_heading")
        root.addWidget(title)

        # ── Stat cards row ──────────────────────────────────────────────────────
        self._stat_today  = StatCard("Today",      "🌅", ACCENT)
        self._stat_week   = StatCard("This Week",  "📅", ACCENT_BLUE)
        self._stat_month  = StatCard("This Month", "🗓",  ACCENT_GREEN)
        self._stat_total  = StatCard("All Time",   "∞",  ACCENT_PURPLE)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        for card in (self._stat_today, self._stat_week, self._stat_month, self._stat_total):
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card.setFixedHeight(106)
            stats_row.addWidget(card)
        root.addLayout(stats_row)

        # ── Second row: bar chart + donut ───────────────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Weekly bar chart
        bar_card = Card()
        bar_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bar_card.setFixedHeight(240)
        bl = QVBoxLayout(bar_card)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)

        bar_hdr = QHBoxLayout()
        bar_title = QLabel("Last 7 Days")
        bar_title.setObjectName("label_subheading")
        bar_hdr.addWidget(bar_title)
        bar_hdr.addStretch()
        self._week_total_lbl = QLabel("")
        self._week_total_lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; font-family: {FONT_MONO}; border: none; background: transparent;"
        )
        bar_hdr.addWidget(self._week_total_lbl)
        bl.addLayout(bar_hdr)

        self._bar_chart = WeeklyBarChart()
        bl.addWidget(self._bar_chart, 1)
        charts_row.addWidget(bar_card, 2)

        # Project donut + legend
        donut_card = Card()
        donut_card.setFixedSize(280, 240)
        dl = QVBoxLayout(donut_card)
        dl.setContentsMargins(20, 16, 20, 16)
        dl.setSpacing(10)

        donut_title = QLabel("By Project")
        donut_title.setObjectName("label_subheading")
        dl.addWidget(donut_title)

        donut_row = QHBoxLayout()
        donut_row.setSpacing(12)

        self._donut = ProjectDonutChart()
        donut_row.addWidget(self._donut)

        self._legend = QVBoxLayout()
        self._legend.setSpacing(6)
        self._legend.addStretch()
        donut_row.addLayout(self._legend, 1)

        dl.addLayout(donut_row, 1)
        charts_row.addWidget(donut_card)

        root.addLayout(charts_row)

        # ── Project breakdown table ─────────────────────────────────────────────
        breakdown_card = Card()
        bc_layout = QVBoxLayout(breakdown_card)
        bc_layout.setContentsMargins(20, 16, 20, 16)
        bc_layout.setSpacing(12)

        bk_title = QLabel("Project Breakdown")
        bk_title.setObjectName("label_subheading")
        bc_layout.addWidget(bk_title)

        # Column headers
        col_hdr = QWidget()
        col_hdr.setStyleSheet("background: transparent;")
        ch = QHBoxLayout(col_hdr)
        ch.setContentsMargins(8, 0, 8, 4)
        for txt, w in [("Project", None), ("Today", 90), ("Week", 90), ("Month", 90), ("Total", 90)]:
            lbl = QLabel(txt.upper())
            lbl.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600; "
                f"letter-spacing: 0.8px; border: none; background: transparent;"
            )
            if w:
                lbl.setFixedWidth(w)
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                ch.addWidget(lbl)
            else:
                ch.addWidget(lbl, 1)
        bc_layout.addWidget(col_hdr)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background: {BORDER}; border: none;")
        div.setFixedHeight(1)
        bc_layout.addWidget(div)

        self._breakdown_layout = QVBoxLayout()
        self._breakdown_layout.setSpacing(0)
        bc_layout.addLayout(self._breakdown_layout)

        root.addWidget(breakdown_card)
        root.addStretch()

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self):
        stats = self.tracker.get_dashboard()

        # Summary stats
        self._stat_today.set_value(sum(s["today"] for s in stats))
        self._stat_week.set_value(sum(s["week"]   for s in stats))
        self._stat_month.set_value(sum(s["month"] for s in stats))
        self._stat_total.set_value(sum(s["total"] for s in stats))

        # Weekly bar chart data
        self._refresh_weekly_chart()

        # Donut chart
        segments = [
            (s["name"], s["total"], s["color"])
            for s in stats if s["total"] > 0
        ]
        self._donut.set_data(segments)

        # Legend
        while self._legend.count() > 1:
            child = self._legend.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_all = sum(s["total"] for s in stats) or 1
        for s in sorted(segments, key=lambda x: x[1], reverse=True)[:5]:
            name, secs, color = s
            row = self._legend_row(name, secs, total_all, color)
            self._legend.insertWidget(self._legend.count() - 1, row)

        # Breakdown table
        while self._breakdown_layout.count():
            child = self._breakdown_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for s in sorted(stats, key=lambda x: x["total"], reverse=True):
            if s["total"] == 0:
                continue
            row = self._breakdown_row(s)
            self._breakdown_layout.addWidget(row)

        if not any(s["total"] > 0 for s in stats):
            hint = QLabel("No time tracked yet. Start a timer to see stats here.")
            hint.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 13px; "
                f"padding: 20px 8px; border: none; background: transparent;"
            )
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._breakdown_layout.addWidget(hint)

    def _refresh_weekly_chart(self):
        today = date.today()
        days = []
        total_week = 0
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_start = d.isoformat() + "T00:00:00"
            day_end   = d.isoformat() + "T23:59:59"
            secs = sum(
                s["today"]
                for s in self._daily_total(day_start, day_end)
            )
            total_week += secs
            label = ["Mo","Tu","We","Th","Fr","Sa","Su"][d.weekday()]
            if i == 0:
                label = "Today"
            days.append((label, secs))

        self._bar_chart.set_data(days)
        self._week_total_lbl.setText(fmt_seconds(total_week))

    def _daily_total(self, day_start: str, day_end: str) -> list:
        """Get seconds per project for a given day."""
        sessions = get_sessions(self.tracker.conn, date_from=day_start[:10], date_to=day_end[:10])
        result = []
        total = sum(s["duration"] for s in sessions)
        result.append({"today": total})
        return result

    def _legend_row(self, name: str, secs: int, total: int, color: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(8)

        dot = ColorPill(color)
        dot.setFixedSize(4, 14)
        row.addWidget(dot)

        lbl = QLabel(name)
        lbl.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        lbl.setMaximumWidth(90)
        row.addWidget(lbl, 1)

        pct = int(secs * 100 / total)
        pct_lbl = QLabel(f"{pct}%")
        pct_lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        row.addWidget(pct_lbl)
        return w

    def _breakdown_row(self, s: dict) -> QWidget:
        w = QWidget()
        w.setFixedHeight(48)
        w.setStyleSheet("""
            QWidget { background: transparent; border-radius: 6px; }
            QWidget:hover { background: #F7F5F2; }
        """)
        row = QHBoxLayout(w)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(12)

        pill = ColorPill(s["color"])
        pill.setFixedSize(4, 24)
        row.addWidget(pill)

        name = QLabel(s["name"])
        name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        row.addWidget(name, 1)

        for val in (s["today"], s["week"], s["month"], s["total"]):
            lbl = QLabel(fmt_seconds(val) if val else "—")
            lbl.setFixedWidth(90)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl.setStyleSheet(
                f"color: {TEXT_SECONDARY if val else TEXT_MUTED}; "
                f"font-family: {FONT_MONO}; font-size: 12px; "
                f"border: none; background: transparent;"
            )
            row.addWidget(lbl)
        return w