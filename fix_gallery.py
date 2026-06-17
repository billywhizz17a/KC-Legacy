#!/usr/bin/env python3
import io

with open(r'C:\Users\chris\CascadeProjects\kc_legacy_valeting\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    if not image_files:
        st.info("No images uploaded yet. Be the first to share your before & after!")
    else:
        # Flat 2-column grid - all images
        for idx in range(0, len(image_files), 2):
            c1, c2 = st.columns(2)
            # First image
            if idx < len(image_files):
                with c1:
                    st.image(os.path.join(IMAGE_UPLOADS_DIR, image_files[idx]), use_container_width=True)
            # Second image
            if idx + 1 < len(image_files):
                with c2:
                    st.image(os.path.join(IMAGE_UPLOADS_DIR, image_files[idx + 1]), use_container_width=True)'''

new = '''    def _render_uniform_image(img_path):
        img = Image.open(img_path)
        img = img.convert("RGB")
        w, h = img.size
        target_ratio = 4 / 3
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        elif current_ratio < target_ratio:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        img = img.resize((600, 450), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(f"""
        <div style="border: 3px solid #d4af37; border-radius: 10px; overflow: hidden; margin-bottom: 20px;">
            <img src="data:image/jpeg;base64,{b64}" style="width: 100%; height: auto; display: block;">
        </div>
        """, unsafe_allow_html=True)

    if not image_files:
        st.info("No images uploaded yet. Be the first to share your before & after!")
    else:
        # Uniform 2-column grid with gold borders
        for idx in range(0, len(image_files), 2):
            c1, c2 = st.columns(2)
            if idx < len(image_files):
                with c1:
                    _render_uniform_image(os.path.join(IMAGE_UPLOADS_DIR, image_files[idx]))
            if idx + 1 < len(image_files):
                with c2:
                    _render_uniform_image(os.path.join(IMAGE_UPLOADS_DIR, image_files[idx + 1]))'''

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\chris\CascadeProjects\kc_legacy_valeting\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Old text not found')
