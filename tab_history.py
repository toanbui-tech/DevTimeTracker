"""
tab_history.py — Session history view
Filterable table of all work sessions with CSV export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont

from style import (
    ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    BORDER, FONT_MONO, FONT_SIZE_SM
)
from tracker import TimeTracker, fmt_seconds
from datetime import datetime


def _fmt_dt(iso: str) -> str:
    if not iso:
        return "\u2014"
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %Y  %H:%M")
    except Exception:
        return iso


class HistoryTab(QWidget):
    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(16)

        # ── Filter bar ─────────────────────────────────────────────────────────
        fb = QHBoxLayout()
        fb.setSpacing(10)

        fb.addWidget(QLabel("Project:"))
        self._cmb_project = QComboBox()
        self._cmb_project.setFixedWidth(180)
        self._cmb_project.addItem("All Projects", None)
        self._cmb_project.currentIndexChanged.connect(self._load_sessions)
        fb.addWidget(self._cmb_project)

        fb.addSpacing(8)
        fb.addWidget(QLabel("From:"))

        self._date_from = QDateEdit()
        self._date_from.setDisplayFormat("MMM dd, yyyy")
        self._date_from.setDate(QDate.currentDate().addDays(-30))
        self._date_from.setCalendarPopup(True)
        self._date_from.setFixedWidth(130)
        self._date_from.dateChanged.connect(self._load_sessions)
        fb.addWidget(self._date_from)

        fb.addWidget(QLabel("To:"))
        self._date_to = QDateEdit()
        self._date_to.setDisplayFormat("MMM dd, yyyy")
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setCalendarPopup(True)
        self._date_to.setFixedWidth(130)
        self._date_to.dateChanged.connect(self._load_sessions)
        fb.addWidget(self._date_to)

        fb.addStretch()

        for label, days in [("Today", 0), ("7 days", 7), ("30 days", 30), ("All", -1)]:
            btn = QPushButton(label)
            btn.setObjectName("btn_icon")
            btn.setStyleSheet(
                f"font-size: {FONT_SIZE_SM}px; padding: 4px 12px; "
                f"border-radius: 4px; color: {TEXT_SECONDARY};"
            )
            btn.clicked.connect(lambda _, d=days: self._quick_filter(d))
            fb.addWidget(btn)

        btn_export = QPushButton("\u2193 Export CSV")
        btn_export.setObjectName("btn_icon")
        btn_export.setStyleSheet(
            f"color: {ACCENT}; font-size: {FONT_SIZE_SM}px; "
            f"padding: 4px 14px; border: 1px solid {ACCENT}44; border-radius: 4px;"
        )
        btn_export.clicked.connect(self._export_csv)
        fb.addWidget(btn_export)

        root.addLayout(fb)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
        root.addWidget(line)

        self._summary = QLabel()
        self._summary.setStyleSheet(f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_SM}px;")
        root.addWidget(self._summary)

        # ── Table ──────────────────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Project", "Date", "Started", "Ended", "Duration"])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSortingEnabled(True)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 120), (2, 90), (3, 90), (4, 100)]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._table.setColumnWidth(col, w)

        root.addWidget(self._table, 1)

    def _quick_filter(self, days: int):
        today = QDate.currentDate()
        self._date_to.setDate(today)
        if days == 0:
            self._date_from.setDate(today)
        elif days == -1:
            self._date_from.setDate(QDate(2000, 1, 1))
        else:
            self._date_from.setDate(today.addDays(-days))

    def refresh(self):
        self._refresh_project_combo()
        self._load_sessions()

    def _refresh_project_combo(self):
        current_id = self._cmb_project.currentData()
        self._cmb_project.blockSignals(True)
        self._cmb_project.clear()
        self._cmb_project.addItem("All Projects", None)
        for p in self.tracker.list_projects():
            self._cmb_project.addItem(p["name"], p["id"])
        for i in range(self._cmb_project.count()):
            if self._cmb_project.itemData(i) == current_id:
                self._cmb_project.setCurrentIndex(i)
                break
        self._cmb_project.blockSignals(False)

    def _load_sessions(self):
        project_id = self._cmb_project.currentData()
        date_from  = self._date_from.date().toString("yyyy-MM-dd")
        date_to    = self._date_to.date().toString("yyyy-MM-dd")

        sessions = self.tracker.get_history(project_id, date_from, date_to)

        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(sessions))

        total_secs = 0
        mono = QFont("Consolas, SF Mono, Menlo")
        mono.setPointSize(10)

        for row_idx, s in enumerate(sessions):
            total_secs += s["duration"]

            start_dt = datetime.fromisoformat(s["start_time"]) if s["start_time"] else None
            end_dt   = datetime.fromisoformat(s["end_time"])   if s["end_time"]   else None

            date_str  = start_dt.strftime("%b %d, %Y") if start_dt else "\u2014"
            start_str = start_dt.strftime("%H:%M:%S")  if start_dt else "\u2014"
            end_str   = end_dt.strftime("%H:%M:%S")    if end_dt   else "\u2014"
            dur_str   = fmt_seconds(s["duration"])

            data = [
                (s["project_name"], Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, False),
                (date_str,          Qt.AlignmentFlag.AlignCenter, False),
                (start_str,         Qt.AlignmentFlag.AlignCenter, True),
                (end_str,           Qt.AlignmentFlag.AlignCenter, True),
                (dur_str,           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, True),
            ]

            for col, (text, align, is_mono) in enumerate(data):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align)
                if is_mono:
                    item.setFont(mono)
                    item.setForeground(QColor(TEXT_SECONDARY))
                self._table.setItem(row_idx, col, item)

            self._table.setRowHeight(row_idx, 44)

        self._table.setSortingEnabled(True)

        count = len(sessions)
        self._summary.setText(
            f"{count} session{'s' if count != 1 else ''}  \u00b7  Total: {fmt_seconds(total_secs)}"
        )

    def _export_csv(self):
        project_id = self._cmb_project.currentData()
        date_from  = self._date_from.date().toString("yyyy-MM-dd")
        date_to    = self._date_to.date().toString("yyyy-MM-dd")

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Sessions",
            f"timetracker_{date_from}_{date_to}.csv",
            "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            count = self.tracker.export_csv(path, project_id, date_from, date_to)
            QMessageBox.information(self, "Export Complete", f"Exported {count} sessions to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))