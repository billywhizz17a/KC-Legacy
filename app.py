import streamlit as st
import os
import uuid
import datetime
import hashlib
import io
import base64
import qrcode
import json
import urllib.request
from collections import defaultdict
from PIL import Image

# Define Storage Folders
if os.path.exists(r"c:\Users\chris\CascadeProjects\kc_legacy_valeting"):
    BASE_DIR = r"c:\Users\chris\CascadeProjects\kc_legacy_valeting"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "text")
IMAGE_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "images")

# API Server URL (PythonAnywhere) - use localhost when running on server
if os.path.exists("/home/kclegeacy"):
    API_BASE_URL = "http://127.0.0.1:5000"
else:
    API_BASE_URL = "https://kclegeacy.pythonanywhere.com"

def send_booking_to_api(booking_data):
    """Send booking to PythonAnywhere (PRIMARY system)."""
    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/api/bookings",
            data=json.dumps(booking_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception:
        return False


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

# Load Favicon if it exists
favicon_path = os.path.join(IMAGE_UPLOADS_DIR, "hero", "favicon.png")
page_icon = "✨"
if os.path.exists(favicon_path):
    try:
        page_icon = Image.open(favicon_path)
    except Exception:
        pass

# Setup Page Configurations
st.set_page_config(
    page_title="KC Legacy Valeting - Premium Car Detailing",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PWA Meta Tags ──
st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#d4af37">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="KC Legacy">
""", unsafe_allow_html=True)

# Create directories if they don't exist
os.makedirs(TEXT_UPLOADS_DIR, exist_ok=True)
os.makedirs(IMAGE_UPLOADS_DIR, exist_ok=True)

# ── Header Banner ──
header_path = os.path.join(IMAGE_UPLOADS_DIR, "header2.jpg")
if os.path.exists(header_path):
    st.image(header_path, use_container_width=True)

# Custom Styling (Black, Gold, and Deep Obsidian Premium Theme)
st.markdown("""
<style>
    /* Hide password visibility toggle (eye icon) */
    button[title="View password"] {
        display: none !important;
    }

    /* Styling the Main Background and Text */
    .stApp {
        background-color: #0d0d0d;
        color: #e6e6e6;
    }

    /* Remove the white band: Streamlit top header/toolbar */
    [data-testid="stHeader"] {
        background-color: #0d0d0d !important;
        background: transparent !important;
    }
    [data-testid="stToolbar"] {
        background-color: #0d0d0d !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    /* Remove default top padding gap above content */
    [data-testid="stAppViewContainer"] > .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
    }
    
    /* Elegant Title and Header styling */
    .gold-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #d4af37; /* Metallic Gold */
        text-align: center;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: #b3b3b3;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    
    /* Luxury Card Containers */
    .luxury-card {
        background-color: #1a1a1a;
        border: 1px solid #d4af37;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
        transition: transform 0.3s;
        height: 860px;
        display: flex;
        flex-direction: column;
    }
    .luxury-card p:last-of-type {
        flex: 1;
        overflow-y: auto;
    }
    .luxury-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
    }
    
    /* Addon Card Containers */
    .addon-card {
        background-color: #1a1a1a;
        border: 1px solid #d4af37;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
        transition: transform 0.3s;
        height: 180px; /* Fixed height for exact same size */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-sizing: border-box;
    }
    .addon-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
    }
    
    /* Button Custom Colors */
    .stButton>button {
        background-color: #d4af37 !important;
        color: #0d0d0d !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #f3e5ab !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Fix grey form labels and inputs */
    [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
    }
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    [data-testid="stCheckbox"] label {
        color: #ffffff !important;
    }
    [data-testid="stCheckbox"] p {
        color: #ffffff !important;
    }
    
    /* ── Sidebar Dark Theme ── */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid rgba(212, 175, 55, 0.15) !important;
        min-height: 100vh !important;
        height: 100% !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 10px !important;
        min-height: 100vh !important;
    }
    /* Match sidebar content wrapper height to full viewport */
    [data-testid="stSidebarContent"] {
        min-height: 100vh !important;
        background-color: #0a0a0a !important;
    }
    /* ── Premium Navigation Menu ── */
    [data-testid="stSidebar"] .stRadio {
        margin-top: 10px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 8px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: #151515 !important;
        border: 2px solid rgba(212, 175, 55, 0.6) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin: 0 !important;
        width: 260px !important;
        height: auto !important;
        text-align: left !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        white-space: nowrap !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: #1a1a1a !important;
        border-color: rgba(212, 175, 55, 0.5) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 2px 8px rgba(212, 175, 55, 0.15) !important;
    }
    /* Selected/active nav item */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[aria-checked="true"] {
        background-color: rgba(212, 175, 55, 0.12) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 0 12px rgba(212, 175, 55, 0.2) !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span {
        border-color: #666 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[aria-checked="true"] span {
        border-color: #d4af37 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span svg {
        fill: #d4af37 !important;
    }
    /* Hide the actual radio circle */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span:first-child {
        display: none !important;
    }
    /* Nav text */
    [data-testid="stSidebar"] .stRadio p {
        color: #e6e6e6 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label[aria-checked="true"] p {
        color: #d4af37 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Header ──
st.sidebar.markdown("""
<div style="text-align: center; padding: 25px 15px 20px 15px; background-color: #111; border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 12px; margin: 10px;">
    <h2 style="color: #d4af37; font-weight: 900; letter-spacing: 3px; margin: 0; font-size: 1.4rem;">KC LEGACY</h2>
    <p style="color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 4px; margin: 6px 0 0 0;">Valeting & Detailing</p>
    <div style="width: 40px; height: 2px; background-color: #d4af37; margin: 12px auto 0 auto;"></div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='color: #555; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 3px; text-align: center; margin: 15px 0 10px 0;'>Navigation</p>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["🏠 Home & Packages", "📅 Book a Session", "📸 Our Work"], label_visibility="collapsed")

# ── Service Info Box ──
st.sidebar.markdown("""
<div style="margin-top: 30px; padding: 18px; background-color: #111; border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; margin: 30px 10px 0 10px;">
    <p style="color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 10px 0;">Service Area</p>
    <p style="color: #e6e6e6; font-size: 0.9rem; margin: 0; font-weight: 500;">Covering Chesterfield & Surrounding Area</p>
    <div style="width: 100%; height: 1px; background-color: rgba(212, 175, 55, 0.15); margin: 12px 0;"></div>
    <p style="color: #d4af37; font-size: 1.05rem; font-weight: 700; margin: 0;">📞 07969 168246</p>
    <p style="color: #555; font-size: 0.8rem; margin: 8px 0 0 0;">Mon - Sat: 8:00 AM - 6:00 PM</p>
</div>
""", unsafe_allow_html=True)

# ── Social Media ──
st.sidebar.markdown("""
<div style="margin-top: 15px; padding: 12px; text-align: center; background-color: #111; border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; margin: 15px 10px 0 10px;">
    <p style="color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 8px 0;">Follow Us</p>
    <a href="https://www.facebook.com/share/14eKaS4FaLL" target="_blank" style="color: #d4af37; text-decoration: none; font-weight: 600; font-size: 0.9rem;">Facebook</a>
</div>
""", unsafe_allow_html=True)

# 🏠 HOME & PACKAGES PAGE
if menu == "🏠 Home & Packages":
    st.markdown("<h1 class='gold-header'>KC Legacy Valeting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>The Ultimate Standard in Luxury Automotive Care</p>", unsafe_allow_html=True)
    
    # ── Company Message ──
    st.markdown("""
    <div style="margin: 30px 0; padding: 25px; background-color: #111; border: 2px solid #d4af37; border-radius: 12px;">
        <p style="color: #d4af37; font-size: 1.1rem; font-weight: 700; margin: 0 0 15px 0; text-align: center;">Our Promise to You</p>
        <p style="color: #ccc; font-size: 0.95rem; line-height: 1.7; margin: 0; text-align: center;">
            At KC Valeting, we understand that every vehicle is different and that the condition of each car can vary greatly. Your expectations and satisfaction are extremely important to us.
        </p>
        <p style="color: #ccc; font-size: 0.95rem; line-height: 1.7; margin: 15px 0 0 0; text-align: center;">
            During all enquiries and bookings, we will assess your vehicle and discuss the results you are hoping to achieve. If the package you have chosen is unlikely to deliver the outcome you want, we will explain this honestly and recommend the most suitable options.
        </p>
        <p style="color: #ccc; font-size: 0.95rem; line-height: 1.7; margin: 15px 0 0 0; text-align: center;">
            We are happy to customise and adapt our services to meet your individual needs and budget. We also welcome any questions you may have, ensuring we fully understand your expectations so we can provide the best possible service and achieve the results you're looking for.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Generate QR codes as base64
    android_url = "https://kclegeacy.pythonanywhere.com/app-debug.apk"
    qr_a = qrcode.QRCode(version=1, box_size=5, border=2)
    qr_a.add_data(android_url)
    qr_a.make(fit=True)
    img_a = qr_a.make_image(fill_color="black", back_color="white")
    buf_a = io.BytesIO()
    img_a.save(buf_a, format="PNG")
    qr_a_b64 = base64.b64encode(buf_a.getvalue()).decode()

    web_url = "https://kclegeacy.pythonanywhere.com"
    qr_i = qrcode.QRCode(version=1, box_size=5, border=2)
    qr_i.add_data(web_url)
    qr_i.make(fit=True)
    img_i = qr_i.make_image(fill_color="black", back_color="white")
    buf_i = io.BytesIO()
    img_i.save(buf_i, format="PNG")
    qr_i_b64 = base64.b64encode(buf_i.getvalue()).decode()

    # ── Install App CTA with QR codes inside one card ──
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #111; border: 2px solid #d4af37; border-radius: 12px;">
        <p style="color: #d4af37; font-size: 1.1rem; font-weight: 700; margin: 0 0 10px 0;">📱 Get the KC Legacy App</p>
        <p style="color: #ccc; font-size: 0.9rem; margin: 0 0 20px 0;">Scan the QR code with your phone camera</p>
        <table style="width:100%; border-collapse: collapse;">
            <tr>
                <td style="width:50%; text-align:center; vertical-align:top; padding: 10px;">
                    <p style="color:#d4af37; font-weight:700; margin:0 0 5px 0;">🤖 Android</p>
                    <p style="color:#ccc; font-size:0.85rem; margin:0 0 10px 0;">Scan to download APK</p>
                    <img src="data:image/png;base64,{qr_a_b64}" width="200" style="display:block; margin:0 auto;">
                </td>
                <td style="width:50%; text-align:center; vertical-align:top; padding: 10px;">
                    <p style="color:#d4af37; font-weight:700; margin:0 0 5px 0;">� Website</p>
                    <p style="color:#ccc; font-size:0.85rem; margin:0 0 10px 0;">Scan to visit booking site</p>
                    <img src="data:image/png;base64,{qr_i_b64}" width="200" style="display:block; margin:0 auto;">
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#d4af37; text-align:center; margin: 40px 0;'>Select Your Detail Package</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="luxury-card">
            <h3 style="color:#d4af37; margin-top:0; font-size:1.3rem; line-height:1.2;">🫧 Express Mini Valet</h3>
            <p style="color: #888; font-size: 0.8rem; margin-top:-5px; min-height:36px;">Quick maintenance clean for busy customers.</p>
            <p style="font-size: 1.5rem; font-weight:bold; color: #fff; margin-top:10px;">£35 / £45</p>
            <p style="color: #aaa; font-size: 0.85rem; min-height: 0;">
                <b>What's Included:</b><br>
                • All rubbish removed<br>
                &nbsp;&nbsp;(remove valuables — I do the rest)<br>
                • Snow foam pre-wash<br>
                • Two bucket hand wash<br>
                • Wheel face clean only<br>
                • Tyre shine and protect<br>
                • Interior vacuum including boot<br>
                • Dashboard & all plastics dusted<br>
                • Windows cleaned inside and outside<br>
                <br><b style="color:#d4af37;">✨ Add Ons Available Below</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="luxury-card">
            <h3 style="color:#d4af37; margin-top:0; font-size:1.3rem; line-height:1.2;">✨ Legacy Revival - Full Valet</h3>
            <p style="color: #888; font-size: 0.8rem; margin-top:-5px; min-height:36px;">Full inside and out clean for a refreshed feel.</p>
            <p style="font-size: 1.5rem; font-weight:bold; color: #fff; margin-top:10px;">£80 / £100</p>
            <p style="color: #aaa; font-size: 0.85rem; min-height: 0;">
                <b>What's Included:</b><br>
                • All rubbish removed<br>
                &nbsp;&nbsp;(remove valuables — I do the rest)<br>
                • Snow foam pre-wash<br>
                • Two bucket hand wash<br>
                • Door shuts & rain drains deep cleaned<br>
                • Windows cleaned inside and outside<br>
                • Tyre shine / protected<br>
                • Deep wheel clean<br>
                • Exterior plastics dressed (if applicable)<br>
                • Dashboard & all plastics including doors, dusted and shampooed (special brushes)<br>
                • Interior hand-applied plastic protection incl. dashboard & door cards (special brushes)<br>
                • Cup holders & trims hoovered and cleaned<br>
                • Full vacuum including boot<br>
                • Carpets hand shampooed<br>
                • Seats hand shampooed<br>
                • Leather cleaned (if applicable)<br>
                • Car mats deep cleaned and protected<br>
                • All visible headliner stains removed<br>
                <br><b style="color:#d4af37;">✨ Add Ons Available Below</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="luxury-card">
            <h3 style="color:#d4af37; margin-top:0; font-size:1.3rem; line-height:1.2;">💎 Legacy Elite - Showroom Stopper</h3>
            <p style="color: #888; font-size: 0.8rem; margin-top:-5px; min-height:36px;">For customers wanting that showroom feel.</p>
            <p style="font-size: 1.5rem; font-weight:bold; color: #fff; margin-top:10px;">£200 / £240</p>
            <p style="color: #aaa; font-size: 0.85rem; min-height: 0;">
                <b>What's Included:</b><br>
                • All rubbish removed<br>
                &nbsp;&nbsp;(remove valuables — I do the rest)<br>
                • Snow foam pre-wash<br>
                • Two bucket hand wash<br>
                • Exterior full iron fallout and clay bar treatment<br>
                &nbsp;&nbsp;(removes light surface scratches & swirls)<br>
                • Machine polish exterior paintwork<br>
                &nbsp;&nbsp;(deepening the shine of your paintwork)<br>
                • Finished with Ceramic Wax spray<br>
                • Coating of ceramic wax spray to provide<br>
                &nbsp;&nbsp;UV protection, water beading (hydrophobicity) —<br>
                &nbsp;&nbsp;Providing the same classic warm, deep, wet-look<br>
                &nbsp;&nbsp;shine as Carnauba waxes — can last up to 12 months<br>
                • Upgraded deep wheel clean<br>
                • Tyre shine / protected<br>
                • Door shuts & rain drains deep cleaned<br>
                • Exterior plastics dressed (if required)<br>
                • Full carpet interior shampoo and extraction<br>
                • Full carpet interior protection<br>
                • Full interior vacuum including boot, door cards,<br>
                &nbsp;&nbsp;cup holders and glove box<br>
                • Interior hand-applied plastic protection<br>
                &nbsp;&nbsp;including door cards<br>
                • Leather treatment (if required)<br>
                • Seats shampooed and extraction<br>
                • Cup holders & trims cleaned<br>
                • Headliner spot cleaned (if required)<br>
                <br><b style="color:#d4af37;">✨ Add Ons Available Below</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # Optional Add-Ons Section
    st.markdown("<h2 style='color:#d4af37; text-align:center; margin: 50px 0 20px 0;'>✨ Optional Add-Ons (Available with Any Valet)</h2>", unsafe_allow_html=True)
    
    # Row 1
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🐾 Pet Hair Removal</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">From £15</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Complete removal of stubborn pet hair from carpets, seats, and boot areas.</p>
        </div>
        """, unsafe_allow_html=True)
    with row1_col2:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🔒 Engine Bay Wipe Down</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£8</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Wipe down and dressing of all engine bay plastics and covers.</p>
        </div>
        """, unsafe_allow_html=True)
    with row1_col3:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🔒 Interior Steam Sanitisation</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£10</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">High-temperature deep steam cleaning to sanitise vents and touchpoints.</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Row 2
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    with row2_col1:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🧲 Iron Fallout & Clay Bar</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£30</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Chemical iron de-contamination and mechanical clay bar treatment for silky-smooth paint.</p>
        </div>
        """, unsafe_allow_html=True)
    with row2_col2:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">💿 Machine Polish & Ceramic Wax</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£130</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Machine polish exterior paintwork finished with Ceramic Wax spray for UV protection and hydrophobicity.</p>
        </div>
        """, unsafe_allow_html=True)
    with row2_col3:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">☁️ Headliner Stain Removal</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">From £10</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Delicate hand-cleansing to remove grease marks and stains from roof lining.</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Row 3
    row3_col1, row3_col2, row3_col3 = st.columns(3)
    with row3_col1:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🔒 Carpet Extraction Clean</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£25</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Full carpet shampooed and extraction including boot for a deeper clean.</p>
        </div>
        """, unsafe_allow_html=True)
    with row3_col2:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">🔒 Seat Shampoo & Extraction</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£25</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">All seats shampooed and extraction for a thorough deep clean.</p>
        </div>
        """, unsafe_allow_html=True)
    with row3_col3:
        st.markdown("""
        <div class="addon-card">
            <h4 style="color:#d4af37; margin:0 0 10px 0;">👶 Child Seat Sanitisation</h4>
            <p style="color:#fff; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">£10</p>
            <p style="color:#888; font-size:0.85rem; margin:0;">Anti-bacterial steam cleaning and sanitisation of baby/child car seats.</p>
        </div>
        """, unsafe_allow_html=True)

