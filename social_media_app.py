"""
KC Legacy Valeting - Social Media Content Creator
Create Instagram / Facebook ready posts from Before & After photos.

Requirements: pip install requests pillow
Run:        python social_media_app.py
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from urllib import request as urllib_request
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

API_BASE = os.environ.get("KC_API_URL", "http://localhost:5000")

# Social media dimensions
SIZES = {
    "Instagram Square (1:1)": (1080, 1080),
    "Instagram Portrait (4:5)": (1080, 1350),
    "Instagram Landscape (1.91:1)": (1080, 566),
    "Facebook Post (1200x630)": (1200, 630),
    "Story (9:16)": (1080, 1920),
}


def api_get(endpoint):
    try:
        req = urllib_request.Request(f"{API_BASE}{endpoint}", headers={"Accept": "application/json"})
        with urllib_request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_image(url):
    try:
        req = urllib_request.Request(f"{API_BASE}{url}")
        with urllib_request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        return Image.open(io.BytesIO(data))
    except Exception:
        return None


class SocialMediaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KC Legacy Valeting - Social Media Creator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0d0d0d")
        self.root.minsize(1000, 700)

        self.bg_color = "#0d0d0d"
        self.gold = "#d4af37"
        self.card_bg = "#1a1a1a"
        self.fg = "#e6e6e6"

        self.before_img = None
        self.after_img = None
        self.preview_photo = None

        self._build_ui()
        self.load_gallery()

    def _build_ui(self):
        # Header
        hdr = tk.Label(self.root, text="SOCIAL MEDIA CONTENT CREATOR", bg=self.bg_color,
                       fg=self.gold, font=("Helvetica Neue", 20, "bold"))
        hdr.pack(pady=(15, 5))
        sub = tk.Label(self.root, text="Create stunning Before & After posts for Instagram & Facebook",
                       bg=self.bg_color, fg="#888", font=("Helvetica", 11))
        sub.pack(pady=(0, 15))

        # Main area
        main = tk.Frame(self.root, bg=self.bg_color)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # ── Left: Image Selector ──
        left = tk.Frame(main, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(left, text="📁 Available Images", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 13, "bold"), pady=8).pack(fill=tk.X)

        search_frm = tk.Frame(left, bg=self.card_bg)
        search_frm.pack(fill=tk.X, padx=8, pady=5)
        tk.Label(search_frm, text="Filter:", bg=self.card_bg, fg=self.fg).pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", lambda *args: self.apply_filter())
        tk.Entry(search_frm, textvariable=self.filter_var, bg="#111", fg=self.fg,
                 insertbackground=self.fg, font=("Helvetica", 10), bd=1, highlightthickness=1,
                 highlightcolor=self.gold).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        list_container = tk.Frame(left, bg=self.card_bg)
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        self.img_list = tk.Listbox(list_container, width=35, bg=self.card_bg, fg=self.fg,
                                   selectbackground=self.gold, selectforeground="#0d0d0d",
                                   font=("Consolas", 10), bd=0, highlightthickness=0)
        self.img_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(list_container, orient="vertical", command=self.img_list.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.img_list.config(yscrollcommand=sb.set)

        btn_frm = tk.Frame(left, bg=self.card_bg)
        btn_frm.pack(fill=tk.X, padx=8, pady=8)
        tk.Button(btn_frm, text="📷 Load as BEFORE", bg="#444", fg=self.fg,
                  font=("Helvetica", 10, "bold"), bd=0, pady=6, cursor="hand2",
                  command=lambda: self.load_selected("before")).pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_frm, text="✨ Load as AFTER", bg=self.gold, fg="#0d0d0d",
                  font=("Helvetica", 10, "bold"), bd=0, pady=6, cursor="hand2",
                  command=lambda: self.load_selected("after")).pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_frm, text="🔄 Refresh List", bg="#222", fg=self.fg,
                  font=("Helvetica", 10), bd=0, pady=5, cursor="hand2",
                  command=self.load_gallery).pack(fill=tk.X)

        # ── Center: Controls ──
        center = tk.Frame(main, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        center.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(center, text="⚙️ Post Settings", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 13, "bold"), pady=8).pack(fill=tk.X)

        pad = 10
        # Platform size
        tk.Label(center, text="Platform / Size:", bg=self.card_bg, fg=self.fg,
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=pad, pady=(10, 2))
        self.size_var = tk.StringVar(value="Instagram Square (1:1)")
        size_menu = ttk.Combobox(center, textvariable=self.size_var,
                                 values=list(SIZES.keys()), state="readonly", width=28)
        size_menu.pack(padx=pad, pady=(0, 10))
        size_menu.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # Caption
        tk.Label(center, text="Caption / Headline:", bg=self.card_bg, fg=self.fg,
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=pad, pady=(5, 2))
        self.caption_var = tk.StringVar(value="Before & After Transformation ✨")
        tk.Entry(center, textvariable=self.caption_var, bg="#111", fg=self.fg,
                 insertbackground=self.fg, font=("Helvetica", 10), bd=1, highlightthickness=1,
                 highlightcolor=self.gold, width=30).pack(padx=pad, pady=(0, 10))
        self.caption_var.trace("w", lambda *args: self.update_preview())

        # Subtitle
        tk.Label(center, text="Subtitle:", bg=self.card_bg, fg=self.fg,
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=pad, pady=(5, 2))
        self.subtitle_var = tk.StringVar(value="KC Legacy Valeting")
        tk.Entry(center, textvariable=self.subtitle_var, bg="#111", fg=self.fg,
                 insertbackground=self.fg, font=("Helvetica", 10), bd=1, highlightthickness=1,
                 highlightcolor=self.gold, width=30).pack(padx=pad, pady=(0, 10))
        self.subtitle_var.trace("w", lambda *args: self.update_preview())

        # Layout
        tk.Label(center, text="Layout:", bg=self.card_bg, fg=self.fg,
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=pad, pady=(5, 2))
        self.layout_var = tk.StringVar(value="Side by Side")
        tk.Radiobutton(center, text="Side by Side", variable=self.layout_var, value="Side by Side",
                       bg=self.card_bg, fg=self.fg, selectcolor=self.gold, font=("Helvetica", 10),
                       command=self.update_preview).pack(anchor="w", padx=pad)
        tk.Radiobutton(center, text="Before | After Labels", variable=self.layout_var,
                       value="Before | After Labels", bg=self.card_bg, fg=self.fg,
                       selectcolor=self.gold, font=("Helvetica", 10),
                       command=self.update_preview).pack(anchor="w", padx=pad)
        tk.Radiobutton(center, text="Single Image Only", variable=self.layout_var,
                       value="Single", bg=self.card_bg, fg=self.fg,
                       selectcolor=self.gold, font=("Helvetica", 10),
                       command=self.update_preview).pack(anchor="w", padx=pad)

        # Hashtags
        tk.Label(center, text="Hashtags:", bg=self.card_bg, fg=self.fg,
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=pad, pady=(15, 2))
        self.hashtags = tk.Text(center, height=5, width=32, bg="#111", fg=self.fg,
                                insertbackground=self.fg, font=("Helvetica", 9), bd=1,
                                highlightthickness=1, highlightcolor=self.gold, wrap=tk.WORD)
        self.hashtags.pack(padx=pad, pady=(0, 10))
        self.hashtags.insert(1.0, "#CarDetailing #BeforeAndAfter #KClegacyValeting "
                               "#PaintCorrection #CeramicCoating #AutoDetailing "
                               "#CarCare #LondonDetailing #PremiumValeting")

        # Caption generator button
        tk.Button(center, text="✨ Auto-Generate Caption", bg="#222", fg=self.gold,
                  font=("Helvetica", 10, "bold"), bd=0, pady=8, cursor="hand2",
                  command=self.auto_caption).pack(fill=tk.X, padx=pad, pady=(5, 10))

        # Export
        tk.Button(center, text="💾 Export Post Image", bg=self.gold, fg="#0d0d0d",
                  font=("Helvetica", 12, "bold"), bd=0, pady=10, cursor="hand2",
                  command=self.export_image).pack(fill=tk.X, padx=pad, pady=(10, 5))
        tk.Button(center, text="📋 Copy Caption to Clipboard", bg="#222", fg=self.fg,
                  font=("Helvetica", 10), bd=0, pady=6, cursor="hand2",
                  command=self.copy_caption).pack(fill=tk.X, padx=pad, pady=(0, 10))

        # ── Right: Preview ──
        right = tk.Frame(main, bg=self.card_bg, bd=1, relief=tk.RIDGE)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="👁️ Live Preview", bg=self.card_bg, fg=self.gold,
                 font=("Helvetica", 13, "bold"), pady=8).pack(fill=tk.X)

        self.preview_lbl = tk.Label(right, bg="#111", text="Select BEFORE and AFTER images\nto see preview",
                                    fg="#888", font=("Helvetica", 12))
        self.preview_lbl.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Status
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                               anchor=tk.W, bg=self.card_bg, fg="#888", font=("Helvetica", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_gallery(self):
        self.img_list.delete(0, tk.END)
        self._image_data = []
        data = api_get("/api/images")
        if "error" in data:
            self.status.config(text=f"API Error: {data['error']}")
            return
        for img in data.get("images", []):
            self.img_list.insert(tk.END, img["filename"])
            self._image_data.append(img)
        self.status.config(text=f"{len(self._image_data)} image(s) available")

    def apply_filter(self):
        term = self.filter_var.get().lower()
        self.img_list.delete(0, tk.END)
        for img in self._image_data:
            if term in img["filename"].lower():
                self.img_list.insert(tk.END, img["filename"])

    def load_selected(self, slot):
        sel = self.img_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an image from the list first.")
            return
        filename = self.img_list.get(sel[0])
        # Find full data
        img_data = next((i for i in self._image_data if i["filename"] == filename), None)
        if not img_data:
            return
        img = fetch_image(img_data["url"])
        if not img:
            messagebox.showerror("Error", "Failed to load image from server.")
            return
        if slot == "before":
            self.before_img = img
            self.status.config(text=f"BEFORE loaded: {filename}")
        else:
            self.after_img = img
            self.status.config(text=f"AFTER loaded: {filename}")
        self.update_preview()

    def auto_caption(self):
        caption = ("✨ Incredible transformation by KC Legacy Valeting! ✨\n\n"
                   "From tired paintwork to a mirror finish — every detail matters.\n\n"
                   "🚗 Professional mobile detailing\n"
                   "📍 Serving London & surrounding areas\n"
                   "💎 Premium products, premium results\n\n"
                   "DM us to book your session!")
        self.caption_var.set("Before & After Transformation ✨")
        self.hashtags.delete(1.0, tk.END)
        self.hashtags.insert(1.0, "#CarDetailing #BeforeAndAfter #PaintCorrection "
                               "#CeramicCoating #AutoDetailing #CarCare "
                               "#LondonDetailing #PremiumValeting #KClegacyValeting "
                               "#DetailingWorld #CarWash #InteriorDetailing")
        messagebox.showinfo("Caption Generated", f"Caption template created!\n\n{caption}")

    def update_preview(self):
        if not self.before_img and not self.after_img:
            self.preview_lbl.config(image="", text="Select BEFORE and AFTER images\nto see preview",
                                    fg="#888", font=("Helvetica", 12))
            return

        size_name = self.size_var.get()
        target_w, target_h = SIZES.get(size_name, (1080, 1080))
        layout = self.layout_var.get()

        # Create canvas
        canvas = Image.new("RGB", (target_w, target_h), "#0d0d0d")
        draw = ImageDraw.Draw(canvas)

        try:
            font_large = ImageFont.truetype("arial.ttf", int(target_h * 0.06))
            font_small = ImageFont.truetype("arial.ttf", int(target_h * 0.035))
            font_label = ImageFont.truetype("arial.ttf", int(target_h * 0.04))
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_label = ImageFont.load_default()

        caption = self.caption_var.get()
        subtitle = self.subtitle_var.get()

        margin = int(target_h * 0.03)
        header_h = int(target_h * 0.12) if caption else margin
        footer_h = int(target_h * 0.06)
        usable_h = target_h - header_h - footer_h - (margin * 2)

        if layout == "Single" and self.after_img:
            img_to_show = self.after_img.copy()
            img_to_show = self._fit_image(img_to_show, target_w - margin * 2, usable_h)
            x = (target_w - img_to_show.width) // 2
            y = header_h + margin + (usable_h - img_to_show.height) // 2
            canvas.paste(img_to_show, (x, y))
        elif layout in ("Side by Side", "Before | After Labels"):
            imgs = []
            labels = []
            if self.before_img:
                imgs.append(self.before_img.copy())
                labels.append("BEFORE")
            if self.after_img:
                imgs.append(self.after_img.copy())
                labels.append("AFTER")
            if not imgs:
                return

            gap = int(target_w * 0.02)
            avail_w = target_w - margin * 2 - gap * (len(imgs) - 1)
            cell_w = avail_w // len(imgs)

            for i, (img, label) in enumerate(zip(imgs, labels)):
                img = self._fit_image(img, cell_w, usable_h)
                x = margin + i * (cell_w + gap) + (cell_w - img.width) // 2
                y = header_h + margin + (usable_h - img.height) // 2
                canvas.paste(img, (x, y))

                if layout == "Before | After Labels":
                    bbox = draw.textbbox((0, 0), label, font=font_label)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    label_x = x + (img.width - tw) // 2
                    label_y = y + img.height - th - int(target_h * 0.015)
                    # Semi-transparent background for label
                    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    pad = int(target_h * 0.01)
                    overlay_draw.rectangle([label_x - pad, label_y - pad,
                                            label_x + tw + pad, label_y + th + pad],
                                           fill=(0, 0, 0, 180))
                    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
                    draw = ImageDraw.Draw(canvas)
                    draw.text((label_x, label_y), label, fill=self.gold, font=font_label)

        # Header text
        if caption:
            bbox = draw.textbbox((0, 0), caption, font=font_large)
            tw = bbox[2] - bbox[0]
            draw.text(((target_w - tw) // 2, margin), caption, fill=self.gold, font=font_large)
        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_small)
            tw = bbox[2] - bbox[0]
            draw.text(((target_w - tw) // 2, margin + int(target_h * 0.055)),
                      subtitle, fill="#888", font=font_small)

        # Footer watermark
        watermark = "KC Legacy Valeting | kclegacyvaleting.co.uk"
        bbox = draw.textbbox((0, 0), watermark, font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text(((target_w - tw) // 2, target_h - footer_h - margin // 2),
                  watermark, fill="#555", font=font_small)

        # Store for export
        self._preview_canvas = canvas

        # Display in GUI
        display = canvas.copy()
        display.thumbnail((500, 500), Image.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(display)
        self.preview_lbl.config(image=self.preview_photo, text="")

    def _fit_image(self, img, max_w, max_h):
        ratio = min(max_w / img.width, max_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        return img.resize((new_w, new_h), Image.LANCZOS)

    def export_image(self):
        if not hasattr(self, "_preview_canvas") or self._preview_canvas is None:
            messagebox.showwarning("No Preview", "Create a preview first by selecting images.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            initialfile="kc_legacy_social_post.png"
        )
        if path:
            self._preview_canvas.save(path, "PNG")
            messagebox.showinfo("Exported", f"Post saved to:\n{path}")
            self.status.config(text=f"Exported: {os.path.basename(path)}")

    def copy_caption(self):
        caption = self.caption_var.get()
        hashtags = self.hashtags.get(1.0, tk.END).strip()
        full_text = f"{caption}\n\n{hashtags}"
        self.root.clipboard_clear()
        self.root.clipboard_append(full_text)
        self.status.config(text="Caption copied to clipboard!")
        messagebox.showinfo("Copied", "Caption and hashtags copied to clipboard!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SocialMediaApp(root)
    root.mainloop()
