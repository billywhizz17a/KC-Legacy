#!/usr/bin/env python3
from PIL import Image
import os

source = r"C:\Users\chris\CascadeProjects\kc_legacy_valeting\uploads\images\header2.jpg"
customer_path = r"C:\Users\chris\CascadeProjects\KC Legacey Customers\android\app\src\main\res"
admin_path = r"C:\Users\chris\CascadeProjects\KC Legacy Admin\android\app\src\main\res"

sizes = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

img = Image.open(source).convert("RGBA")

def create_icons(base_path, name):
    for folder, size in sizes.items():
        resized = img.resize((size, size), Image.LANCZOS)
        
        # Square icon
        path = os.path.join(base_path, folder, "ic_launcher.png")
        resized.save(path, "PNG")
        print(f"Saved: {path}")
        
        # Round icon
        round_path = os.path.join(base_path, folder, "ic_launcher_round.png")
        resized.save(round_path, "PNG")
        print(f"Saved: {round_path}")
    print(f"{name} icons done!")

create_icons(customer_path, "Customer")
create_icons(admin_path, "Admin")
print("All launcher icons created!")
