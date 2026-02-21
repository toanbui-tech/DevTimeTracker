"""
tab_timer.py — Timer view v3
Clean project cards. Each card has a prominent Start/Stop button.
No hover tricks. Professional, simple, obvious UX.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QInputDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from style import (
    BG_SURFACE, BG_BASE, BG_HOVER, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    ACCENT_GREEN, ACCENT_GREEN_LIGHT,
    ACCENT_RED, ACCENT_RED_LIGHT,
    FONT_MONO, PROJECT_COLORS, RADIUS, RADIUS_SM
)
from widgets import add_shadow
from tracker import TimeTracker, fmt_seconds


class TimerTab(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        self._cards: dict = {}
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

        # ── Top bar ────────────────────────────────────────────────────────────
        topbar = QWidget()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(
            f"background: {BG_SURFACE}; border-bottom: 1px solid {BORDER};"
        )
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(28, 0, 28, 0)

        title = QLabel("Timer")
        title.setObjectName("label_heading")
        tb.addWidget(title)
        tb.addStretch()

        self._global_status = QLabel("No timer running")
        self._global_status.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; border: none; background: transparent;"
        )
        tb.addWidget(self._global_status)
        tb.addSpacing(20)

        btn_add = QPushButton("+ New Project")
        btn_add.setFixedHeight(36)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: {RADIUS_SM}px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {ACCENT_DARK}; }}
            QPushButton:pressed {{ background: #C2410C; }}
        """)
        btn_add.clicked.connect(self._add_project)
        tb.addWidget(btn_add)
        root.addWidget(topbar)

        # ── Scrollable project cards ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background: {BG_BASE};")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._cards_container = QWidget()
        self._cards_container.setStyleSheet(f"background: {BG_BASE};")
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(28, 24, 28, 24)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()

        scroll.setWidget(self._cards_container)
        root.addWidget(scroll, 1)

    # ── Tick ───────────────────────────────────────────────────────────────────

    def _tick(self):
        if not self.tracker.is_running:
            return
        pid = self.tracker.active_project_id
        elapsed = self.tracker.elapsed_seconds()

        if pid in self._cards:
            self._cards[pid].update_elapsed(elapsed)

        name = next(
            (p["name"] for p in self.tracker.list_projects() if p["id"] == pid), ""
        )
        self._global_status.setText(f"● {name}  {fmt_seconds(elapsed)}")
        self._global_status.setStyleSheet(
            f"color: {ACCENT_GREEN}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )

    # ── Start / Stop ───────────────────────────────────────────────────────────

    def _start_project(self, project_id: int):
        prev_pid = self.tracker.active_project_id
        if self.tracker.is_running:
            self.tracker.stop_timer()
            if prev_pid in self._cards:
                self._cards[prev_pid].set_state("idle")

        self.tracker.start_timer(project_id)

        if project_id in self._cards:
            self._cards[project_id].set_state("running")

        self.data_changed.emit()

    def _stop_timer(self, project_id: int):
        self.tracker.stop_timer()
        if project_id in self._cards:
            self._cards[project_id].set_state("idle")

        self._global_status.setText("No timer running")
        self._global_status.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        self.data_changed.emit()

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
        card = self._cards.get(project_id)
        current = card._name if card else ""
        name, ok = QInputDialog.getText(
            self, "Rename Project", "New name:", text=current
        )
        if ok and name.strip():
            try:
                self.tracker.rename_project(project_id, name.strip())
                self.refresh_projects()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_project(self, project_id: int):
        card = self._cards.get(project_id)
        name = card._name if card else ""
        reply = QMessageBox.question(
            self, "Delete Project",
            f"Delete \"{name}\"?\n\nAll time history will be preserved.",
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
        for card in self._cards.values():
            card.setParent(None)
        self._cards.clear()

        while self._cards_layout.count() > 1:
            child = self._cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        projects = self.tracker.list_projects()
        active_pid = self.tracker.active_project_id

        if not projects:
            hint = QLabel("No projects yet.\nClick \"+ New Project\" to get started.")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 14px; "
                f"padding: 60px 0; border: none; background: transparent;"
            )
            self._cards_layout.insertWidget(0, hint)
            return

        for p in projects:
            pid = p["id"]
            is_active = (pid == active_pid)
            elapsed = self.tracker.elapsed_seconds() if is_active else 0

            card = ProjectCard(
                project_id=pid,
                name=p["name"],
                color=p["color"],
                total_seconds=self.tracker.get_project_total(pid),
                elapsed_seconds=elapsed,
                is_active=is_active,
            )
            card.start_clicked.connect(self._start_project)
            card.stop_clicked.connect(self._stop_timer)
            card.rename_clicked.connect(self._rename_project)
            card.delete_clicked.connect(self._delete_project)

            self._cards[pid] = card
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

        # Sync global status
        if self.tracker.is_running and active_pid in self._cards:
            name = next((p["name"] for p in projects if p["id"] == active_pid), "")
            self._global_status.setText(
                f"● {name}  {fmt_seconds(self.tracker.elapsed_seconds())}"
            )
            self._global_status.setStyleSheet(
                f"color: {ACCENT_GREEN}; font-size: 12px; font-weight: 600; "
                f"border: none; background: transparent;"
            )
        else:
            self._global_status.setText("No timer running")
            self._global_status.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 12px; "
                f"border: none; background: transparent;"
            )

    def notify_recovery(self, project_name: str):
        QMessageBox.information(
            self, "Session Recovered",
            f"Your timer for \"{project_name}\" was still running.\n"
            f"It has been resumed automatically."
        )


# ── Project Card ───────────────────────────────────────────────────────────────

