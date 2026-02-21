"""
main_window.py — Main window v2
Two-panel layout: sidebar (left) + content area (right).
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent

from style import APP_STYLE, BG_BASE, BG_SIDEBAR, ACCENT_GREEN
from sidebar import Sidebar
from tab_timer import TimerTab
from tab_dashboard import DashboardTab
from tab_history import HistoryTab
from tab_projects import ProjectsTab
from tracker import TimeTracker, fmt_seconds


class MainWindow(QMainWindow):
    def __init__(self, tracker: TimeTracker):
        super().__init__()
        self.tracker = tracker
        self.setWindowTitle("TimeTracker")
        self.setMinimumSize(900, 620)
        self.resize(1080, 720)
        self.setStyleSheet(APP_STYLE)
        self._build_ui()
        self._check_recovery()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────────────
        self._sidebar = Sidebar(self.tracker)
        self._sidebar.nav_changed.connect(self._on_nav)
        root.addWidget(self._sidebar)

        # ── Content stack ──────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {BG_BASE};")

        self._timer_tab = TimerTab(self.tracker)
        self._dash_tab  = DashboardTab(self.tracker)
        self._hist_tab  = HistoryTab(self.tracker)
        self._proj_tab  = ProjectsTab(self.tracker)

        self._pages = {
            "timer":     self._timer_tab,
            "dashboard": self._dash_tab,
            "history":   self._hist_tab,
            "projects":  self._proj_tab,
        }

        for page in self._pages.values():
            self._stack.addWidget(page)

        # Wire data changes
        self._timer_tab.data_changed.connect(self._on_data_changed)
        self._proj_tab.projects_changed.connect(self._on_data_changed)

        root.addWidget(self._stack, 1)

    def _on_nav(self, page: str):
        widget = self._pages.get(page)
        if widget:
            self._stack.setCurrentWidget(widget)
            if hasattr(widget, "refresh"):
                widget.refresh()

    def _on_data_changed(self):
        self._timer_tab.refresh_projects()
        # Refresh current page if it's dashboard/history/projects
        current = self._stack.currentWidget()
        if current in (self._dash_tab, self._hist_tab, self._proj_tab):
            if hasattr(current, "refresh"):
                current.refresh()

    def _check_recovery(self):
        if self.tracker.recovered:
            pid = self.tracker.active_project_id
            name = next(
                (p["name"] for p in self.tracker.list_projects() if p["id"] == pid),
                "Unknown"
            )
            self.tracker.acknowledge_recovery()
            QTimer.singleShot(400, lambda: self._timer_tab.notify_recovery(name))

    def closeEvent(self, event: QCloseEvent):
        if self.tracker.is_running:
            msg = QMessageBox(self)
            msg.setWindowTitle("Timer Still Running")
            msg.setText(
                "A timer is still running.\n\n"
                "Close Anyway \u2192 timer will auto-resume next launch.\n"
                "Stop && Close \u2192 save the session now."
            )
            btn_close  = msg.addButton("Close Anyway",  QMessageBox.ButtonRole.DestructiveRole)
            btn_stop   = msg.addButton("Stop && Close", QMessageBox.ButtonRole.AcceptRole)
            btn_cancel = msg.addButton("Cancel",        QMessageBox.ButtonRole.RejectRole)
            msg.setDefaultButton(btn_cancel)
            msg.exec()

            clicked = msg.clickedButton()
            if clicked == btn_cancel:
                event.ignore()
                return
            elif clicked == btn_stop:
                self.tracker.stop_timer()

        self.tracker.close()
        event.accept()