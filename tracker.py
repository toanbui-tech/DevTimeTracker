"""
tracker.py — TimeTracker service layer
Owns the timer state machine and coordinates DB operations.
"""

import csv
from datetime import datetime
from typing import Optional

from database import (
    get_connection, init_db,
    create_project, get_all_projects, rename_project,
    delete_project, update_project_color,
    start_session, stop_session, get_active_session,
    get_sessions, get_dashboard_stats, get_project_total_seconds,
    clear_state,
)


def fmt_seconds(total: int) -> str:
    """Convert integer seconds to HH:MM:SS string."""
    total = max(0, int(total))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class TimeTracker:
    def __init__(self, db_path: str = None):
        self.conn = get_connection(db_path)
        init_db(self.conn)

        self._active_session_id: Optional[int] = None
        self._active_project_id: Optional[int] = None
        self._session_start: Optional[datetime] = None
        self._recovered = False

        self._restore_active_session()

    def _restore_active_session(self) -> None:
        session = get_active_session(self.conn)
        if session:
            self._active_session_id = session["id"]
            self._active_project_id = session["project_id"]
            self._session_start = datetime.fromisoformat(session["start_time"])
            self._recovered = True

    @property
    def recovered(self) -> bool:
        return self._recovered

    def acknowledge_recovery(self) -> None:
        self._recovered = False

    # ── Projects ───────────────────────────────────────────────────────────────

    def add_project(self, name: str, color: str = "#4A9EFF") -> int:
        return create_project(self.conn, name, color)

    def list_projects(self) -> list:
        return get_all_projects(self.conn)

    def rename_project(self, project_id: int, new_name: str) -> None:
        rename_project(self.conn, project_id, new_name)

    def set_project_color(self, project_id: int, color: str) -> None:
        update_project_color(self.conn, project_id, color)

    def remove_project(self, project_id: int) -> None:
        if self._active_project_id == project_id:
            raise ValueError("Cannot delete a project with a running timer.")
        delete_project(self.conn, project_id)

    # ── Timer ──────────────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._active_session_id is not None

    @property
    def active_project_id(self) -> Optional[int]:
        return self._active_project_id

    def elapsed_seconds(self) -> int:
        if not self._session_start:
            return 0
        return int((datetime.utcnow() - self._session_start).total_seconds())

    def start_timer(self, project_id: int) -> None:
        if self.is_running:
            self.stop_timer()
        self._active_session_id = start_session(self.conn, project_id)
        self._active_project_id = project_id
        self._session_start = datetime.utcnow()

    def stop_timer(self) -> int:
        if not self.is_running:
            return 0
        duration = stop_session(self.conn, self._active_session_id)
        self._active_session_id = None
        self._active_project_id = None
        self._session_start = None
        return duration

    def discard_timer(self) -> None:
        if not self.is_running:
            return
        self.conn.execute(
            "UPDATE sessions SET end_time = ?, duration = 0 WHERE id = ?",
            (datetime.utcnow().isoformat(), self._active_session_id),
        )
        self.conn.commit()
        clear_state(self.conn, "active_session_id")
        clear_state(self.conn, "active_project_id")
        self._active_session_id = None
        self._active_project_id = None
        self._session_start = None

    # ── Queries ────────────────────────────────────────────────────────────────

    def get_project_total(self, project_id: int) -> int:
        total = get_project_total_seconds(self.conn, project_id)
        if self.is_running and self._active_project_id == project_id:
            total += self.elapsed_seconds()
        return total

    def get_dashboard(self) -> list:
        stats = get_dashboard_stats(self.conn)
        if self.is_running:
            live = self.elapsed_seconds()
            for row in stats:
                if row["id"] == self._active_project_id:
                    row["today"] += live
                    row["week"]  += live
                    row["month"] += live
                    row["total"] += live
        return stats

    def get_history(self, project_id=None, date_from=None, date_to=None) -> list:
        return get_sessions(self.conn, project_id, date_from, date_to)

    def export_csv(self, path: str, project_id=None,
                   date_from=None, date_to=None) -> int:
        sessions = self.get_history(project_id, date_from, date_to)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Session ID", "Project", "Start Time", "End Time",
                "Duration (s)", "Duration (HH:MM:SS)", "Note"
            ])
            for s in sessions:
                writer.writerow([
                    s["id"], s["project_name"],
                    s["start_time"], s["end_time"] or "",
                    s["duration"], fmt_seconds(s["duration"]),
                    s["note"] or "",
                ])
        return len(sessions)

    def close(self) -> None:
        self.conn.close()