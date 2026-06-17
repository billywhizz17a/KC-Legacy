# ✨ KC Legacy Valeting - Premium Automotive Care Portal

Welcome to the official, offline, local-first web application for **KC Legacy Valeting**. This luxury portal serves as both an interactive landing page for customers and a complete booking & content management system for business administrators.

---

## 📂 Created Project Structure

Your business directories have been automatically created and structured as requested:

- 📂 `c:\Users\chris\CascadeProjects\kc_legacy_valeting\` — Root project folder
- 📂 `c:\Users\chris\CascadeProjects\kc_legacy_valeting\uploads\text\` — Storage for book logs, bookings, and special instructions text files
- 📂 `c:\Users\chris\CascadeProjects\kc_legacy_valeting\uploads\images\` — Storage for before-and-after detailing images and vehicle condition shots

---

## 🎨 Premium Features

- **🏠 Luxury Home & Packages**: High-end black & gold themed display for valeting packages (Bronze, Silver, Gold, and Platinum).
- **📅 Smart Booking System**: Generates custom UUID-linked text files and stores them instantly under `uploads/text/`.
- **📸 Before & After Image Uploader**: Allows uploading and auto-timestamping car progress photos straight into `uploads/images/`.
- **📁 Legacy Management Dashboard**: Allows reading, reviewing, and deleting active bookings and photo galleries completely offline.

---

## 🚀 How to Launch Your Website

Since you already have Python and Streamlit installed, launching the website takes less than 3 seconds!

1. **Open your Terminal (PowerShell)**.
2. **Run this command**:
   ```bash
   streamlit run c:\Users\chris\CascadeProjects\kc_legacy_valeting\app.py
   ```
3. A gorgeous interactive window will automatically open in your web browser at:
   `http://localhost:8501`

---

---

## 📱 Progressive Web App (PWA)

The app is configured as a PWA, allowing customers to install it on their phone's home screen:

- **Android**: Tap the "Install App" button on the homepage
- **iPhone**: Tap Share → Add to Home Screen in Safari

Files:
- `manifest.json` — App configuration (name, icons, theme)
- `pwa_icons/` — App icons (192×192 and 512×512)

---

## 🌐 Deploy to Streamlit Cloud (Public Website)

To make the app accessible to customers via a public URL:

1. **Create a GitHub repository** (free at github.com)
2. **Upload these files to the repo**:
   - `app.py`
   - `requirements.txt`
   - `manifest.json`
   - `pwa_icons/` folder
3. **Go to** [share.streamlit.io](https://share.streamlit.io)
4. **Connect your GitHub repo** → Click Deploy
5. **Your public URL** will be: `https://kclegacy.streamlit.app` (or similar)

Once deployed, share this link on Facebook — customers tap it and can install the app instantly.

---

## 🔐 Admin Access

Type the admin password in the sidebar to unlock the **Admin Dashboard** and view all bookings.

*Enjoy managing your luxury automotive business!*
