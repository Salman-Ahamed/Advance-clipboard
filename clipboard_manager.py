import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys

import storage
from monitor import ClipboardMonitor
from paster import paste_text, type_text, smart_paste

# ── Design ────────────────────────────────────────────────────────────────────
BG = "#0d0d14"
CARD = "#16162a"
CARD_HOVER = "#1c1c35"
CARD_SELECTED = "#22224a"
ACCENT = "#7c3aed"
TEXT = "#f1f5f9"
MUTED = "#6b7280"
BORDER = "#1e1e3a"
DELETE_RED = "#ef4444"
PIN_YELLOW = "#f59e0b"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_TIMESTAMP = ("Segoe UI", 8)

monitor = None
tray_icon = None


def format_time(ts):
    diff = time.time() - (ts or time.time())
    if diff < 60:
        return "just now"
    elif diff < 3600:
        m = int(diff // 60)
        return f"{m} min ago"
    elif diff < 86400:
        h = int(diff // 3600)
        return f"{h} hour ago"
    else:
        d = int(diff // 86400)
        return f"{d} day ago"


def create_tray_icon(root):

    def on_show():
        root.after(0, lambda: show_window(root))

    def on_quit():
        root.after(0, lambda: quit_app(root))

    def on_toggle_monitor(icon, item):
        global monitor
        if monitor and monitor.is_running():
            monitor.stop()
        else:
            monitor.start()

    def update_menu(icon):
        if monitor and monitor.is_running():
            text = "Pause Monitoring"
        else:
            text = "Start Monitoring"
        menu = pystray.Menu(
            pystray.MenuItem("Show/Hide", on_show, default=True),
            pystray.MenuItem(text, on_toggle_monitor),
            pystray.MenuItem("Quit", on_quit),
        )
        icon.menu = menu

    try:
        import pystray
        from PIL import Image, ImageDraw

        def create_image():
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([8, 8, 56, 56], radius=12, fill="#7c3aed")
            draw.rectangle([22, 20, 42, 44], fill="#f1f5f9")
            draw.rectangle([18, 28, 46, 34], fill="#f1f5f9")
            return img

        icon = pystray.Icon("clipboard-manager", create_image(), "Clipboard")
        update_menu(icon)
        thread = threading.Thread(target=icon.run, daemon=True)
        thread.start()
        return icon
    except Exception:
        return None


def show_window(root):
    root.deiconify()
    root.lift()
    root.focus_force()


def quit_app(root):
    if monitor:
        monitor.stop()
    root.quit()
    root.destroy()
    if tray_icon:
        tray_icon.stop()
    os._exit(0)


class ClipboardCard(tk.Frame):
    def __init__(self, parent, data, index, is_selected,
                 on_select, on_paste, on_type, on_pin, on_delete):
        super().__init__(parent, bg=CARD_SELECTED if is_selected else CARD)
        self.data = data
        self.index = index
        self.is_selected = is_selected
        self.on_select = on_select
        self.on_paste_inline = on_paste
        self.on_type_inline = on_type
        self.on_pin_inline = on_pin
        self.on_delete_inline = on_delete

        self.pack(fill="x", padx=6, pady=2)

        # ── Inner layout ──
        inner = tk.Frame(self, bg=self.cget("bg"))
        inner.pack(fill="x", padx=0, pady=0)
        inner.bind("<Button-1>", self._do_select)
        inner.bind("<Double-Button-1>", self._do_action)
        self._bind_recursive(inner, "<Button-1>", self._do_select)

        # Left accent bar
        accent_color = ACCENT if data.get("pinned") else (ACCENT if is_selected else BORDER)
        self.accent = tk.Frame(inner, width=4, bg=accent_color)
        self.accent.pack(side="left", fill="y")
        self.accent.bind("<Double-Button-1>", self._do_action)
        self._bind_recursive(self.accent, "<Button-1>", self._do_select)

        # Pin star
        star = "★" if data.get("pinned") else "☆"
        pin_fg = PIN_YELLOW if data.get("pinned") else MUTED
        self.pin_lbl = tk.Label(inner, text=star, font=FONT,
                                bg=self.cget("bg"), fg=pin_fg, cursor="hand2", width=2)
        self.pin_lbl.pack(side="left", padx=(6, 2), pady=8)
        self.pin_lbl.bind("<Button-1>", lambda e: self._do_pin())

        # Value text
        self.text_frame = tk.Frame(inner, bg=self.cget("bg"))
        self.text_frame.pack(side="left", fill="x", expand=True, padx=(4, 4))
        self._bind_recursive(self.text_frame, "<Button-1>", self._do_select)

        val = data.get("value", "")
        display = val[:100] + "..." if len(val) > 100 else val
        self.val_lbl = tk.Label(self.text_frame, text=display, font=FONT,
                                bg=self.cget("bg"), fg=TEXT, anchor="w", wraplength=400)
        self.val_lbl.pack(fill="x")
        self.val_lbl.bind("<Double-Button-1>", self._do_action)
        self._bind_recursive(self.val_lbl, "<Button-1>", self._do_select)

        ts = data.get("timestamp", time.time())
        self.ts_lbl = tk.Label(self.text_frame, text=format_time(ts),
                               font=FONT_TIMESTAMP, bg=self.cget("bg"), fg=MUTED, anchor="w")
        self.ts_lbl.pack(fill="x")
        self.ts_lbl.bind("<Double-Button-1>", self._do_action)
        self._bind_recursive(self.ts_lbl, "<Button-1>", self._do_select)

        # Action buttons on right
        act = tk.Frame(inner, bg=self.cget("bg"))
        act.pack(side="right", padx=(0, 6))
        self._bind_recursive(act, "<Button-1>", self._do_select)

        btn_bg = self.cget("bg")
        self.action_btn = tk.Label(act, text="▶", font=FONT_SMALL,
                                   bg=btn_bg, fg=ACCENT, cursor="hand2", padx=4)
        self.action_btn.pack(side="top", pady=(6, 0))
        self.action_btn.bind("<Button-1>", lambda e: self._do_action())

        self.type_btn = tk.Label(act, text="⌨", font=FONT_SMALL,
                                 bg=btn_bg, fg=MUTED, cursor="hand2", padx=4)
        self.type_btn.pack(side="top", pady=(0, 2))
        self.type_btn.bind("<Button-1>", lambda e: self._do_type())

        self.del_btn = tk.Label(act, text="×", font=FONT_SMALL,
                                bg=btn_bg, fg=DELETE_RED, cursor="hand2", padx=4)
        self.del_btn.pack(side="top", pady=(0, 2))
        self.del_btn.bind("<Button-1>", lambda e: self._do_delete())

        # Hover effects
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _bind_recursive(self, widget, event, callback):
        widget.bind(event, callback, add="+")
        for child in widget.winfo_children():
            self._bind_recursive(child, event, callback)

    def _do_select(self, event=None):
        if self.on_select:
            self.on_select(self.index)

    def _do_action(self):
        if self.on_paste_inline:
            self.on_paste_inline(self.data)

    def _do_type(self):
        if self.on_type_inline:
            self.on_type_inline(self.data)

    def _do_pin(self):
        if self.on_pin_inline:
            self.on_pin_inline(self.index)

    def _do_delete(self):
        if self.on_delete_inline:
            self.on_delete_inline(self.index)

    def _on_hover(self, event):
        if not self.is_selected:
            self.configure(bg=CARD_HOVER)
            self._recolor_children(CARD_HOVER)

    def _on_leave(self, event):
        if not self.is_selected:
            self.configure(bg=CARD)
            self._recolor_children(CARD)

    def _recolor_children(self, color):
        for child in self.winfo_children():
            try:
                child.configure(bg=color)
            except:
                pass
            for sub in child.winfo_children():
                try:
                    sub.configure(bg=color)
                except:
                    pass
                for sub2 in sub.winfo_children():
                    try:
                        sub2.configure(bg=color)
                    except:
                        pass

    def update_selection(self, is_selected):
        self.is_selected = is_selected
        bg = CARD_SELECTED if is_selected else CARD
        self.configure(bg=bg)
        self._recolor_children(bg)
        accent_color = ACCENT if (self.data.get("pinned") or is_selected) else BORDER
        self.accent.configure(bg=accent_color)
        pin_fg = PIN_YELLOW if self.data.get("pinned") else MUTED
        self.pin_lbl.configure(fg=pin_fg)


class ClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard")
        self.root.configure(bg=BG)
        self.root.geometry(storage.load_settings().get("window_geometry", "600x400+200+100"))
        self.root.minsize(600, 400)
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

        self.items = storage.load_history()
        self.filter_text = ""
        self.show_pinned_only = False
        self.selected_real_index = None

        settings = storage.load_settings()
        self.paste_mode = settings.get("paste_mode", "type")

        self.cards = []
        self._setup_ui()
        self._register_paste_hotkey()
        self._start_monitor()
        self._bind_global_shortcuts()

    # ── UI Setup ─────────────────────────────────────────────────────────────
    def _setup_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self.root, bg=BG)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        header.grid_columnconfigure(3, weight=1)

        tk.Label(header, text="☰ Clipboard", font=FONT_HEADER,
                 bg=BG, fg=TEXT).grid(row=0, column=0, sticky="w")

        # Paste / Type mode buttons in header
        mode_style = {"font": FONT_SMALL, "relief": "flat",
                      "padx": 10, "pady": 2, "cursor": "hand2", "bd": 0}
        self.paste_btn = tk.Button(header, text="📋  Paste",
                                   bg=ACCENT, fg=TEXT,
                                   activebackground="#6d28d9", activeforeground=TEXT,
                                   **mode_style, command=self._on_paste_click)
        self.paste_btn.grid(row=0, column=1, padx=(8, 2))

        self.type_btn = tk.Button(header, text="⌨  Type",
                                  bg=CARD, fg=MUTED,
                                  activebackground=ACCENT, activeforeground=TEXT,
                                  **mode_style, command=self._on_type_click)
        self.type_btn.grid(row=0, column=2, padx=(2, 0))

        # Search + pinned toggle
        search_frame = tk.Frame(header, bg=BG)
        search_frame.grid(row=0, column=3, sticky="e")

        self.pinned_btn = tk.Button(search_frame, text="★ Only", font=FONT_SMALL,
                                    bg=CARD, fg=MUTED, relief="flat", padx=8, pady=2,
                                    activebackground=ACCENT, activeforeground=TEXT,
                                    cursor="hand2", command=self._toggle_pinned_filter)
        self.pinned_btn.pack(side="right", padx=(4, 0))

        self.search_var = tk.StringVar(value="🔍  Search history...")
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=FONT, bg=CARD, fg=TEXT, insertbackground=TEXT,
                                     relief="flat", width=24, bd=0)
        self.search_entry.pack(side="right", padx=(0, 4))
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, "end")
                               if self.search_entry.get() == "🔍  Search history..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "🔍  Search history...")
                               if not self.search_entry.get() else None)

        # Separator
        sep = tk.Frame(self.root, height=1, bg=BORDER)
        sep.grid(row=0, column=0, sticky="ew", padx=16, pady=(44, 0))

        # Canvas + scrollable frame (replaces listbox)
        list_frame = tk.Frame(self.root, bg=BG)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Custom.Vertical.TScrollbar",
                        background="#2d2d50", troughcolor=BG, arrowcolor=ACCENT,
                        bordercolor=BORDER, lightcolor="#1c1c35", darkcolor="#0d0d14")

        self.scrollbar = ttk.Scrollbar(list_frame, style="Custom.Vertical.TScrollbar",
                                        orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas, bg=BG)
        self.scroll_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="inner")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Bottom bar
        bottom = tk.Frame(self.root, bg=BG)
        bottom.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        bottom.grid_columnconfigure(2, weight=1)

        self.status_label = tk.Label(bottom, font=FONT_SMALL, bg=BG, fg=MUTED)
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        btn_style = {"font": FONT_SMALL, "relief": "flat",
                     "padx": 10, "pady": 4, "cursor": "hand2", "bd": 0}

        btn_style_full = dict(btn_style, bg=CARD, fg=TEXT,
                              activebackground=ACCENT, activeforeground=TEXT)
        self.pin_btn = tk.Button(bottom, text="☆  Pin", **btn_style_full,
                                 command=self._toggle_pin_selected)
        self.pin_btn.grid(row=0, column=1, padx=(0, 4))

        delete_style = dict(btn_style_full, fg=DELETE_RED, activebackground="#450a0a")
        self.delete_btn = tk.Button(bottom, text="✕  Delete", **delete_style,
                                    command=self._delete_selected)
        self.delete_btn.grid(row=0, column=2, padx=(0, 4))

        self.clear_btn = tk.Button(bottom, text="🗑  Clear Unpinned", **btn_style_full,
                                   command=self._clear_unpinned)
        self.clear_btn.grid(row=0, column=3, padx=(0, 4))

        self.search_var.trace_add("write", lambda *a: self._on_search())
        self._update_mode_buttons()
        self._refresh_list()

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig("inner", width=event.width)

    # ── List Management ──────────────────────────────────────────────────────
    def _get_filtered_items(self):
        items = self.items
        if self.show_pinned_only:
            items = [i for i in items if i.get("pinned", False)]
        if self.filter_text:
            q = self.filter_text.lower()
            items = [i for i in items if q in i.get("value", "").lower()]
        return items

    def _find_real_index(self, item):
        for i, it in enumerate(self.items):
            if it is item:
                return i
        return -1

    def _rebuild_cards(self):
        for card in self.cards:
            card.destroy()
        self.cards.clear()

        filtered = self._get_filtered_items()

        # Auto-select first item if nothing selected
        sel_real = self.selected_real_index
        if sel_real is not None:
            sel_in_filtered = None
            for i, item in enumerate(filtered):
                if self._find_real_index(item) == sel_real:
                    sel_in_filtered = i
                    break
            if sel_in_filtered is None:
                sel_real = None

        if sel_real is None and filtered:
            sel_real = self._find_real_index(filtered[0])

        self.selected_real_index = sel_real

        for i, item in enumerate(filtered):
            real_idx = self._find_real_index(item)
            is_sel = (real_idx == sel_real)
            card = ClipboardCard(
                self.scroll_frame, item, real_idx, is_sel,
                on_select=self._on_card_select,
                on_paste=self._on_card_paste,
                on_type=self._on_card_type,
                on_pin=self._on_card_pin,
                on_delete=self._on_card_delete,
            )
            self.cards.append(card)

        total = len(self.items)
        pinned = sum(1 for i in self.items if i.get("pinned", False))
        self.status_label.config(text=f"Ctrl+Shift+Space: Paste  |  Total: {total}  |  Pinned: {pinned}")

        if self.selected_real_index is not None:
            self.root.after_idle(self._scroll_to_selection)

    def _scroll_to_selection(self):
        for card in self.cards:
            if card.index == self.selected_real_index:
                y = card.winfo_y()
                self.canvas.yview_moveto(y / self.canvas.winfo_height())
                break

    def _on_card_select(self, real_index):
        old_sel = self.selected_real_index
        self.selected_real_index = real_index
        for card in self.cards:
            card.update_selection(card.index == real_index)
        self._update_bottom_pin_button()

    def _on_card_paste(self, data):
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(100, lambda: self._execute(data["value"]))
        self.root.after(400, self.root.deiconify)

    def _on_card_type(self, data):
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(100, lambda: type_text(data["value"]))
        self.root.after(400, self.root.deiconify)

    def _on_card_pin(self, real_index):
        self.items = storage.toggle_pin(real_index)
        self._rebuild_cards()

    def _on_card_delete(self, real_index):
        item = self.items[real_index]
        if item.get("pinned"):
            messagebox.showinfo("Info", "Unpin the item first to delete it.")
            return
        self.items = storage.remove_item(real_index)
        if self.selected_real_index == real_index:
            self.selected_real_index = None
        self._rebuild_cards()

    def _refresh_list(self):
        self._rebuild_cards()

    def _on_search(self):
        self.filter_text = self.search_entry.get()
        if self.filter_text == "🔍  Search history...":
            self.filter_text = ""
        self._rebuild_cards()

    def _toggle_pinned_filter(self):
        self.show_pinned_only = not self.show_pinned_only
        color = ACCENT if self.show_pinned_only else MUTED
        self.pinned_btn.config(fg=color)
        self._rebuild_cards()

    def _update_bottom_pin_button(self):
        if self.selected_real_index is not None and self.selected_real_index < len(self.items):
            pinned = self.items[self.selected_real_index].get("pinned", False)
            self.pin_btn.config(text="★  Unpin" if pinned else "☆  Pin")
        else:
            self.pin_btn.config(text="☆  Pin")

    def _update_mode_buttons(self):
        if self.paste_mode == "paste":
            self.paste_btn.config(bg=ACCENT, fg=TEXT)
            self.type_btn.config(bg=CARD, fg=MUTED)
        else:
            self.paste_btn.config(bg=CARD, fg=MUTED)
            self.type_btn.config(bg=ACCENT, fg=TEXT)

    def _set_paste_mode(self, mode):
        self.paste_mode = mode
        s = storage.load_settings()
        s["paste_mode"] = mode
        storage.save_settings(s)
        self._update_mode_buttons()

    def _execute(self, text):
        if self.paste_mode == "paste":
            global monitor
            smart_paste(text, monitor)
        else:
            type_text(text)

    def _on_paste_click(self):
        self._set_paste_mode("paste")
        self._paste_selected()

    def _on_type_click(self):
        self._set_paste_mode("type")
        self._type_selected()

    # ── Bottom Bar Actions ───────────────────────────────────────────────────
    def _get_selected_item(self):
        idx = self.selected_real_index
        if idx is None or idx >= len(self.items):
            return None
        return self.items[idx], idx

    def _paste_selected(self):
        result = self._get_selected_item()
        if not result:
            if self.items:
                self._on_card_select(self._find_real_index(self.items[0]))
                result = self._get_selected_item()
            if not result:
                return
        item, _ = result
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(100, lambda: self._execute(item["value"]))
        self.root.after(400, self.root.deiconify)

    def _type_selected(self):
        result = self._get_selected_item()
        if not result:
            if self.items:
                self._on_card_select(self._find_real_index(self.items[0]))
                result = self._get_selected_item()
            if not result:
                return
        item, _ = result
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(100, lambda: type_text(item["value"]))
        self.root.after(400, self.root.deiconify)

    def _toggle_pin_selected(self):
        if self.selected_real_index is None:
            return
        self.items = storage.toggle_pin(self.selected_real_index)
        self._rebuild_cards()

    def _delete_selected(self):
        if self.selected_real_index is None:
            return
        item = self.items[self.selected_real_index]
        if item.get("pinned"):
            messagebox.showinfo("Info", "Unpin the item first to delete it.")
            return
        self.items = storage.remove_item(self.selected_real_index)
        self.selected_real_index = None
        self._rebuild_cards()

    def _clear_unpinned(self):
        if messagebox.askyesno("Confirm", "Delete all unpinned items?"):
            self.items = storage.clear_unpinned()
            self.selected_real_index = None
            self._rebuild_cards()

    # ── Hotkey ──────────────────────────────────────────────────────────────
    def _register_paste_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey("ctrl+shift+space", lambda: self.root.after(0, self._hotkey_paste))
        except Exception:
            pass

    def _hotkey_paste(self):
        result = self._get_selected_item()
        if not result and self.items:
            self._on_card_select(self._find_real_index(self.items[0]))
            result = self._get_selected_item()
        if not result:
            return
        item, _ = result
        self.root.withdraw()
        self.root.update_idletasks()
        global monitor
        if self.paste_mode == "paste":
            smart_paste(item["value"], monitor)
        else:
            type_text(item["value"])
        self.root.after(400, self.root.deiconify)

    # ── Keyboard Shortcuts ──────────────────────────────────────────────────
    def _bind_global_shortcuts(self):
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.root.bind("<Escape>", lambda e: self.root.iconify())

    # ── Monitor ──────────────────────────────────────────────────────────────
    def _start_monitor(self):
        global monitor
        monitor = ClipboardMonitor(on_new_item=self._on_new_item)
        monitor.start()

    def _on_new_item(self, items):
        def update():
            self.items = items
            self._rebuild_cards()
        self.root.after(0, update)

    # ── Window Mgmt ──────────────────────────────────────────────────────────
    def _minimize_to_tray(self):
        self.root.withdraw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ClipboardApp(root)
        tray_icon = create_tray_icon(root)
        if tray_icon:
            root.protocol("WM_DELETE_WINDOW", app._minimize_to_tray)
        app.run()
    except Exception:
        import traceback, os, sys
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(exe_dir, "crash_log.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Clipboard Crash Log\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n\n")
            traceback.print_exc(file=f)
        raise
