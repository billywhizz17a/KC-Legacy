# Deploy KC Legacy API to PythonAnywhere (Free Cloud Hosting)

## Why PythonAnywhere?
- **Free tier** available
- **24/7 uptime** — your API never sleeps
- **Python/Flask ready** — no server config needed
- **Public URL** — accessible from anywhere

---

## Step 1: Sign Up

1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online in less than a minute"
3. Create a free account (username = e.g. `kclegacy`)

---

## Step 2: Upload Your Code

### Method A: Zip Upload (Easiest)
1. On your computer, zip the entire `kc_legacy_valeting` folder:
   ```
   Right-click folder → Send to → Compressed (zipped) folder
   ```
2. In PythonAnywhere:
   - Go to **Files** tab
   - Click **Upload a file**
   - Upload `kc_legacy_valeting.zip`
3. Open a **Bash console** (Consoles tab → Bash)
   ```bash
   unzip kc_legacy_valeting.zip
   ```

### Method B: Git Clone (If you use Git)
```bash
git clone YOUR_REPO_URL
```

---

## Step 3: Install Dependencies

Open a **Bash console** and run:
```bash
cd ~/kc_legacy_valeting
pip install -r requirements.txt
```

---

## Step 4: Configure WSGI

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** → **Python 3.11**
4. In the WSGI configuration file section, click the link to edit
5. **Replace ALL the code** with the content from `pythonanywhere_wsgi.py` in your project
6. **Important**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username

Example:
```python
import sys
PROJECT_PATH = '/home/kclegacy/kc_legacy_valeting'
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

from api_server import app as application
```

7. Click **Save**

---

## Step 5: Configure Static Files (For Images)

1. In the **Web** tab, under **Static files**
2. Click **Enter URL** and type: `/uploads/images/`
3. Click **Enter path** and type: `/home/YOUR_USERNAME/kc_legacy_valeting/uploads/images/`
4. Add another:
   - URL: `/uploads/text/`
   - Path: `/home/YOUR_USERNAME/kc_legacy_valeting/uploads/text/`

---

## Step 6: Reload the App

1. In the **Web** tab
2. Click **Reload** button
3. Your API is now live at:
   ```
   https://YOUR_USERNAME.pythonanywhere.com/api/health
   ```
   (Replace YOUR_USERNAME with your actual username)

---

## Step 7: Test the API

Open this URL in your browser:
```
https://YOUR_USERNAME.pythonanywhere.com/api/health
```

You should see:
```json
{"status":"ok","service":"KC Legacy Valeting API"}
```

---

## Step 8: Update the Admin App

In your **mobile admin app login screen**, enter:
```
https://YOUR_USERNAME.pythonanywhere.com
```

**Save** — the app remembers it for next time.

---

## Your Public API Endpoints

| Endpoint | URL |
|----------|-----|
| Health | `https://YOUR_USERNAME.pythonanywhere.com/api/health` |
| Bookings | `https://YOUR_USERNAME.pythonanywhere.com/api/bookings` |
| Images | `https://YOUR_USERNAME.pythonanywhere.com/api/images` |
| Banner | `https://YOUR_USERNAME.pythonanywhere.com/api/banner` |

---

## Important Notes

### Free Tier Limits:
- API stays awake for **3 months** from last visit
- If inactive, it sleeps (visits wake it up in ~10 seconds)
- **Hack**: Set a phone alarm to visit the URL once a month

### Uploading Existing Data:
Your current bookings and images are on your local computer. To move them:
1. Zip your local `uploads/` folder
2. Upload via PythonAnywhere Files tab
3. Unzip in the Bash console

### Security:
- The API has NO authentication (by design — customers need to submit bookings)
- The admin app uses the entry name `kclvs417xh` for login
- Anyone with the API URL can see bookings/images
- For production, consider adding API key authentication

---

## Troubleshooting

**"Internal Server Error"**
- Check **Web → Error log** for details
- Usually means a missing dependency: run `pip install -r requirements.txt` again

**"404 Not Found"**
- Make sure WSGI file path matches your actual project location
- Check the `sys.path.insert()` line has the correct username

**Images not showing**
- Verify static files are configured in Web tab
- Check file paths in the PythonAnywhere console

---

## Alternative: Paid Tier
If you need 24/7 uptime without sleeping:
- PythonAnywhere Hacker plan: $5/month
- Or use Render (free, no sleep): https://render.com

---

Ready to go live! 🚀
