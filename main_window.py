"""
main_window.py — Application window
Owns the tab bar and wires together all tabs.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent

from style import APP_STYLE, BG_DARK, BORDER, TEXT_MUTED, ACCENT_OK
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
        self.setMinimumSize(760, 600)
        self.resize(900, 680)
        self.setStyleSheet(APP_STYLE)
        self._build_ui()
        self._check_recovery()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self._tabs.setDocumentMode(True)

        self._timer_tab = TimerTab(self.tracker)
        self._dash_tab  = DashboardTab(self.tracker)
        self._hist_tab  = HistoryTab(self.tracker)
        self._proj_tab  = ProjectsTab(self.tracker)

        self._tabs.addTab(self._timer_tab, "  Timer  ")
        self._tabs.addTab(self._dash_tab,  "  Dashboard  ")
        self._tabs.addTab(self._hist_tab,  "  History  ")
        self._tabs.addTab(self._proj_tab,  "  Projects  ")

        self._timer_tab.data_changed.connect(self._on_data_changed)
        self._proj_tab.projects_changed.connect(self._on_data_changed)
        self._tabs.currentChanged.connect(self._on_tab_changed)

        root.addWidget(self._tabs)

        # Status bar
        status = QWidget()
        status.setFixedHeight(28)
        status.setStyleSheet(f"background: {BG_DARK}; border-top: 1px solid {BORDER};")
        slay = QHBoxLayout(status)
        slay.setContentsMargins(16, 0, 16, 0)

        self._status_left = QLabel("Ready")
        self._status_left.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        slay.addWidget(self._status_left)
        slay.addStretch()

        self._status_right = QLabel("")
        self._status_right.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-family: Consolas;")
        slay.addWidget(self._status_right)

        root.addWidget(status)

        self._status_clock = QTimer(self)
        self._status_clock.timeout.connect(self._update_status)
        self._status_clock.start(1000)

    def _update_status(self):
        from datetime import datetime
        self._status_right.setText(datetime.now().strftime("%a %b %d, %Y  %H:%M:%S"))
        if self.tracker.is_running:
            self._status_left.setText(f"\u25cf Recording  {fmt_seconds(self.tracker.elapsed_seconds())}")
            self._status_left.setStyleSheet(f"color: {ACCENT_OK}; font-size: 11px;")
        else:
            self._status_left.setText("Ready")
            self._status_left.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")

    def _on_tab_changed(self, index: int):
        widget = self._tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _on_data_changed(self):
        self._timer_tab.refresh_projects()

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
                "Close Anyway \u2192 timer resumes automatically next launch.\n"
                "Stop && Close \u2192 save the current session now."
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