class ProjectCard(QWidget):
    """
    Full-width project card:
      [color bar] | [name + total] | [live elapsed] | [Rename] [Delete] [▶ Start / ⏹ Stop]
    Button is always visible and large — no hover required.
    """

    start_clicked  = pyqtSignal(int)
    stop_clicked   = pyqtSignal(int)
    rename_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)

    def __init__(self, project_id: int, name: str, color: str,
                 total_seconds: int, elapsed_seconds: int = 0,
                 is_active: bool = False, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self._name = name
        self._color = color
        self._total = total_seconds
        self._is_active = is_active

        self.setFixedHeight(88)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        add_shadow(self, blur=10, offset=(0, 2), color=(0, 0, 0, 8))

        self._build_ui(elapsed_seconds)
        self._apply_style()

    def _build_ui(self, elapsed: int):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Left color accent bar
        self._bar = QWidget()
        self._bar.setFixedWidth(5)
        outer.addWidget(self._bar)

        # Main row
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        row = QHBoxLayout(content)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(16)

        # Project name + total time
        info = QVBoxLayout()
        info.setSpacing(3)
        info.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._name_lbl = QLabel(self._name)
        self._name_lbl.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        info.addWidget(self._name_lbl)

        self._total_lbl = QLabel("Total: " + fmt_seconds(self._total))
        self._total_lbl.setStyleSheet(
            f"font-size: 11px; color: {TEXT_MUTED}; "
            f"border: none; background: transparent;"
        )
        info.addWidget(self._total_lbl)

        row.addLayout(info, 1)

        # Live elapsed clock (center)
        self._elapsed_lbl = QLabel(fmt_seconds(elapsed) if self._is_active else "")
        self._elapsed_lbl.setFixedWidth(108)
        self._elapsed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._elapsed_lbl.setStyleSheet(f"""
            font-family: {FONT_MONO};
            font-size: 24px;
            font-weight: 700;
            color: {ACCENT_GREEN if self._is_active else 'transparent'};
            border: none;
            background: transparent;
        """)
        row.addWidget(self._elapsed_lbl)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._btn_rename = self._small_btn("Rename")
        self._btn_rename.clicked.connect(
            lambda checked=False: self.rename_clicked.emit(self.project_id)
        )
        btn_row.addWidget(self._btn_rename)

        self._btn_delete = self._small_btn("Delete", danger=True)
        self._btn_delete.clicked.connect(
            lambda checked=False: self.delete_clicked.emit(self.project_id)
        )
        btn_row.addWidget(self._btn_delete)

        btn_row.addSpacing(4)

        # The main Start / Stop button
        self._btn_toggle = QPushButton()
        self._btn_toggle.setFixedSize(108, 44)
        self._btn_toggle.clicked.connect(
            lambda checked=False: self._on_toggle()
        )
        btn_row.addWidget(self._btn_toggle)
        self._refresh_toggle()

        row.addLayout(btn_row)
        outer.addWidget(content, 1)

    def _small_btn(self, text: str, danger: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(32)
        if danger:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {ACCENT_RED};
                    border: 1px solid {ACCENT_RED}44;
                    border-radius: 6px;
                    padding: 0 14px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {ACCENT_RED_LIGHT};
                    border-color: {ACCENT_RED};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SECONDARY};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    padding: 0 14px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                    color: {TEXT_PRIMARY};
                    border-color: {TEXT_MUTED};
                }}
            """)
        return btn

    def _on_toggle(self):
        if self._is_active:
            self.stop_clicked.emit(self.project_id)
        else:
            self.start_clicked.emit(self.project_id)

    def _refresh_toggle(self):
        if self._is_active:
            self._btn_toggle.setText("⏹  Stop")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT_RED};
                    color: white;
                    border: none;
                    border-radius: {RADIUS_SM}px;
                    font-size: 14px;
                    font-weight: 700;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{ background: #DC2626; }}
                QPushButton:pressed {{ background: #B91C1C; }}
            """)
        else:
            self._btn_toggle.setText("▶  Start")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT};
                    color: white;
                    border: none;
                    border-radius: {RADIUS_SM}px;
                    font-size: 14px;
                    font-weight: 700;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{ background: {ACCENT_DARK}; }}
                QPushButton:pressed {{ background: #C2410C; }}
            """)

    def _apply_style(self):
        if self._is_active:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {ACCENT_GREEN_LIGHT};
                    border-radius: {RADIUS}px;
                    border: 1.5px solid {ACCENT_GREEN}55;
                }}
            """)
            self._bar.setStyleSheet(
                f"background: {ACCENT_GREEN}; "
                f"border-top-left-radius: {RADIUS}px; "
                f"border-bottom-left-radius: {RADIUS}px; border: none;"
            )
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {BG_SURFACE};
                    border-radius: {RADIUS}px;
                    border: 1px solid {BORDER};
                }}
            """)
            self._bar.setStyleSheet(
                f"background: {self._color}; "
                f"border-top-left-radius: {RADIUS}px; "
                f"border-bottom-left-radius: {RADIUS}px; border: none;"
            )

    def set_state(self, state: str):
        self._is_active = (state == "running")
        self._apply_style()
        self._refresh_toggle()

        if not self._is_active:
            self._elapsed_lbl.setText("")
            self._elapsed_lbl.setStyleSheet(
                f"font-family: {FONT_MONO}; font-size: 24px; font-weight: 700; "
                f"color: transparent; border: none; background: transparent;"
            )
            self._total_lbl.setText("Total: " + fmt_seconds(self._total))

    def update_elapsed(self, elapsed: int):
        self._elapsed_lbl.setText(fmt_seconds(elapsed))
        self._elapsed_lbl.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: 24px; font-weight: 700; "
            f"color: {ACCENT_GREEN}; border: none; background: transparent;"
        )
        self._total_lbl.setText("Total: " + fmt_seconds(self._total + elapsed))