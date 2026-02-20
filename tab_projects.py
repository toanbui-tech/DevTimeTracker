"""
tab_projects.py — Project management view
Create, rename, change color, delete projects.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QInputDialog, QMessageBox, QScrollArea, QFrame, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from style import (
    BG_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_HOT, FONT_MONO, FONT_SIZE_SM, FONT_SIZE_MD,
    FONT_SIZE_LG, RADIUS, PROJECT_COLORS
)
from widgets import Card
from tracker import TimeTracker, fmt_seconds


class ProjectsTab(QWidget):
    projects_changed = pyqtSignal()

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._color_index = 0
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Projects")
        title.setObjectName("label_heading")
        header.addWidget(title)
        header.addStretch()
        btn_new = QPushButton("+ New Project")
        btn_new.setObjectName("btn_primary")
        btn_new.setFixedHeight(36)
        btn_new.clicked.connect(self._add_project)
        header.addWidget(btn_new)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._layout.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    def refresh(self):
        while self._layout.count() > 1:
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        projects = self.tracker.list_projects()
        active_pid = self.tracker.active_project_id

        if not projects:
            hint = QLabel("No projects yet. Click '+ New Project' to get started.")
            hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: {FONT_SIZE_MD}px;")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, hint)
            return

        for p in projects:
            self._layout.insertWidget(
                self._layout.count() - 1,
                self._build_card(p, active_pid)
            )

    def _build_card(self, p: dict, active_pid: int) -> QWidget:
        card = Card()
        card.setFixedHeight(70)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(12)

        # Clickable color swatch
        color_btn = QPushButton()
        color_btn.setFixedSize(24, 24)
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {p['color']};
                border-radius: 12px;
                border: 2px solid {p['color']}66;
            }}
            QPushButton:hover {{ border: 2px solid {p['color']}; }}
        """)
        color_btn.setToolTip("Click to change color")
        color_btn.clicked.connect(
            lambda _, pid=p["id"], c=p["color"]: self._change_color(pid, c)
        )
        layout.addWidget(color_btn)

        # Name
        name_lbl = QLabel(p["name"])
        name_lbl.setStyleSheet(
            f"font-size: {FONT_SIZE_MD}px; font-weight: 500; color: {TEXT_PRIMARY};"
        )
        layout.addWidget(name_lbl, 1)

        # Running badge
        if p["id"] == active_pid:
            badge = QLabel("\u25cf RUNNING")
            badge.setStyleSheet(
                "color: #3DD68C; font-size: 10px; font-weight: 600; letter-spacing: 1px;"
            )
            layout.addWidget(badge)

        # Total time
        total = self.tracker.get_project_total(p["id"])
        time_lbl = QLabel(fmt_seconds(total))
        time_lbl.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: {FONT_SIZE_SM}px; color: {TEXT_SECONDARY};"
        )
        layout.addWidget(time_lbl)

        layout.addSpacing(8)

        btn_rename = QPushButton("Rename")
        btn_rename.setStyleSheet(
            f"font-size: {FONT_SIZE_SM}px; padding: 4px 12px; "
            f"border: 1px solid {BORDER}; border-radius: 4px; color: {TEXT_SECONDARY};"
        )
        btn_rename.clicked.connect(
            lambda _, pid=p["id"], name=p["name"]: self._rename(pid, name)
        )
        layout.addWidget(btn_rename)

        btn_del = QPushButton("Delete")
        btn_del.setStyleSheet(
            f"font-size: {FONT_SIZE_SM}px; padding: 4px 12px; "
            f"border: 1px solid {ACCENT_HOT}44; border-radius: 4px; color: {ACCENT_HOT};"
        )
        btn_del.clicked.connect(
            lambda _, pid=p["id"], name=p["name"]: self._delete(pid, name)
        )
        layout.addWidget(btn_del)

        return card

    def _add_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name.strip():
            color = PROJECT_COLORS[self._color_index % len(PROJECT_COLORS)]
            self._color_index += 1
            try:
                self.tracker.add_project(name.strip(), color)
                self.refresh()
                self.projects_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _rename(self, project_id: int, current_name: str):
        name, ok = QInputDialog.getText(self, "Rename Project", "New name:", text=current_name)
        if ok and name.strip():
            try:
                self.tracker.rename_project(project_id, name.strip())
                self.refresh()
                self.projects_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete(self, project_id: int, name: str):
        reply = QMessageBox.question(
            self, "Delete Project",
            f"Delete '{name}'?\n\nSessions will be kept in history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.tracker.remove_project(project_id)
                self.refresh()
                self.projects_changed.emit()
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))

    def _change_color(self, project_id: int, current_color: str):
        color = QColorDialog.getColor(QColor(current_color), self, "Choose Project Color")
        if color.isValid():
            self.tracker.set_project_color(project_id, color.name())
            self.refresh()
            self.projects_changed.emit()