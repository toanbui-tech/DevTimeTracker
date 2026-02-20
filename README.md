# ⏱ TimeTracker

Ứng dụng desktop theo dõi thời gian làm việc theo từng dự án. Chạy hoàn toàn offline, không cần internet, dữ liệu lưu trên máy của bạn.

---

## Yêu cầu hệ thống

- Python 3.10 trở lên
- Windows / macOS / Linux

---

## Cài đặt & Chạy

### Bước 1 — Cài thư viện

```bash
pip install PyQt6
```

### Bước 2 — Chạy ứng dụng

```bash
python main.py
```

> Chạy lệnh này **trong thư mục chứa các file `.py`**.

---

## Cấu trúc thư mục

Tất cả file nằm **cùng một cấp**, không có subfolder:

```
your-folder/
├── main.py            ← Điểm khởi động, chạy file này
├── main_window.py     ← Cửa sổ chính, tab bar, status bar
├── database.py        ← Toàn bộ SQLite schema và truy vấn
├── tracker.py         ← Logic đồng hồ bấm giờ, quản lý session
├── style.py           ← Màu sắc, font, stylesheet toàn app
├── widgets.py         ← Các widget tái sử dụng (StatBox, ProjectListItem…)
├── tab_timer.py       ← Tab Timer: đồng hồ trực tiếp + danh sách project
├── tab_dashboard.py   ← Tab Dashboard: thống kê theo project
├── tab_history.py     ← Tab History: lịch sử session + xuất CSV
└── tab_projects.py    ← Tab Projects: quản lý project (thêm/sửa/xóa)
```

---

## Dữ liệu được lưu ở đâu?

Dữ liệu lưu tự động vào file SQLite trên máy bạn:

| Hệ điều hành | Đường dẫn |
|---|---|
| Windows | `C:\Users\<tên>\\.timetracker\timetracker.db` |
| macOS / Linux | `~/.timetracker/timetracker.db` |

- Dữ liệu **giữ nguyên sau khi tắt máy hoặc khởi động lại**
- Để **backup**, chỉ cần copy file `timetracker.db`
- Để **xóa toàn bộ dữ liệu**, xóa file đó đi

---

## Cách sử dụng

### Tạo project
1. Mở tab **Timer** hoặc **Projects**
2. Bấm **+ New Project**
3. Nhập tên → OK

### Bắt đầu bấm giờ
- Trong tab **Timer**, hover chuột vào tên project → bấm **▶**
- Đồng hồ lớn bắt đầu chạy, có chấm xanh nhấp nháy

### Dừng timer
- Bấm nút **Stop Timer** ở panel trên cùng

### Hôm sau tiếp tục
- Bấm **▶** cho cùng project đó — thời gian tự động cộng dồn, không bị reset

### Chỉ một timer chạy tại một thời điểm
- Nếu bấm start project khác trong khi đang chạy → timer cũ tự động dừng và lưu lại

---

## Các tab

### Timer
- Đồng hồ đếm thời gian thực (cập nhật mỗi giây)
- Danh sách tất cả project kèm tổng thời gian
- Hover vào project để thấy nút ▶ Rename ✕

### Dashboard
- Tổng thời gian toàn bộ: **Hôm nay / Tuần này / Tháng này / Tất cả**
- Bảng chi tiết theo từng project
- Tự động cập nhật mỗi giây khi có timer đang chạy

### History
- Toàn bộ lịch sử session theo thứ tự mới nhất
- Lọc theo **project** và **khoảng ngày**
- Quick filter: Today / 7 days / 30 days / All
- Xuất ra file **CSV** để dùng ngoài app

### Projects
- Xem danh sách project kèm tổng thời gian
- **Đổi màu** project: bấm vào ô tròn màu
- **Rename** / **Delete** trực tiếp
- Project bị xóa là xóa mềm — lịch sử session vẫn còn trong History

---

## Tự phục hồi khi tắt máy đột ngột

Nếu bạn tắt máy hoặc app bị crash **trong khi timer đang chạy**:

- Lần mở app tiếp theo sẽ hiện thông báo **"Session Recovered"**
- Timer tự động tiếp tục tính từ lúc bắt đầu ban đầu
- Bấm **Stop Timer** bình thường để lưu session

---

## Xuất dữ liệu CSV

1. Vào tab **History**
2. Chọn project và khoảng ngày muốn xuất (hoặc để All)
3. Bấm **↓ Export CSV**
4. Chọn nơi lưu file

File CSV có các cột: `Session ID, Project, Start Time, End Time, Duration (s), Duration (HH:MM:SS), Note`

---

## Đổi giao diện / màu sắc

Mở file `style.py` và chỉnh các biến ở đầu file:

```python
ACCENT     = "#4A9EFF"   # Màu chủ đạo (xanh dương)
ACCENT_HOT = "#FF5C5C"   # Màu Stop / xóa (đỏ)
ACCENT_OK  = "#3DD68C"   # Màu đang chạy (xanh lá)
BG_DARK    = "#0F1117"   # Nền chính
BG_CARD    = "#1A1D27"   # Nền card/panel
```

---

## Database Schema

```sql
-- Danh sách project
CREATE TABLE projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    color      TEXT    NOT NULL DEFAULT '#4A9EFF',
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    archived   INTEGER NOT NULL DEFAULT 0  -- xóa mềm
);

-- Mỗi lần bấm Start→Stop là một session
CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    start_time TEXT    NOT NULL,       -- ISO-8601 UTC
    end_time   TEXT,                   -- NULL = đang chạy
    duration   INTEGER NOT NULL DEFAULT 0,  -- giây
    note       TEXT
);

-- Lưu trạng thái app (dùng cho crash recovery)
CREATE TABLE app_state (
    key   TEXT PRIMARY KEY,
    value TEXT
);
```

---

## Build thành file .exe (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name TimeTracker main.py
```

File `.exe` sẽ xuất hiện trong thư mục `dist/`.

---

## Gỡ lỗi thường gặp

**Lỗi `No module named 'core'` hoặc `No module named 'ui'`**
→ Bạn đang dùng bản code cũ có subfolder. Hãy dùng bản mới nhất — tất cả file nằm cùng một cấp.

**Lỗi `No module named 'PyQt6'`**
```bash
pip install PyQt6
```

**App không khởi động trên Windows**
→ Chạy trong Git Bash hoặc Command Prompt, đứng đúng thư mục chứa `main.py`:
```bash
cd path\to\your-folder
python main.py
```

**Muốn xem database bằng tay**
→ Dùng [DB Browser for SQLite](https://sqlitebrowser.org/) mở file `~/.timetracker/timetracker.db`