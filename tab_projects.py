"""
tab_projects.py — Projects view v2
Modern card grid with color customization.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QInputDialog, QMessageBox, QScrollArea, QFrame,
    QColorDialog, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient

from style import (
    BG_SURFACE, BG_BASE, BG_HOVER, BORDER, BORDER_MED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_LIGHT, ACCENT_DARK, ACCENT_GREEN, ACCENT_GREEN_LIGHT,
    ACCENT_RED, ACCENT_RED_LIGHT, FONT_MONO, FONT_DISPLAY,
    RADIUS, RADIUS_SM, RADIUS_LG, PROJECT_COLORS
)
from widgets import add_shadow
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
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Projects")
        title.setObjectName("label_heading")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_new = QPushButton("+ New Project")
        btn_new.setObjectName("btn_primary")
        btn_new.setFixedHeight(38)
        btn_new.clicked.connect(self._add_project)
        hdr.addWidget(btn_new)
        root.addLayout(hdr)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(16)
        self._grid.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self._container)
        root.addWidget(scroll, 1)

    def refresh(self):
        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        projects = self.tracker.list_projects()
        active_pid = self.tracker.active_project_id

        if not projects:
            hint = QLabel("No projects yet.\nClick '+ New Project' to get started.")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 14px; line-height: 1.6; "
                f"border: none; background: transparent;"
            )
            self._grid.addWidget(hint, 0, 0, 1, 3)
            return

        cols = 3
        for idx, p in enumerate(projects):
            card = ProjectCard(
                project_id=p["id"],
                name=p["name"],
                color=p["color"],
                total_seconds=self.tracker.get_project_total(p["id"]),
                is_active=(p["id"] == active_pid),
            )
            card.rename_requested.connect(self._rename)
            card.delete_requested.connect(self._delete)
            card.color_requested.connect(self._change_color)
            self._grid.addWidget(card, idx // cols, idx % cols)

        # Fill remaining cells
        remainder = len(projects) % cols
        if remainder:
            for i in range(cols - remainder):
                spacer = QWidget()
                spacer.setStyleSheet("background: transparent;")
                self._grid.addWidget(spacer, len(projects) // cols, remainder + i)

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
        name, ok = QInputDialog.getText(
            self, "Rename Project", "New name:", text=current_name
        )
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
            f"Delete \"{name}\"?\n\nTime sessions will be kept in History.",
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
        color = QColorDialog.getColor(QColor(current_color), self, "Choose Color")
        if color.isValid():
            self.tracker.set_project_color(project_id, color.name())
            self.refresh()
            self.projects_changed.emit()


class ProjectCard(QWidget):
    """
    Rich project card with gradient top bar, stats, and action buttons.
    """

    rename_requested = pyqtSignal(int, str)
    delete_requested = pyqtSignal(int, str)
    color_requested  = pyqtSignal(int, str)

    def __init__(self, project_id: int, name: str, color: str,
                 total_seconds: int, is_active: bool, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self._color = color
        self._name  = name
        self._is_active = is_active

        self.setMinimumSize(200, 160)
        self.setMaximumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_SURFACE};
                border-radius: {RADIUS_LG}px;
                border: 1px solid {BORDER};
            }}
        """)
        add_shadow(self, blur=20, offset=(0, 4), color=(0, 0, 0, 12))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Color header strip
        self._header = ColorHeader(color, name, is_active)
        self._header.setFixedHeight(80)
        self._header.color_clicked.connect(
            lambda: self.color_requested.emit(self.project_id, self._color)
        )
        layout.addWidget(self._header)

        # Body
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 12, 16, 14)
        body_layout.setSpacing(10)

        # Total time
        time_row = QHBoxLayout()
        time_icon = QLabel("⏱")
        time_icon.setStyleSheet("font-size: 12px; border: none; background: transparent;")
        time_row.addWidget(time_icon)

        time_lbl = QLabel(fmt_seconds(total_seconds))
        time_lbl.setStyleSheet(f"""
            font-family: {FONT_MONO};
            font-size: 16px;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            border: none;
            background: transparent;
        """)
        time_row.addWidget(time_lbl)
        time_row.addStretch()

        if is_active:
            badge = QLabel("Live")
            badge.setStyleSheet(f"""
                color: {ACCENT_GREEN};
                background: {ACCENT_GREEN_LIGHT};
                border-radius: 10px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            """)
            time_row.addWidget(badge)

        body_layout.addLayout(time_row)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(8)

        btn_rename = self._small_btn("Rename", TEXT_SECONDARY, BORDER)
        btn_rename.clicked.connect(lambda: self.rename_requested.emit(self.project_id, self._name))
        actions.addWidget(btn_rename)

        btn_delete = self._small_btn("Delete", ACCENT_RED, f"{ACCENT_RED}33")
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.project_id, self._name))
        actions.addWidget(btn_delete)
        actions.addStretch()

        body_layout.addLayout(actions)
        layout.addWidget(body)

    def _small_btn(self, text: str, color: str, border: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {color};
                border: 1.5px solid {border};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {color}14;
                border-color: {color};
            }}
        """)
        return btn


class ColorHeader(QWidget):
    """Gradient top portion of project card, clickable to change color."""

    color_clicked = pyqtSignal()

    def __init__(self, color: str, name: str, is_active: bool, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._name = name
        self._is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to change color")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"""
            color: white;
            font-size: 14px;
            font-weight: 700;
            font-family: {FONT_DISPLAY};
            border: none;
            background: transparent;
        """)
        layout.addWidget(name_lbl, 1)

        if is_active:
            dot = QLabel("●")
            dot.setStyleSheet(
                "color: white; font-size: 10px; border: none; background: transparent;"
            )
            layout.addWidget(dot)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, self.width(), self.height())
        c1 = QColor(self._color)
        c2 = QColor(self._color)
        c2.setHsv(
            (c1.hsvHue() + 20) % 360,
            min(255, c1.hsvSaturation() + 30),
            max(0, c1.value() - 30)
        )
        grad.setColorAt(0, c1)
        grad.setColorAt(1, c2)

        from PyQt6.QtGui import QPainterPath
        from PyQt6.QtCore import QRectF
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), RADIUS_LG, RADIUS_LG)
        # Only round top corners — clip bottom to square
        p.setClipPath(path)
        p.fillRect(self.rect(), QBrush(grad))

    def mousePressEvent(self, e):
        self.color_clicked.emit()
        super().mousePressEvent(e)