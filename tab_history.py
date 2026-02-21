"""
tab_history.py — History view v2
Clean session log with improved filtering and export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QFrame, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont, QBrush

from style import (
    BG_SURFACE, BG_BASE, BG_HOVER, BORDER, BORDER_MED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_LIGHT, ACCENT_DARK, ACCENT_GREEN, ACCENT_GREEN_LIGHT,
    FONT_MONO, RADIUS, RADIUS_SM
)
from widgets import Card, add_shadow
from tracker import TimeTracker, fmt_seconds
from datetime import datetime


class HistoryTab(QWidget):
    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # ── Title ──────────────────────────────────────────────────────────────
        title = QLabel("History")
        title.setObjectName("label_heading")
        root.addWidget(title)

        # ── Filter card ────────────────────────────────────────────────────────
        filter_card = Card()
        filter_card.setFixedHeight(68)
        fc = QHBoxLayout(filter_card)
        fc.setContentsMargins(16, 0, 16, 0)
        fc.setSpacing(14)

        # Project
        fc.addWidget(self._caption("Project"))
        self._cmb_project = QComboBox()
        self._cmb_project.setFixedWidth(170)
        self._cmb_project.addItem("All Projects", None)
        self._cmb_project.currentIndexChanged.connect(self._load_sessions)
        fc.addWidget(self._cmb_project)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-width: 1px;")
        fc.addWidget(sep)

        # Date range
        fc.addWidget(self._caption("From"))
        self._date_from = QDateEdit()
        self._date_from.setDisplayFormat("MMM dd, yyyy")
        self._date_from.setDate(QDate.currentDate().addDays(-30))
        self._date_from.setCalendarPopup(True)
        self._date_from.setFixedWidth(130)
        self._date_from.dateChanged.connect(self._load_sessions)
        fc.addWidget(self._date_from)

        fc.addWidget(self._caption("To"))
        self._date_to = QDateEdit()
        self._date_to.setDisplayFormat("MMM dd, yyyy")
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setCalendarPopup(True)
        self._date_to.setFixedWidth(130)
        self._date_to.dateChanged.connect(self._load_sessions)
        fc.addWidget(self._date_to)

        fc.addStretch()

        # Quick filters
        for label, days in [("Today", 0), ("7d", 7), ("30d", 30), ("All", -1)]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_BASE};
                    color: {TEXT_SECONDARY};
                    border: 1.5px solid {BORDER};
                    border-radius: 6px;
                    padding: 0 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {ACCENT_LIGHT};
                    color: {ACCENT};
                    border-color: {ACCENT}44;
                }}
            """)
            btn.clicked.connect(lambda checked=False, d=days: self._quick_filter(d))
            fc.addWidget(btn)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-width: 1px;")
        fc.addWidget(sep2)

        btn_export = QPushButton("↓ Export CSV")
        btn_export.setFixedHeight(34)
        btn_export.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: {RADIUS_SM}px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {ACCENT_DARK}; }}
        """)
        btn_export.clicked.connect(self._export_csv)
        fc.addWidget(btn_export)

        root.addWidget(filter_card)

        # ── Summary row ────────────────────────────────────────────────────────
        self._summary_row = QHBoxLayout()
        self._summary_row.setSpacing(20)
        self._sessions_lbl = self._summary_chip("0 sessions", ACCENT)
        self._total_lbl    = self._summary_chip("Total: 00:00:00", TEXT_SECONDARY)
        self._summary_row.addWidget(self._sessions_lbl)
        self._summary_row.addWidget(self._total_lbl)
        self._summary_row.addStretch()
        root.addLayout(self._summary_row)

        # ── Table ──────────────────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "Project", "Date", "Started", "Finished", "Duration"
        ])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSortingEnabled(True)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_SURFACE};
                border-radius: {RADIUS}px;
                border: 1px solid {BORDER};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {BG_BASE};
                padding: 0 14px;
            }}
            QTableWidget::item:selected {{
                background: {ACCENT_LIGHT};
            }}
        """)
        add_shadow(self._table)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 130), (2, 90), (3, 90), (4, 110)]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._table.setColumnWidth(col, w)

        root.addWidget(self._table, 1)

    def _caption(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        return lbl

    def _summary_chip(self, text: str, color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
            font-weight: 600;
            background: {color}14;
            border-radius: 20px;
            padding: 3px 12px;
            border: none;
        """)
        return lbl

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
        sessions   = self.tracker.get_history(project_id, date_from, date_to)

        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(sessions))

        total_secs = 0
        mono = QFont("DM Mono, Consolas")
        mono.setPixelSize(12)

        for i, s in enumerate(sessions):
            total_secs += s["duration"]

            start_dt = datetime.fromisoformat(s["start_time"]) if s["start_time"] else None
            end_dt   = datetime.fromisoformat(s["end_time"])   if s["end_time"]   else None

            date_str  = start_dt.strftime("%b %d, %Y") if start_dt else "—"
            start_str = start_dt.strftime("%H:%M:%S")  if start_dt else "—"
            end_str   = end_dt.strftime("%H:%M:%S")    if end_dt   else "—"

            # Project cell with color dot
            proj_item = QTableWidgetItem(f"  {s['project_name']}")
            proj_item.setForeground(QBrush(QColor(TEXT_PRIMARY)))
            self._table.setItem(i, 0, proj_item)

            for col, (text, is_mono) in enumerate([
                (date_str,  False),
                (start_str, True),
                (end_str,   True),
                (fmt_seconds(s["duration"]), True),
            ], start=1):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if is_mono:
                    item.setFont(mono)
                    item.setForeground(QBrush(QColor(TEXT_SECONDARY)))
                self._table.setItem(i, col, item)

            self._table.setRowHeight(i, 48)

        self._table.setSortingEnabled(True)

        count = len(sessions)
        self._sessions_lbl.setText(f"{count} session{'s' if count != 1 else ''}")
        self._total_lbl.setText(f"Total: {fmt_seconds(total_secs)}")

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
            QMessageBox.information(
                self, "Export Complete",
                f"Exported {count} sessions to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))