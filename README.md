# KC Legacy Valeting

Premium automotive valeting & detailing business platform — Flask backend, customer booking app, and admin dashboard.

Live site: <https://KCLegacy.pythonanywhere.com>

---

## Project Structure

```
kc_legacy_valeting/
├── pythonanywhere_server/       # Flask backend (deployed to PythonAnywhere)
│   ├── api_server.py            # Flask API server
│   ├── requirements.txt         # Python dependencies
│   ├── uploads/                 # Booking text files, images, responses
│   └── www/                     # Static website files
│       ├── site.html            # Main website
│       ├── site.css
│       ├── site.js
│       ├── index.html           # Mobile booking page (/booking)
│       ├── app.js
│       ├── style.css
│       ├── download.html        # APK download page
│       ├── header2.jpg          # Hero banner image
│       ├── Booking.apk          # Customer Android app
│       ├── manifest.json
│       └── icons
├── customer_app/                # Capacitor Android customer app
│   ├── android/                 # Android Studio project
│   ├── capacitor.config.json
│   └── (web assets in android/app/src/main/assets/public/)
├── mobile_admin/                # Capacitor Android admin app
│   ├── android/                 # Android Studio project
│   ├── capacitor.config.json
│   └── www/                     # Web assets
├── pythonanywhere_wsgi.py       # WSGI entry point (uploaded to /var/www/)
├── upload_to_pa.py              # Deployment script (PythonAnywhere API)
└── .env                         # API credentials (gitignored)
```

---

## Components

### Flask Website (`pythonanywhere_server/`)
- **`/`** — Main website with packages, gallery, QR codes, booking form
- **`/booking`** — Mobile-optimised booking page
- **`/api/bookings`** — Create/list/delete bookings
- **`/api/quote`** — Submit quote requests
- **`/api/bookings/<filename>/response`** — Admin responses to bookings
- **`/api/bookings/ref/<ref>`** — Check booking status by reference
- **`/api/images`** — Gallery image listing
- **`/api/qr/<target>`** — QR code generation (android/web)

### Customer App (`customer_app/`)
- Capacitor Android app wrapping the mobile booking page
- Package: `com.KCLegacy.customer`
- Connects to `https://KCLegacy.pythonanywhere.com`

### Admin App (`mobile_admin/`)
- Capacitor Android PWA for managing bookings
- Package: `com.KCLegacy.admin`
- Login with admin entry name, view bookings, calendar, send responses

---

## Deployment

1. **PythonAnywhere** — Run `python upload_to_pa.py` to upload files and reload the web app
2. **Customer APK** — Build with `./gradlew assembleDebug` in `customer_app/android/`, then upload `Booking.apk` to `www/`
3. **Admin APK** — Build with `./gradlew assembleDebug` in `mobile_admin/android/`

---

## Tech Stack

- **Backend**: Flask, Flask-CORS, Pillow, qrcode
- **Hosting**: PythonAnywhere
- **Mobile**: Capacitor (Android)
- **Theme**: Black & gold premium design
