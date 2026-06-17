"""
KC Legacy Valeting - Admin Client (Standalone Desktop App)
Connects independently to the API server to view & manage bookings.

Requirements: pip install requests pillow
Run:        python admin_client.py
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from urllib import request as urllib_request
import json
from PIL import Image, ImageTk
import io

API_BASE = os.environ.get("KC_API_URL", "https://kclegeacy.pythonanywhere.com")


def api_get(endpoint):
    try:
        req = urllib_request.Request(f"{API_BASE}{endpoint}", headers={"Accept": "application/json"})
        with urllib_request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def api_delete(endpoint):
    try:
        req = urllib_request.Request(f"{API_BASE}{endpoint}", method="DELETE")
        with urllib_request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_image(url):
    try:
        req = urllib_request.Request(f"{API_BASE}{url}")
        with urllib_request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data))
        return img
    except Exception:
        return None


class AdminClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KC Legacy Valeting - Admin Client")
        self.root.geometry("1000x750")
        self.root.configure(bg="#0d0d0d")
        self.root.minsize(800, 600)

        self.bg_color = "#0d0d0d"
        self.gold = "#d4af37"
        self.card_bg = "#1a1a1a"
        self.fg = "#e6e6e6"

        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        # Banner
        banner_frame = tk.Frame(self.root, bg=self.bg_color, height=160)
        banner_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        banner_frame.pack_propagate(False)

        self.banner_lbl = tk.Label(banner_frame, bg=self.card_bg)
        self.banner_lbl.pack(expand=True, fill=tk.BOTH)

        # Header
        hdr = tk.Label(self.root, text="KC LEGACY VALETING - ADMIN CLIENT", bg=self.bg_color,
                       fg=self.gold, font=("Helvetica Neue", 18, "bold"))
        hdr.pack(pady=(10, 2))
        sub = tk.Label(self.root, text=f"Connected to: {API_BASE}", bg=self.bg_color,
                       fg="#888", font=("Helvetica", 9))
        sub.pack(pady=(0, 10))

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.gold)], foreground=[("selected", "#0d0d0d")])

        # ── Bookings Tab ──
        bookings_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(bookings_tab, text="📋 Bookings")

        left = tk.Frame(bookings_tab, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8), pady=5)

        tk.Label(left, text="Booking Files", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 12, "bold"), pady=5).pack(fill=tk.X)
        self.booking_list = tk.Listbox(left, width=40, bg=self.card_bg, fg=self.fg,
                                       selectbackground=self.gold, selectforeground="#0d0d0d",
                                       font=("Consolas", 10), bd=0, highlightthickness=0)
        self.booking_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.booking_list.bind("<<ListboxSelect>>", self.on_booking_select)

        btn_frm = tk.Frame(left, bg=self.card_bg)
        btn_frm.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frm, text="🔄 Refresh", bg=self.gold, fg="#0d0d0d",
                  font=("Helvetica", 10, "bold"), bd=0, pady=5, cursor="hand2",
                  command=self.refresh_data).pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_frm, text="🗑️ Delete", bg="#8B0000", fg="white",
                  font=("Helvetica", 10, "bold"), bd=0, pady=5, cursor="hand2",
                  command=self.delete_booking).pack(fill=tk.X)

        right = tk.Frame(bookings_tab, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        tk.Label(right, text="Booking Details", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 12, "bold"), pady=5).pack(fill=tk.X)

        self.booking_text = scrolledtext.ScrolledText(right, wrap=tk.WORD, bg="#111", fg=self.fg,
                                                      font=("Consolas", 10), bd=0, padx=10, pady=10,
                                                      insertbackground=self.fg, highlightthickness=0)
        self.booking_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.booking_text.config(state=tk.DISABLED)

        # ── Gallery Tab ──
        gallery_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(gallery_tab, text="🖼️ Image Gallery")

        g_top = tk.Frame(gallery_tab, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        g_top.pack(fill=tk.X, padx=5, pady=(5, 8))
        tk.Label(g_top, text="Uploaded Images", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 12, "bold"), pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(g_top, text="🔄 Refresh Gallery", bg=self.gold, fg="#0d0d0d",
                  font=("Helvetica", 10, "bold"), bd=0, padx=15, pady=5, cursor="hand2",
                  command=self.refresh_gallery).pack(side=tk.RIGHT, padx=10)

        self.gallery_canvas = tk.Canvas(gallery_tab, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(gallery_tab, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_frame = tk.Frame(self.gallery_canvas, bg=self.bg_color)
        self.gallery_frame.bind("<Configure>", lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all")))
        self.gallery_canvas.create_window((0, 0), window=self.gallery_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=scrollbar.set)
        self.gallery_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                               anchor=tk.W, bg=self.card_bg, fg="#888", font=("Helvetica", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_banner(self):
        img = fetch_image("/api/banner")
        if img:
            w = self.banner_lbl.winfo_width()
            if w < 50:
                w = 960
            ratio = w / img.width
            h = int(img.height * ratio)
            if h > 160:
                h = 160
                ratio = h / img.height
                w = int(img.width * ratio)
            img = img.resize((w, h), Image.LANCZOS)
            self.banner_photo = ImageTk.PhotoImage(img)
            self.banner_lbl.config(image=self.banner_photo)
        else:
            self.banner_lbl.config(text="KC LEGACY VALETING", bg=self.card_bg, fg=self.gold,
                                   font=("Helvetica", 24, "bold"))

    def refresh_data(self):
        # Banner
        self.load_banner()

        # Bookings
        self.booking_list.delete(0, tk.END)
        data = api_get("/api/bookings")
        if "error" in data:
            self.status.config(text=f"Error: {data['error']}")
            return

        for b in data.get("bookings", []):
            self.booking_list.insert(tk.END, b["filename"])
        self.status.config(text=f"{data.get('count', 0)} booking(s) loaded")
        self.booking_text.config(state=tk.NORMAL)
        self.booking_text.delete(1.0, tk.END)
        self.booking_text.insert(1.0, "Select a booking to view details.\n\n")
        self.booking_text.config(state=tk.DISABLED)

    def on_booking_select(self, event):
        sel = self.booking_list.curselection()
        if not sel:
            return
        filename = self.booking_list.get(sel[0])
        data = api_get(f"/api/bookings/{filename}")
        self.booking_text.config(state=tk.NORMAL)
        self.booking_text.delete(1.0, tk.END)
        if "error" in data:
            self.booking_text.insert(1.0, f"Error: {data['error']}")
        else:
            self.booking_text.insert(1.0, data.get("content", ""))
        self.booking_text.config(state=tk.DISABLED)
        self.status.config(text=f"Viewing: {filename}")

    def delete_booking(self):
        sel = self.booking_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a booking file to delete.")
            return
        filename = self.booking_list.get(sel[0])
        if messagebox.askyesno("Confirm", f"Delete {filename}?"):
            res = api_delete(f"/api/bookings/{filename}")
            if "error" in res:
                messagebox.showerror("Error", res["error"])
            else:
                self.refresh_data()
                messagebox.showinfo("Deleted", f"{filename} removed.")

    def refresh_gallery(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()

        data = api_get("/api/images")
        if "error" in data:
            lbl = tk.Label(self.gallery_frame, text=f"Error loading gallery:\n{data['error']}",
                           bg=self.bg_color, fg="#ff4444", font=("Helvetica", 12))
            lbl.pack(pady=20)
            return

        images = data.get("images", [])
        if not images:
            lbl = tk.Label(self.gallery_frame, text="No images found.", bg=self.bg_color,
                           fg="#888", font=("Helvetica", 12))
            lbl.pack(pady=20)
            return

        row_frame = None
        for i, img_info in enumerate(images):
            if i % 3 == 0:
                row_frame = tk.Frame(self.gallery_frame, bg=self.bg_color)
                row_frame.pack(fill=tk.X, pady=5)

            cell = tk.Frame(row_frame, bg=self.card_bg, bd=1, relief=tk.RIDGE, padx=5, pady=5)
            cell.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

            img = fetch_image(img_info["url"])
            if img:
                img.thumbnail((220, 160), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(cell, image=photo, bg=self.card_bg)
                lbl.image = photo  # keep reference
                lbl.pack(pady=5)
            else:
                tk.Label(cell, text="[Image Error]", bg=self.card_bg, fg="#888").pack(pady=5)

            fn_lbl = tk.Label(cell, text=img_info["filename"], bg=self.card_bg, fg=self.fg,
                              font=("Consolas", 9), wraplength=220)
            fn_lbl.pack()
            sz_lbl = tk.Label(cell, text=f"{img_info['size'] / 1024:.1f} KB", bg=self.card_bg,
                              fg="#888", font=("Helvetica", 8))
            sz_lbl.pack()

        self.status.config(text=f"{len(images)} image(s) loaded")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminClientApp(root)
    root.after(100, app.load_banner)  # resize banner after window renders
    root.mainloop()
