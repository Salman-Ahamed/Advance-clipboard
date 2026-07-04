# Clipboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://windows.com)

A modern, dark-themed clipboard manager for Windows. Auto-captures clipboard history, pin favorites, paste or type (character-by-character), all from a system tray app with a global hotkey.

## Features

### Core

- **Auto Clipboard Capture** — Monitors clipboard changes via Win32 `GetClipboardSequenceNumber()` and stores history automatically. Every real Ctrl+C is detected — even recopying the same text after deletion.
- **Persistent History** — All items saved to `clipboard_history.json`, survives restarts. Capped at **500 items** (oldest trimmed automatically).
- **Pin / Favorite** — Star items to protect them from "Clear Unpinned". Pinned items have a purple left accent bar.
- **Dual Paste Modes** — **Paste** (Ctrl+V simulation with `smart_paste`) or **Type** (character-by-character via `keyboard.write()`). Type is the default mode.
- **Double-click to Execute** — Double-click any card to paste or type (whichever mode is currently active).
- **Global Hotkey** — `Ctrl+Shift+Space` to paste/type selected item from any app.

### Search & Filter

- **Search History** — Real-time filter with "🔍 Search history..." placeholder. Press `Ctrl+F` to focus.
- **Pinned-only Filter** — Click **★ Only** to show only pinned items.

### UI

