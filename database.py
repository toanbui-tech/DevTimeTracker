"""
database.py — SQLite persistence layer for TimeTracker
All schema creation and raw DB operations live here.
"""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path


def get_db_path() -> str:
    data_dir = Path.home() / ".timetracker"
    data_dir.mkdir(exist_ok=True)
    return str(data_dir / "timetracker.db")


def get_connection(db_path: str = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            color       TEXT    NOT NULL DEFAULT '#4A9EFF',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            archived    INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            start_time  TEXT    NOT NULL,
            end_time    TEXT,
            duration    INTEGER NOT NULL DEFAULT 0,
            note        TEXT
        );

        CREATE TABLE IF NOT EXISTS app_state (
            key   TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_start   ON sessions(start_time);
    """)
    conn.commit()


# ── Projects ───────────────────────────────────────────────────────────────────

def create_project(conn, name: str, color: str = "#4A9EFF") -> int:
    cur = conn.execute(
        "INSERT INTO projects (name, color) VALUES (?, ?)", (name.strip(), color)
    )
    conn.commit()
    return cur.lastrowid


def get_all_projects(conn) -> list:
    return conn.execute(
        "SELECT * FROM projects WHERE archived = 0 ORDER BY name"
    ).fetchall()


def rename_project(conn, project_id: int, new_name: str) -> None:
    conn.execute("UPDATE projects SET name = ? WHERE id = ?", (new_name.strip(), project_id))
    conn.commit()


def delete_project(conn, project_id: int) -> None:
    conn.execute("UPDATE projects SET archived = 1 WHERE id = ?", (project_id,))
    conn.commit()


def update_project_color(conn, project_id: int, color: str) -> None:
    conn.execute("UPDATE projects SET color = ? WHERE id = ?", (color, project_id))
    conn.commit()


# ── Sessions ───────────────────────────────────────────────────────────────────

def start_session(conn, project_id: int) -> int:
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        "INSERT INTO sessions (project_id, start_time) VALUES (?, ?)", (project_id, now)
    )
    conn.commit()
    set_state(conn, "active_session_id", str(cur.lastrowid))
    set_state(conn, "active_project_id", str(project_id))
    return cur.lastrowid


def stop_session(conn, session_id: int) -> int:
    row = conn.execute(
        "SELECT start_time FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if not row:
        return 0
    start = datetime.fromisoformat(row["start_time"])
    end = datetime.utcnow()
    duration = int((end - start).total_seconds())
    conn.execute(
        "UPDATE sessions SET end_time = ?, duration = ? WHERE id = ?",
        (end.isoformat(), duration, session_id),
    )
    conn.commit()
    clear_state(conn, "active_session_id")
    clear_state(conn, "active_project_id")
    return duration


def get_active_session(conn):
    session_id = get_state(conn, "active_session_id")
    if not session_id:
        return None
    row = conn.execute(
        "SELECT s.*, p.name as project_name FROM sessions s "
        "JOIN projects p ON p.id = s.project_id "
        "WHERE s.id = ? AND s.end_time IS NULL",
        (int(session_id),),
    ).fetchone()
    return dict(row) if row else None


def get_sessions(conn, project_id=None, date_from=None, date_to=None) -> list:
    sql = (
        "SELECT s.*, p.name as project_name, p.color as project_color "
        "FROM sessions s JOIN projects p ON p.id = s.project_id "
        "WHERE s.end_time IS NOT NULL "
    )
    params = []
    if project_id:
        sql += "AND s.project_id = ? "
        params.append(project_id)
    if date_from:
        sql += "AND s.start_time >= ? "
        params.append(date_from)
    if date_to:
        sql += "AND s.start_time <= ? "
        params.append(date_to + "T23:59:59")
    sql += "ORDER BY s.start_time DESC"
    return conn.execute(sql, params).fetchall()


# ── Aggregates ─────────────────────────────────────────────────────────────────

def get_project_total_seconds(conn, project_id: int) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(duration), 0) as total FROM sessions "
        "WHERE project_id = ? AND end_time IS NOT NULL", (project_id,)
    ).fetchone()
    return row["total"]


def get_project_seconds_for_range(conn, project_id: int, start: str, end: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(duration), 0) as total FROM sessions "
        "WHERE project_id = ? AND end_time IS NOT NULL "
        "AND start_time >= ? AND start_time <= ?",
        (project_id, start, end),
    ).fetchone()
    return row["total"]


def get_dashboard_stats(conn) -> list:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    stats = []
    for p in get_all_projects(conn):
        pid = p["id"]
        stats.append({
            "id":    pid,
            "name":  p["name"],
            "color": p["color"],
            "today": get_project_seconds_for_range(
                conn, pid,
                today.isoformat() + "T00:00:00",
                today.isoformat() + "T23:59:59"),
            "week":  get_project_seconds_for_range(
                conn, pid,
                week_start.isoformat() + "T00:00:00",
                today.isoformat() + "T23:59:59"),
            "month": get_project_seconds_for_range(
                conn, pid,
                month_start.isoformat() + "T00:00:00",
                today.isoformat() + "T23:59:59"),
            "total": get_project_total_seconds(conn, pid),
        })
    return stats


# ── App state KV ───────────────────────────────────────────────────────────────

def set_state(conn, key: str, value: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO app_state (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()


def get_state(conn, key: str):
    row = conn.execute(
        "SELECT value FROM app_state WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else None


def clear_state(conn, key: str) -> None:
    conn.execute("DELETE FROM app_state WHERE key = ?", (key,))
    conn.commit()