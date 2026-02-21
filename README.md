# ⏱ TimeTracker

A professional, fully offline desktop time tracker for developers and freelancers. Track time across multiple projects — no cloud, no account, no internet required.

---

## Requirements

- Python 3.10 or later
- Windows / macOS / Linux

---

## Installation & Running

### Step 1 — Install dependencies

```bash
pip install PyQt6
```

### Step 2 — Run

```bash
cd your-folder
python main.py
```

---

## File Structure

All files in **one flat folder** — no subfolders needed:

```
your-folder/
├── main.py             ← Entry point — run this
├── main_window.py      ← App window, sidebar wiring
├── sidebar.py          ← Left navigation sidebar
├── style.py            ← All colors, fonts, stylesheet
├── widgets.py          ← Reusable custom widgets & charts
├── tab_timer.py        ← Timer screen (project cards)
├── tab_dashboard.py    ← Dashboard screen (stats & charts)
├── tab_history.py      ← History screen (session log)
├── tab_projects.py     ← Projects screen (manage projects)
├── database.py         ← SQLite schema & all queries
└── tracker.py          ← Timer logic & business layer
```

---

## Where Data Is Stored

```
Windows:       C:\Users\<you>\.timetracker\timetracker.db
macOS/Linux:   ~/.timetracker/timetracker.db
```

- Data **persists after shutdown** — nothing is ever lost
- **Backup**: copy `timetracker.db` anywhere
- **Reset**: delete `timetracker.db`

---

## How to Use

### Navigation
The app has a **sidebar on the left** with 4 sections:
- **Timer** — track time on your projects
- **Dashboard** — view stats and charts
- **History** — browse all past sessions
- **Projects** — manage your project list

---

### Timer Screen

This is your main screen. Each project appears as a **full-width card**:

```
┌─────────────────────────────────────────────────────────────────┐
│ ▌ Website Redesign        Total: 04:22:10   [Rename] [Delete] [▶ Start] │
└─────────────────────────────────────────────────────────────────┘
```

**To start tracking:**
→ Click the orange **▶ Start** button on any project card

**While a timer is running**, the card turns green and shows a live clock:

```
┌─────────────────────────────────────────────────────────────────┐
│ ▌ Website Redesign  (green)   01:23:45   [Rename] [Delete] [⏹ Stop] │
└─────────────────────────────────────────────────────────────────┘
```

**To stop:**
→ Click the red **⏹ Stop** button

**Rules:**
- Only **one timer runs at a time** — starting a new project auto-stops the current one
- Time **accumulates across days** — picking up a project tomorrow adds to its total

**To create a project:**
→ Click **+ New Project** button (top right of Timer screen)

---

### Dashboard Screen

Shows time aggregated across all projects:

- **4 summary cards**: Today / This Week / This Month / All Time
- **7-day bar chart**: hours worked per day for the last week
- **Project donut chart**: proportion of time per project
- **Project breakdown table**: Today / Week / Month / Total per project

All stats update live every second while a timer is running.

---

### History Screen

Full log of every work session:

| Column | Description |
|--------|-------------|
| Project | Which project |
| Date | Day of the session |
| Started | Start time |
| Finished | End time |
| Duration | Length of session |

**Filters:**
- Filter by **project** (dropdown)
- Filter by **date range** (From / To date pickers)
- Quick buttons: **Today / 7d / 30d / All**

**Export:**
→ Click **↓ Export CSV** to save a spreadsheet of all sessions

---

### Projects Screen

Manage your project list:

- **Color swatch** (click to change color via color picker)
- **Rename** button — change the project name
- **Delete** button — removes the project (sessions kept in History)
- Shows total tracked time per project

---

## Crash Recovery

If the app closes while a timer is running (power cut, crash, force-quit):

1. Reopen the app
2. A **"Session Recovered"** dialog appears
3. The timer resumes from the original start time
4. Click **⏹ Stop** to save the session normally

---

## Export to CSV

1. Go to **History**
2. Set your filters (or leave as All)
3. Click **↓ Export CSV**
4. Choose save location

CSV columns: `Session ID, Project, Start Time, End Time, Duration (s), Duration (HH:MM:SS), Note`

---

## Customizing Colors

Open `style.py` and edit the top section:

```python
ACCENT            = "#F97316"   # Orange — primary buttons, active state
ACCENT_GREEN      = "#22C55E"   # Green — running timer
ACCENT_RED        = "#EF4444"   # Red — stop button, delete
BG_BASE           = "#F7F5F2"   # Warm off-white background
BG_SURFACE        = "#FFFFFF"   # Card backgrounds
BG_SIDEBAR        = "#1C1917"   # Dark sidebar

PROJECT_COLORS = [...]          # Default colors cycled for new projects
```

Restart the app to apply changes.

---

## Database Schema

```sql
-- Projects
CREATE TABLE projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    color      TEXT    NOT NULL DEFAULT '#F97316',
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    archived   INTEGER NOT NULL DEFAULT 0   -- soft delete
);

-- Work sessions — one row per Start→Stop
CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    start_time TEXT    NOT NULL,            -- ISO-8601 UTC
    end_time   TEXT,                        -- NULL = currently running
    duration   INTEGER NOT NULL DEFAULT 0, -- seconds
    note       TEXT
);

-- Crash recovery store
CREATE TABLE app_state (
    key   TEXT PRIMARY KEY,
    value TEXT
);
```

---

## Build a Standalone .exe (Windows)

No Python needed to run the output file.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DevTimeTracker main.py
```

With a custom icon (`.ico` file must exist in the folder):

```bash
pyinstaller --onefile --windowed --name DevTimeTracker --icon=icon.ico main.py
```

Output: `dist\DevTimeTracker.exe` — double-click to run.

> **Note:** First launch may take 5–10 seconds as Windows extracts the bundle. This is normal.

> **Windows Defender warning:** Click "More info" → "Run anyway". This is expected for self-built executables.

---

## Troubleshooting

**`ImportError: cannot import name 'X' from 'style'`**
→ You have a mix of old and new files. Replace **all** `.py` files with the latest version together.

**`ModuleNotFoundError: No module named 'PyQt6'`**
```bash
pip install PyQt6
```

**App won't start — terminal shows no error**
→ Run from inside the correct folder:
```bash
cd C:\Users\you\Desktop\DevTimeTracker
python main.py
```

**Find the database on Windows**
→ Open File Explorer → type `%USERPROFILE%\.timetracker` in the address bar → Enter

**Want to inspect the database**
→ Download [DB Browser for SQLite](https://sqlitebrowser.org/) (free) and open `timetracker.db`