# 📅 BOOK A SESSION (TEXT UPLOAD FOLDER)
elif menu == "📅 Book a Session":
    st.markdown("<h1 class='gold-header'>Book Your Detailing Session</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Reserve your spot in just a few clicks</p>", unsafe_allow_html=True)
    
    st.write("Fill out your booking details below. You'll receive a unique booking reference to track your appointment and see messages from us.")
    
    # ── Booking Form (all inputs commit together on submit) ──
    with st.form("booking_form", clear_on_submit=False):
        # ── Customer Details ──
        st.markdown("<h3 style='color:#d4af37; margin-top:20px;'>Your Details</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. John Doe")
            phone = st.text_input("Phone Number", placeholder="e.g. 07123 456789")
        with col2:
            email = st.text_input("Email Address", placeholder="e.g. john@example.com")
            car_reg = st.text_input("Registration (optional)", placeholder="e.g. AB12 CDE")
        car_make = st.text_input("Car Make & Model", placeholder="e.g. BMW M4")

        # ── Date ──
        st.markdown("<h3 style='color:#d4af37; margin-top:20px;'>Preferred Date</h3>", unsafe_allow_html=True)
        booking_date = st.date_input("Select Date", min_value=datetime.date.today(), label_visibility="collapsed")

        # ── Package Selection ──
        st.markdown("<h3 style='color:#d4af37; margin-top:20px;'>Select Package</h3>", unsafe_allow_html=True)
        package_col1, package_col2, package_col3 = st.columns(3)

        with package_col1:
            pkg_refresh = st.checkbox("Express Mini Valet - £35")
        with package_col2:
            pkg_revival = st.checkbox("Legacy Revival - £80")
        with package_col3:
            pkg_elite = st.checkbox("Legacy Elite - £200")

        package_prices = {"Express Mini Valet": 35, "Legacy Revival": 80, "Legacy Elite": 200}
        selected_package = None
        package_price = 0
        if pkg_refresh:
            selected_package = "Express Mini Valet"
            package_price = 35
        elif pkg_revival:
            selected_package = "Legacy Revival"
            package_price = 80
        elif pkg_elite:
            selected_package = "Legacy Elite"
            package_price = 200
        else:
            selected_package = "Express Mini Valet"
            package_price = 35

        # ── Add-Ons ──
        st.markdown("<h3 style='color:#d4af37; margin-top:20px;'>Optional Add-Ons</h3>", unsafe_allow_html=True)
        addon_col1, addon_col2, addon_col3 = st.columns(3)

        addon_prices = {
            "Pet Hair Removal": 15,
            "Engine Bay Wipe Down": 8,
            "Interior Steam Sanitisation": 10,
            "Iron Fallout & Clay Bar": 30,
            "Machine Polish & Ceramic Wax": 130,
            "Headliner Stain Removal": 10,
            "Carpet Extraction Clean": 25,
            "Seat Shampoo & Extraction": 25,
            "Child Seat Sanitisation": 10
        }

        selected_addons = []
        with addon_col1:
            if st.checkbox("Pet Hair Removal +£15"): selected_addons.append("Pet Hair Removal")
            if st.checkbox("Engine Bay Wipe Down +£8"): selected_addons.append("Engine Bay Wipe Down")
            if st.checkbox("Interior Steam Sanitisation +£10"): selected_addons.append("Interior Steam Sanitisation")
        with addon_col2:
            if st.checkbox("Iron Fallout & Clay Bar +£30"): selected_addons.append("Iron Fallout & Clay Bar")
            if st.checkbox("Machine Polish & Ceramic Wax +£130"): selected_addons.append("Machine Polish & Ceramic Wax")
            if st.checkbox("Headliner Stain Removal +£10"): selected_addons.append("Headliner Stain Removal")
        with addon_col3:
            if st.checkbox("Carpet Extraction Clean +£25"): selected_addons.append("Carpet Extraction Clean")
            if st.checkbox("Seat Shampoo & Extraction +£25"): selected_addons.append("Seat Shampoo & Extraction")
            if st.checkbox("Child Seat Sanitisation +£10"): selected_addons.append("Child Seat Sanitisation")

        # ── Special Requests ──
        st.markdown("<h3 style='color:#d4af37; margin-top:20px;'>Special Instructions</h3>", unsafe_allow_html=True)
        special_requests = st.text_area("Notes", placeholder="Any special requests...", label_visibility="collapsed")

        # ── Quote Calculator ──
        addons_total = sum(addon_prices[a] for a in selected_addons)
        total_price = package_price + addons_total

        st.markdown(f"""
        <div style="background: rgba(212, 175, 55, 0.05); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; padding: 18px; text-align: center; margin: 20px 0;">
            <div style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 2px;">Estimated Price</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #d4af37; margin: 8px 0;">&pound;{total_price}</div>
            <div style="font-size: 0.8rem; color: #888;">{selected_package}: &pound;{package_price}{'' if not selected_addons else ' + Add-ons: &pound;' + str(addons_total)}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Submit ──
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            update_quote = st.form_submit_button("📊 UPDATE QUOTE", use_container_width=True)
        with col_btn2:
            book_now = st.form_submit_button("🎉 BOOK NOW", use_container_width=True)

        if book_now:
            if not name or not car_make:
                st.error("Please provide both your name and car model to submit your booking.")
            else:
                booking_id = str(uuid.uuid4())[:8]
                filename = f"booking_{booking_id}_{name.replace(' ', '_')}.txt"
                file_path = os.path.join(TEXT_UPLOADS_DIR, filename)
                
                addons_str = "\n".join([f"  - {a} (+£{addon_prices[a]})" for a in selected_addons]) if selected_addons else "  None"
                
                booking_content = f"""=============================================
             KC LEGACY VALETING BOOKING
=============================================
Booking ID: {booking_id}
Submission Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---------------------------------------------
CUSTOMER INFORMATION:
Name: {name}
Phone: {phone}
Email: {email}

VEHICLE & PACKAGE DETAILS:
Vehicle: {car_make}
Registration: {car_reg or 'N/A'}
Selected Package: {selected_package} (From £{package_price})
Scheduled Date: {booking_date}

ADD-ONS INCLUDED:
{addons_str}

SPECIAL REQUESTS:
{special_requests or 'None'}

ESTIMATED TOTAL: £{total_price}
=============================================
"""
                # Send to PythonAnywhere FIRST (primary system)
                api_data = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "carMake": car_make,
                    "carReg": car_reg or "N/A",
                    "package": selected_package,
                    "packagePrice": package_price,
                    "date": str(booking_date),
                    "addons": selected_addons,
                    "totalPrice": total_price,
                    "specialRequests": special_requests or "None",
                    "bookingId": booking_id,
                    "bookingContent": booking_content
                }
                api_sent = send_booking_to_api(api_data)

                if api_sent:
                    # Save locally as backup
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(booking_content)
                    except Exception:
                        pass
                    st.session_state["booking_ref_input"] = booking_id
                    st.success(f"🎉 Booking Confirmed! Your reference is #{booking_id}")
                    st.info("✅ We've filled your reference into 'Check Your Booking' below. Save it to see updates and messages from us at any time.")
                    st.balloons()
                else:
                    # Fallback to local save if API fails
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(booking_content)
                        st.session_state["booking_ref_input"] = booking_id
                        st.warning(f"⚠️ Booking saved locally. Will sync to admin app — reference: #{booking_id}. You can still check status below once synced.")
                    except Exception as e:
                        st.error(f"❌ Booking failed: {e}")

    # ── Check Your Booking ──
    st.markdown("<hr style='border-color: #d4af37; margin: 40px 0 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37; text-align:center;'>🔍 Check Your Booking</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; text-align:center; font-size:0.9rem;'>Enter your booking reference to see updates and messages from us.</p>", unsafe_allow_html=True)

    if "booking_ref_input" not in st.session_state:
        st.session_state["booking_ref_input"] = ""

    ref_col1, ref_col2 = st.columns([3, 1])
    with ref_col1:
        booking_ref = st.text_input("Booking Reference", placeholder="e.g. a3b7c9d2", label_visibility="collapsed", key="booking_ref_input")
    with ref_col2:
        check_btn = st.button("Check Status", use_container_width=True)

    if check_btn and booking_ref:
        ref = booking_ref.strip().replace('#', '').lower()
        try:
            req = urllib.request.Request(f"{API_BASE_URL}/api/bookings/ref/{ref}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data.get("found"):
                st.success(f"✅ Booking found! Reference: #{ref}")

                # Show booking details
                content = data.get("content", "")
                lines = content.split('\n')
                detail_lines = []
                for line in lines:
                    if line.startswith(('Name:', 'Phone:', 'Email:', 'Vehicle:', 'Registration:', 'Selected Package:', 'Scheduled Date:', 'ESTIMATED TOTAL:')):
                        detail_lines.append(line)
                if detail_lines:
                    st.markdown("""
                    <div style="background:#1a1a1a; border:1px solid rgba(212,175,55,0.2); border-radius:10px; padding:15px; margin:10px 0;">
                        <p style="color:#d4af37; font-weight:bold; margin-bottom:10px;">📋 Your Booking Details</p>
                    """ + "".join([f'<p style="color:#ccc; font-size:0.9rem; margin:4px 0;">{l}</p>' for l in detail_lines]) + """
                    </div>
                    """, unsafe_allow_html=True)

                # Show admin responses
                responses = data.get("responses", [])
                if responses:
                    st.markdown("<p style='color:#d4af37; font-weight:bold; margin-top:15px;'>📨 Messages from KC Legacy</p>", unsafe_allow_html=True)
                    for r in responses:
                        status_color = "#4caf50" if r.get("status") == "confirmed" else "#ff9800" if r.get("status") == "reschedule" else "#2196f3"
                        status_text = r.get("status", "pending").capitalize()
                        st.markdown(f"""
                        <div style="background:#1a1a1a; border-left:3px solid {status_color}; border-radius:8px; padding:12px; margin:8px 0;">
                            <p style="color:{status_color}; font-size:0.8rem; font-weight:bold; margin-bottom:4px;">{status_text} — {r.get('timestamp', '')}</p>
                            <p style="color:#ccc; font-size:0.9rem; margin:0;">{r.get('message', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No messages yet. We'll update you here once we review your booking.")
            else:
                st.error("❌ Booking not found. Double-check your reference number.")
        except Exception as e:
            st.error(f"❌ Could not check booking: {e}")

# 📸 OUR WORK (GALLERY)
elif menu == "📸 Our Work":
    st.markdown("<h1 class='gold-header'>Our Work</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>See the KC Legacy transformation</p>", unsafe_allow_html=True)

    # ── Gallery: Show Existing Images ──
    st.markdown("<hr style='border-color: #d4af37; margin: 40px 0 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#d4af37; text-align:center; margin-bottom:20px;'>📸 Our Work</h2>", unsafe_allow_html=True)

    # Exclude logos, icons, headers, test files, and corrupted filenames
    excluded_names = {"facebook_logo", "favicon", "header2", "kclegacy", "product", "kclecy"}
    def _is_real_photo(filename):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return False
        base = filename.rsplit(".", 1)[0].lower()
        # Skip known non-photos by partial name match
        for ex in excluded_names:
            if ex in base:
                return False
        # Skip weird names like j.jpeg, jj.jpeg, jjjjjjjjjjjjj.jpeg
        # (anything that is only repeated letters like j, g, k)
        stripped = base.replace("j", "").replace("g", "").replace("k", "").strip()
        if stripped == "" or (len(base) >= 2 and len(set(base)) <= 2):
            return False
        return True
    image_files = sorted([f for f in os.listdir(IMAGE_UPLOADS_DIR) if _is_real_photo(f)])

    def _render_uniform_image(img_path):
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
                    _render_uniform_image(os.path.join(IMAGE_UPLOADS_DIR, image_files[idx + 1]))








