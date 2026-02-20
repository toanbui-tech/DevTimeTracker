# ⏱ TimeTracker

A lightweight, fully offline desktop time-tracking application for developers and freelancers who work across multiple projects.

---

## Technology Choice: Python + PyQt6 + SQLite

### Why not Electron or Tauri?

| Criterion          | Electron         | Tauri            | **Python + PyQt6** |
|--------------------|------------------|------------------|--------------------|
| Startup time       | 2–4 seconds      | ~1 second        | **~0.5 seconds**   |
| RAM at idle        | ~180 MB          | ~30 MB           | **~25 MB**         |
| Install complexity | Node + npm       | Rust + Node      | **pip install**    |
| Single executable  | Moderate         | Good             | **pyinstaller**    |
| Native feel        | Chrome shell     | WebView          | **True native**    |
| SQLite support     | node-sqlite3     | rusqlite         | **stdlib**         |

**Python + PyQt6 wins** for a local utility: zero web stack, SQLite is in the standard library, and the executable is small enough to distribute as a single file.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   main.py (entry point)              │
│         QApplication → MainWindow                    │
└─────────────────┬───────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │   MainWindow    │  Tab bar + status bar
         └────┬────┬───┬───┘
              │    │   │  
     ┌────────▼┐ ┌─▼──▼─┐ ┌──────────┐ ┌──────────┐
     │TimerTab │ │Dash  │ │HistoryTab│ │ProjectsTab│
     │(live    │ │board │ │(sessions │ │(CRUD +   │
     │ clock)  │ │Tab   │ │ filter)  │ │ colors)  │
     └────┬────┘ └──────┘ └──────────┘ └──────────┘
          │
          │  calls
          ▼
┌─────────────────────────────────────────────────────┐
│              core/tracker.py  (TimeTracker)          │
│   Timer state machine + business logic               │
│   - start_timer / stop_timer / discard_timer         │
│   - elapsed_seconds() (live)                         │
│   - get_dashboard() / get_history() / export_csv()   │
└─────────────────┬───────────────────────────────────┘
                  │  calls
                  ▼
┌─────────────────────────────────────────────────────┐
│              core/database.py  (SQLite)              │
│   All schema creation + raw SQL queries              │
│   - init_db() / create_project() / start_session()  │
│   - get_active_session() (crash recovery)            │
│   - get_dashboard_stats() / get_sessions()           │
└─────────────────────────────────────────────────────┘
                  │  persists to
                  ▼
         ~/.timetracker/timetracker.db
```

---

## Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    color       TEXT    NOT NULL DEFAULT '#4A9EFF',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    archived    INTEGER NOT NULL DEFAULT 0   -- soft delete
);

-- Work sessions table
-- One row per contiguous work block (start→stop pair)
CREATE TABLE sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    start_time  TEXT    NOT NULL,       -- ISO-8601 UTC
    end_time    TEXT,                   -- NULL = currently running
    duration    INTEGER NOT NULL DEFAULT 0,  -- seconds
    note        TEXT
);

-- App state key-value store (crash recovery)
CREATE TABLE app_state (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- Indices
CREATE INDEX idx_sessions_project ON sessions(project_id);
CREATE INDEX idx_sessions_start   ON sessions(start_time);
```

**Key design decisions:**

- `end_time = NULL` marks an active session — used for crash recovery
- `duration` is stored redundantly (computed at stop time) for fast aggregation
- `archived = 1` for soft-deleted projects preserves history
- `app_state` stores `active_session_id` / `active_project_id` — if the app crashes, these tell us exactly which session to resume

---

## Project Structure

```
timetracker/
├── main.py               # Entry point (QApplication + MainWindow)
├── requirements.txt      # Python dependencies
├── build.spec            # PyInstaller config for executable build
│
├── core/
│   ├── __init__.py
│   ├── database.py       # All SQLite schema + queries (no business logic)
│   └── tracker.py        # TimeTracker service class (timer state machine)
│
└── ui/
    ├── __init__.py
    ├── style.py           # Design tokens + Qt stylesheet (theme here)
    ├── widgets.py         # Reusable custom widgets (StatBox, ProjectListItem…)
    ├── main_window.py     # MainWindow: tab bar + status bar
    ├── tab_timer.py       # Tab 1: live clock + project list
    ├── tab_dashboard.py   # Tab 2: per-project time aggregates
    ├── tab_history.py     # Tab 3: filterable session log + CSV export
    └── tab_projects.py    # Tab 4: project CRUD + color picker
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or later  
- pip

### 1. Clone / download the project

```bash
git clone <repo-url>   # or download and unzip
cd timetracker
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

Data is stored at `~/.timetracker/timetracker.db` (created automatically on first run).

---

## How to Use

### Creating a project
1. Go to the **Timer** tab
2. Click **+ New Project** in the top-right of the project list
3. Enter a name and press OK

### Starting / stopping a timer
- Hover over a project row → click the **▶** button to start its timer
- The big clock starts counting in the top panel
- Click **Stop Timer** to stop and save the session

### Resuming work
Simply start the timer for the same project the next day — time accumulates automatically.

### Viewing stats
- **Dashboard** tab: today / this week / this month / all-time per project
- **History** tab: every session, filterable by project and date range

### Exporting data
History tab → click **↓ Export CSV** → choose a save location

### Crash recovery
If the app closes while a timer is running (crash or force-quit), the next launch will automatically resume the session and show a notification.

---

## Building a Standalone Executable

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build

```bash
pyinstaller build.spec
```

The executable will be in `dist/TimeTracker` (Linux/macOS) or `dist/TimeTracker.exe` (Windows).

### macOS App Bundle

Running PyInstaller on macOS produces `dist/TimeTracker.app` — a proper `.app` bundle you can move to `/Applications`.

### Windows

The output is a single `.exe` with no installer required.

---

## Configuration & Theming

All colors, fonts, and spacing are defined in `ui/style.py`:

```python
# Change the accent color across the entire app
ACCENT = "#4A9EFF"

# Add more project colors
PROJECT_COLORS = ["#4A9EFF", "#3DD68C", ...]
```

---

## Future Improvement Suggestions

### Near-term
- **Idle detection**: Use `QTimer` + system idle APIs (`xprintidle` on Linux, `GetLastInputInfo` on Windows, `ioreg` on macOS) — prompt user to discard idle time after N minutes of inactivity
- **System tray**: Keep app running in background, show running timer in tray icon
- **Keyboard shortcuts**: `⌘R` to start/stop, `⌘N` for new project

### Medium-term  
- **Notes per session**: Add a text note field when stopping a timer
- **Goals / targets**: Set a daily/weekly hour goal per project with progress bars
- **Tags**: Tag sessions for cross-project reporting (e.g., "meetings", "deep work")
- **Multiple CSV formats**: Week summary, invoice-ready, Toggl-compatible export

### Long-term
- **Charts**: Weekly bar charts using `pyqtgraph` or `matplotlib`
- **Billing rates**: Attach hourly rates to projects, auto-calculate invoice amounts
- **Sync (optional)**: Optional encrypted sync via Dropbox/iCloud file sharing
- **Plugin API**: Let users write Python scripts that react to timer events (e.g., post to Slack)

---

## Troubleshooting

**App won't start on macOS ("unidentified developer")**  
```bash
xattr -cr TimeTracker.app
```

**PyQt6 install fails on Linux**  
```bash
sudo apt install python3-pyqt6
# or
pip install PyQt6 --pre
```

**Database location**  
```
~/.timetracker/timetracker.db
```
Back this file up to preserve all your time data.

**Reset all data**  
```bash
rm ~/.timetracker/timetracker.db
```