- **Dark Theme** — Purple accent (#7c3aed) on deep dark (#0d0d14). Card backgrounds (#16162a) with hover (#1c1c35) and selected (#22224a) states.
- **Custom Scrollbar** — Dark purple-themed `ttk.Scrollbar` with `clam` theme.
- **Canvas + Embedded Frame** — Custom card-based UI (not a Listbox). Each card has a left accent bar, pin star, text, and delete button.
- **Auto-select First Item** — When the list refreshes (search, filter, new item), the first item is automatically selected.
- **Auto-scroll to Selection** — After rebuild, the view scrolls to keep the selected card visible.
- **Status Bar** — Shows hotkey hint, total item count, and pinned count.

### System Tray

- **System Tray Icon** — Custom-drawn purple clipboard icon using Pillow. Right-click for menu.
- **Show/Hide Window** — From tray menu.
- **Pause/Resume Monitoring** — Toggle clipboard capture on/off from tray menu.
- **Quit** — Exit the application completely.

### Window Management

- **Minimum Window Size** — 600x400 enforced.
- **Geometry Persistence** — Window position/size saved to `settings.json` on close and restored on launch.
- **Auto-migration** — Old 800x600 settings are silently upgraded to 600x400.
- **Focus Restoration** — Before paste/type, Win32 `SwitchToThisWindow` restores focus to the previous app so the paste lands in the correct input field.

### Paste vs Type Details

| Mode | Behavior |
|---|---|
| **📋 Paste** | Uses `smart_paste()` — pauses clipboard monitor, copies text, waits 50ms, sends `Ctrl+V`, waits 100ms, resumes monitor. This prevents the paste action from being re-captured as new history. |
| **⌨ Type** (default) | Uses `keyboard.write()` to type text character-by-character. No clipboard modification. |

- **Type mode** is ideal for terminals, remote desktop, SSH sessions, or web inputs that block `Ctrl+V`.
- Both modes save to `settings.json` and restore on next launch.

### Persistence & Storage

| File | Purpose |
|---|---|
| `clipboard_history.json` | History items — each has `value`, `pinned` (bool), `timestamp` (Unix epoch), `date` (ISO 8601) |
| `settings.json` | `window_geometry`, `paste_mode`, `theme`, `max_history`, `window_hotkey` |
| `crash_log.txt` | Auto-generated on unexpected crash with traceback |

## Window Layout

```
┌──────────────────────────────────────────────────────────┐
│ ☰ Clipboard  [📋 Paste] [⌨ Type]   [★ Only] [🔍 ...]   │
├──────────────────────────────────────────────────────────┤
│  ▎☆ hello world                               🗑        │
│  ▎  2 min ago                                            │
│                                                          │
│  ▎★ some pinned text                        🗑           │
│  ▎  1 hour ago                                           │
│                                                          │
│  ▎☆ another item                             🗑          │
│  ▎  3 hours ago                                           │
├──────────────────────────────────────────────────────────┤
│ Ctrl+Shift+Space: Paste  |  Total: 24  |  Pinned: 2     │
│ [☆ Pin] [✕ Delete] [🗑 Clear Unpinned]                  │
└──────────────────────────────────────────────────────────┘
  ▎ = left accent bar (purple when pinned/selected)
```

### Card Anatomy

```
┌──────────────────────────────────┬─────┐
│ ▎ ☆ Text value            🗑     │     │
│ ▎   2 min ago                    │     │
└──────────────────────────────────┴─────┘
 ↑        ↑              ↑          ↑
 accent   pin star      delete     scrollbar
 bar      (☆/★)        (🗑)
```

- **Accent bar** — 4px purple (#7c3aed) when pinned or selected; dark border (#1e1e3a) otherwise
- **Pin star** — ☆ (not pinned) / ★ (pinned, yellow #f59e0b)
- **Delete** — 🗑 trash icon (#ef4444 red). Pinned items must be unpinned first
- **Hover** — Card background changes from #16162a to #1c1c35 on mouse enter

## Actions

| Action | How |
|---|---|
| **Select item** | Single-click on any card |
| **Paste / Type** (current mode) | **Double-click** card body, or click **📋 Paste**/**⌨ Type** in header, or press **Ctrl+Shift+Space** globally |
| **Switch mode (no execute)** | Click the other mode button — switches mode for next action |
| **Toggle pin** | Click **☆ / ★** star on card |
| **Delete item** | Click **🗑** on card (pinned items must be unpinned first) |
| **Delete all unpinned** | Click **🗑 Clear Unpinned** in bottom bar (shows confirmation) |
| **Delete selected** | Click **✕ Delete** in bottom bar |
| **Pin/Unpin selected** | Click **☆ Pin / ★ Unpin** in bottom bar |
| **Search** | Type in search box, or press **Ctrl+F** |
| **Filter pinned only** | Click **★ Only** in header |
| **Hide to tray** | Close window or press **Escape** |
| **Show from tray** | Click tray icon **"Show/Hide"** |
| **Pause/Resume monitoring** | Right-click tray icon → **Pause/Start Monitoring** |
| **Quit** | Right-click tray icon → **Quit** |

## Keyboard Shortcuts

| Shortcut | Where | Action |
|---|---|---|
| `Ctrl+Shift+Space` | Global (any app) | Paste/type selected clipboard item |
| `Ctrl+F` | Inside app | Focus search box |
| `Escape` | Inside app | Hide to system tray |

## Installation

### Option 1: Run from source

```bash
# Clone the repository
git clone https://github.com/yourusername/Advance-clipboard.git
cd Advance-clipboard

# Install dependencies
pip install -r requirements.txt

# Run the app (requires admin for global hotkey)
python main.py
```

### Option 2: Build standalone EXE

```bash
# Run the build script (cleans old builds, installs deps, builds EXE)
.\scripts\build.bat
```

The executable will be created in `dist/clipboard-manager.exe`.

> **Admin rights required** — The global hotkey uses `keyboard.add_hotkey()` which needs elevation on Windows. The EXE is built with `--uac-admin` to prompt for admin automatically. Old EXE instances must be killed via Task Manager before updating.

## Tech Stack

| Library | Usage |
|---|---|
| **Python 3.8+** | Language |
| **Tkinter** | GUI framework (Canvas + embedded Frame) |
| **PyInstaller** | EXE packaging (`--noconsole --onefile --uac-admin`) |
| **keyboard** | Global hotkey via `add_hotkey("ctrl+shift+space")` |
| **pyperclip** | Clipboard read/write |
| **pystray** | System tray icon with menu |
| **Pillow** | Custom tray icon rendering (purple rounded rectangle) |
| **ctypes** | Win32 API (`GetClipboardSequenceNumber`, `SwitchToThisWindow`) |
| **json** | Persistence (history + settings) |

## Design System

### Colors

| Token | Hex | Usage |
|---|---|---|
| `BG` | `#0d0d14` | Window background |
| `CARD` | `#16162a` | Card normal state |
| `CARD_HOVER` | `#1c1c35` | Card hover state |
| `CARD_SELECTED` | `#22224a` | Card selected state |
| `ACCENT` | `#7c3aed` | Purple accent (buttons, selected/pinned bar) |
| `TEXT` | `#f1f5f9` | Primary text |
| `MUTED` | `#6b7280` | Secondary text (timestamps, inactive) |
| `BORDER` | `#1e1e3a` | Borders, inactive accent bar |
| `DELETE_RED` | `#ef4444` | Delete buttons |
| `PIN_YELLOW` | `#f59e0b` | Pinned star |

### Fonts

| Token | Font |
|---|---|
| `FONT` | Segoe UI 10px |
| `FONT_BOLD` | Segoe UI 10px bold |
| `FONT_SMALL` | Segoe UI 9px |
| `FONT_HEADER` | Segoe UI 14px bold |
| `FONT_TIMESTAMP` | Segoe UI 8px |

### Timestamp Formatting

| Age | Display |
|---|---|
| < 60 seconds | "just now" |
| < 1 hour | "X min ago" |
| < 24 hours | "X hour ago" |
| >= 24 hours | "X day ago" |

## Project Structure

```
Advance-clipboard/
├── main.py                  # Entry point (imports src.main)
├── src/
│   ├── main.py              # Main GUI (Tkinter), hotkeys, tray icon, ClipboardApp
│   ├── monitor.py           # ClipboardMonitor — Win32 sequence-based detection (daemon thread, 500ms)
│   ├── storage.py           # JSON persistence (history + settings), migration, dedup, 500 cap
│   ├── paster.py            # paste_text, type_text, smart_paste (pause/resume monitor)
│   └── __init__.py          # Package init
├── scripts/
│   └── build.bat            # One-click PyInstaller EXE builder
├── requirements.txt         # Python dependencies
├── clipboard_history.json   # Auto-generated clipboard history
├── settings.json            # Auto-generated settings
├── crash_log.txt            # Auto-generated on crash
├── LICENSE                  # MIT License
└── README.md                # This file
```

### Key Architectural Details

| Detail | Description |
|---|---|
| **Canvas + Frame** | Cards are `ClipboardCard` (tk.Frame) widgets packed in a scrollable canvas — not a Listbox |
| **Recursive Binding** | `_bind_recursive()` binds events to a widget and all its children, ensuring clicks anywhere on a card register |
| **Thread Safety** | `ClipboardMonitor` runs in a daemon thread. UI updates use `root.after(0, ...)` to schedule on the main thread |
| **Duplicate Detection** | Uses `GetClipboardSequenceNumber()` — a Windows counter that increments on every real clipboard update, even if the content is the same. This ensures recopying the same text after deletion is detected as a new entry |
| **smart_paste Flow** | `monitor.stop()` → `pyperclip.copy(text)` → wait 50ms → `keyboard.send("ctrl+v")` → wait 100ms → `monitor.start()`. The pause prevents the paste action from being captured as new history |
| **Focus Management** | Before paste/type, Win32 `SwitchToThisWindow(prev_hwnd, True)` restores focus to the previous application. `_prev_hwnd` is saved when the window is shown from tray or when the hotkey is pressed |
| **Crash Logging** | On unhandled exception, writes traceback to `crash_log.txt` in the executable directory |

## Build Details

- Command: `pyinstaller --noconsole --onefile --uac-admin --name "clipboard-manager" src/main.py`
- Admin manifest is embedded for `keyboard.add_hotkey()` support
- Output: `dist/clipboard-manager.exe`

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
