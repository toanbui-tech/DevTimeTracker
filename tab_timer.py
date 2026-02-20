"""
tab_timer.py — Main timer view (Tab 1)
Live clock, project list, start/stop controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from style import (
    BG_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_OK, FONT_SIZE_SM, FONT_SIZE_MD, PROJECT_COLORS
)
from widgets import LiveIndicator, ProjectListItem
from tracker import TimeTracker, fmt_seconds


class TimerTab(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._project_items: dict = {}
        self._color_index = 0

        self._build_ui()

        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)

        self.refresh_projects()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Timer panel ────────────────────────────────────────────────────────
        top = QFrame()
        top.setStyleSheet(f"QFrame {{ background-color: {BG_CARD}; border-bottom: 1px solid {BORDER}; }}")
        top.setFixedHeight(200)
        tl = QVBoxLayout(top)
        tl.setContentsMargins(32, 24, 32, 24)
        tl.setSpacing(8)

        # Status row
        sr = QHBoxLayout()
        self._live_dot = LiveIndicator()
        self._live_dot.setVisible(False)
        self._status_label = QLabel("No active timer")
        self._status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_SM}px;")
        sr.addWidget(self._live_dot)
        sr.addSpacing(6)
        sr.addWidget(self._status_label)
        sr.addStretch()
        tl.addLayout(sr)

        # Clock
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setObjectName("label_timer")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tl.addWidget(self._timer_label)

        # Active project name
        self._project_label = QLabel("")
        self._project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._project_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;")
        tl.addWidget(self._project_label)

        # Start/Stop button
        self._btn_toggle = QPushButton("Start Timer")
        self._btn_toggle.setObjectName("btn_primary")
        self._btn_toggle.setFixedHeight(44)
        self._btn_toggle.clicked.connect(self._toggle_timer)
        tl.addWidget(self._btn_toggle)

        root.addWidget(top)

        # ── Project list header ────────────────────────────────────────────────
        lh = QHBoxLayout()
        lh.setContentsMargins(20, 16, 16, 8)
        lbl = QLabel("PROJECTS")
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 600; letter-spacing: 1.5px;")
        lh.addWidget(lbl)
        lh.addStretch()
        btn_add = QPushButton("+ New Project")
        btn_add.setObjectName("btn_icon")
        btn_add.setStyleSheet(f"color: {ACCENT}; font-size: {FONT_SIZE_SM}px; padding: 4px 10px; border-radius: 4px;")
        btn_add.clicked.connect(self._add_project)
        lh.addWidget(btn_add)
        root.addLayout(lh)

        # ── Scrollable project list ────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(12, 4, 12, 12)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        root.addWidget(scroll, 1)

    # ── Tick ───────────────────────────────────────────────────────────────────

    def _tick(self):
        if not self.tracker.is_running:
            return
        self._timer_label.setText(fmt_seconds(self.tracker.elapsed_seconds()))
        pid = self.tracker.active_project_id
        if pid and pid in self._project_items:
            self._project_items[pid].update_time(self.tracker.get_project_total(pid))

    # ── Controls ───────────────────────────────────────────────────────────────

    def _toggle_timer(self):
        if self.tracker.is_running:
            self.tracker.stop_timer()
            self._update_timer_ui(running=False)
            self.data_changed.emit()
        else:
            projects = self.tracker.list_projects()
            if len(projects) == 1:
                self._start_for_project(projects[0]["id"])
            else:
                QMessageBox.information(
                    self, "Select a Project",
                    "Hover over a project in the list and click \u25b6 to start its timer."
                )

    def _start_for_project(self, project_id: int):
        if self.tracker.is_running and self.tracker.active_project_id != project_id:
            self.tracker.stop_timer()

        self.tracker.start_timer(project_id)

        name = next((p["name"] for p in self.tracker.list_projects() if p["id"] == project_id), "")
        self._update_timer_ui(running=True, project_name=name)
        self.data_changed.emit()

    def _update_timer_ui(self, running: bool, project_name: str = ""):
        self._live_dot.setVisible(running)

        if running:
            self._status_label.setText("Recording")
            self._status_label.setStyleSheet(f"color: {ACCENT_OK}; font-size: {FONT_SIZE_SM}px;")
            self._project_label.setText(project_name)
            self._btn_toggle.setText("Stop Timer")
            self._btn_toggle.setObjectName("btn_stop")
        else:
            self._status_label.setText("No active timer")
            self._status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_SM}px;")
            self._timer_label.setText("00:00:00")
            self._project_label.setText("")
            self._btn_toggle.setText("Start Timer")
            self._btn_toggle.setObjectName("btn_primary")

        # Force Qt to re-apply the objectName stylesheet
        self._btn_toggle.style().unpolish(self._btn_toggle)
        self._btn_toggle.style().polish(self._btn_toggle)

        for pid, item in self._project_items.items():
            item.set_active(running and pid == self.tracker.active_project_id)

    # ── Project management ─────────────────────────────────────────────────────

    def _add_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name.strip():
            color = PROJECT_COLORS[self._color_index % len(PROJECT_COLORS)]
            self._color_index += 1
            try:
                self.tracker.add_project(name.strip(), color)
                self.refresh_projects()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _rename_project(self, project_id: int):
        item = self._project_items.get(project_id)
        current = item.name_label.text() if item else ""
        name, ok = QInputDialog.getText(self, "Rename Project", "New name:", text=current)
        if ok and name.strip():
            try:
                self.tracker.rename_project(project_id, name.strip())
                self.refresh_projects()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_project(self, project_id: int):
        item = self._project_items.get(project_id)
        name = item.name_label.text() if item else ""
        reply = QMessageBox.question(
            self, "Delete Project",
            f"Delete '{name}'?\n\nTime sessions will be kept in history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.tracker.remove_project(project_id)
                self.refresh_projects()
                self.data_changed.emit()
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))

    # ── Refresh ────────────────────────────────────────────────────────────────

    def refresh_projects(self):
        for item in self._project_items.values():
            item.setParent(None)
        self._project_items.clear()

        while self._list_layout.count() > 1:
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        active_pid = self.tracker.active_project_id
        for p in self.tracker.list_projects():
            pid = p["id"]
            item = ProjectListItem(
                project_id=pid,
                name=p["name"],
                color=p["color"],
                total_seconds=self.tracker.get_project_total(pid),
                is_active=(pid == active_pid),
            )
            item.start_requested.connect(self._start_for_project)
            item.rename_requested.connect(self._rename_project)
            item.delete_requested.connect(self._delete_project)
            self._project_items[pid] = item
            self._list_layout.insertWidget(self._list_layout.count() - 1, item)

        if self.tracker.is_running:
            name = next((p["name"] for p in self.tracker.list_projects()
                         if p["id"] == active_pid), "")
            self._timer_label.setText(fmt_seconds(self.tracker.elapsed_seconds()))
            self._update_timer_ui(running=True, project_name=name)
        else:
            self._update_timer_ui(running=False)

    def notify_recovery(self, project_name: str):
        QMessageBox.information(
            self, "Session Recovered",
            f"TimeTracker resumed a running session for:\n\n"
            f"  \"{project_name}\"\n\n"
            f"The timer is still counting. Stop it when you are done."
        )