"""
KC Legacy Valeting - Admin Booking Viewer
A standalone desktop program to check bookings and showcase the brand banner.
Run with: python admin_program.py
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request
import json
from PIL import Image, ImageTk, ImageEnhance, ImageOps

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "text")
IMAGE_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "images")

# Fallback banner images (in order of preference)
BANNER_CANDIDATES = [
    os.path.join(IMAGE_UPLOADS_DIR, "hero", "hero.png"),
    os.path.join(IMAGE_UPLOADS_DIR, "header2.jpg"),
    os.path.join(IMAGE_UPLOADS_DIR, "favicon.png"),
]

# PythonAnywhere API (PRIMARY system)
API_BASE_URL = "https://kclegeacy.pythonanywhere.com"


def fetch_bookings_from_api():
    """Fetch all bookings from PythonAnywhere (PRIMARY system)."""
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/api/bookings", timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get("bookings", [])
    except Exception:
        return []


def delete_booking_via_api(filename):
    """Delete a booking from PythonAnywhere (PRIMARY system)."""
    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/api/bookings/{filename}",
            method='DELETE'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def find_banner():
    """Return the first existing banner image path, or None."""
    for path in BANNER_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KC Legacy Valeting - Admin Booking Viewer")
        self.root.geometry("900x700")
        self.root.configure(bg="#0d0d0d")
        self.root.minsize(700, 500)

        # Styling
        self.bg_color = "#0d0d0d"
        self.gold = "#d4af37"
        self.card_bg = "#1a1a1a"
        self.fg = "#e6e6e6"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg, font=("Helvetica", 10))
        style.configure("Gold.TLabel", background=self.bg_color, foreground=self.gold, font=("Helvetica", 16, "bold"))
        style.configure("TButton",
                        font=("Helvetica", 10, "bold"),
                        background=self.gold,
                        foreground="#0d0d0d")
        style.map("TButton",
                  background=[("active", "#b8962e")],
                  foreground=[("active", "#0d0d0d")])

        self.bookings_data = {}
        self._build_ui()
        self.refresh_bookings()

    def _build_ui(self):
        # Full-window background image (KC logo)
        bg_path = os.path.join(IMAGE_UPLOADS_DIR, "hero", "hero.png")
        if os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                enhancer = ImageEnhance.Brightness(bg_img)
                bg_img = enhancer.enhance(0.15)
                win_w, win_h = 900, 580
                bg_img = ImageOps.contain(bg_img, (win_w, win_h))
                self.bg_tk = ImageTk.PhotoImage(bg_img)
                self.bg_label = tk.Label(self.root, image=self.bg_tk, bg=self.bg_color)
                self.bg_label.place(x=0, y=120, relwidth=1, height=win_h)
            except Exception:
                pass

        # Top Banner Frame
        banner_frame = tk.Frame(self.root, bg=self.bg_color, height=180)
        banner_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        banner_frame.pack_propagate(False)

        banner_path = find_banner()
        if banner_path:
            try:
                img = Image.open(banner_path)
                # Resize to fit width while keeping aspect ratio
                target_width = 880
                ratio = target_width / img.width
                target_height = int(img.height * ratio)
                if target_height > 180:
                    target_height = 180
                    ratio = target_height / img.height
                    target_width = int(img.width * ratio)
                img = img.resize((target_width, target_height), Image.LANCZOS)
                self.banner_tk = ImageTk.PhotoImage(img)
                self.banner_lbl = tk.Label(banner_frame, image=self.banner_tk, bg=self.bg_color)
                self.banner_lbl.pack(expand=True, pady=(30, 0))
            except Exception:
                self._placeholder_banner(banner_frame)
        else:
            self._placeholder_banner(banner_frame)

        # Header
        header = ttk.Label(self.root, text="KC LEGACY VALETING - ADMIN DASHBOARD", style="Gold.TLabel")
        header.pack(pady=(10, 5))

        subtitle = ttk.Label(self.root, text="Review customer bookings and session notes")
        subtitle.pack(pady=(0, 10))

        # Main Content Area
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Booking List
        left_frame = tk.Frame(main_frame, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        list_header = tk.Label(left_frame, text="📁 Booking Files", bg=self.card_bg, fg=self.gold,
                               font=("Helvetica", 12, "bold"), pady=5)
        list_header.pack(fill=tk.X)

        list_scroll = tk.Scrollbar(left_frame, orient=tk.VERTICAL, bg=self.card_bg,
                                   highlightthickness=0)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(left_frame, width=35, bg=self.card_bg, fg=self.fg,
                                  selectbackground=self.gold, selectforeground="#0d0d0d",
                                  font=("Consolas", 10), bd=0, highlightthickness=0,
                                  yscrollcommand=list_scroll.set)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        list_scroll.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btn_frame = tk.Frame(left_frame, bg=self.card_bg)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        refresh_btn = ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_bookings)
        refresh_btn.pack(fill=tk.X, pady=(0, 5))

        del_btn = ttk.Button(btn_frame, text="🗑️ Delete Selected", command=self.delete_booking)
        del_btn.pack(fill=tk.X)

        # Right: Booking Content
        right_frame = tk.Frame(main_frame, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        content_header = tk.Label(right_frame, text="📄 Booking Details", bg=self.card_bg, fg=self.gold,
                                  font=("Helvetica", 12, "bold"), pady=5)
        content_header.pack(fill=tk.X)

        self.content_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD, bg="#111", fg=self.fg,
            font=("Consolas", 10), bd=0, padx=10, pady=10,
            insertbackground=self.fg, highlightthickness=0
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.content_text.config(state=tk.DISABLED)

        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                               anchor=tk.W, bg=self.card_bg, fg="#888", font=("Helvetica", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _placeholder_banner(self, parent):
        lbl = tk.Label(parent, text="KC LEGACY VALETING", bg=self.card_bg, fg=self.gold,
                       font=("Helvetica", 24, "bold"))
        lbl.pack(expand=True)

    def refresh_bookings(self):
        self.listbox.delete(0, tk.END)
        self.bookings_data = {}

        # Fetch from PythonAnywhere FIRST (primary system)
        api_bookings = fetch_bookings_from_api()
        if api_bookings:
            for b in api_bookings:
                filename = b.get("filename", "unknown")
                self.bookings_data[filename] = b.get("content", "")
                self.listbox.insert(tk.END, filename)
            self.status.config(text=f"{len(api_bookings)} booking(s) from admin dashboard")
        else:
            # Fallback to local files
            os.makedirs(TEXT_UPLOADS_DIR, exist_ok=True)
            files = sorted([f for f in os.listdir(TEXT_UPLOADS_DIR) if f.endswith(".txt")])
            for f in files:
                try:
                    with open(os.path.join(TEXT_UPLOADS_DIR, f), "r", encoding="utf-8", errors="replace") as fh:
                        self.bookings_data[f] = fh.read()
                except Exception:
                    self.bookings_data[f] = "[Error reading file]"
                self.listbox.insert(tk.END, f)
            self.status.config(text=f"{len(files)} booking(s) from local backup")

        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, "Select a booking from the list to view its contents.\n\n")
        self.content_text.config(state=tk.DISABLED)

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        filename = self.listbox.get(selection[0])
        content = self.bookings_data.get(filename, "[No content available]")
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content)
        self.content_text.config(state=tk.DISABLED)
        self.status.config(text=f"Viewing: {filename}")

    def delete_booking(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a booking to delete.")
            return
        filename = self.listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{filename}?"):
            # Delete from PythonAnywhere FIRST (primary system)
            api_ok = delete_booking_via_api(filename)
            if api_ok:
                # Also remove local backup if it exists
                filepath = os.path.join(TEXT_UPLOADS_DIR, filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                self.refresh_bookings()
                messagebox.showinfo("Deleted", f"{filename} has been deleted from admin dashboard.")
            else:
                # Fallback: delete locally only
                filepath = os.path.join(TEXT_UPLOADS_DIR, filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        self.refresh_bookings()
                        messagebox.showinfo("Deleted", f"{filename} deleted locally (admin dashboard sync failed).")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete:\n{e}")
                else:
                    messagebox.showerror("Error", "Failed to delete from admin dashboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
