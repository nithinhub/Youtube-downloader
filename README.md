# YouTube to MP3 API — Free Backend

No API key needed. Uses **yt-dlp** (open source) + **ffmpeg** for conversion.

---

## API Endpoints

### `GET /info?url=<youtube_url>`
Returns video metadata (title, channel, duration, thumbnail).

**Example:**
```
GET https://your-api.railway.app/info?url=https://youtube.com/watch?v=dQw4w9WgXcQ
```
**Response:**
```json
{
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "Rick Astley",
  "duration": 213,
  "thumbnail": "https://..."
}
```

---

### `GET /convert?url=<url>&format=mp3&quality=192`
Downloads and converts audio. Returns the file directly.

**Params:**
| Param | Options | Default |
|-------|---------|---------|
| `url` | any YouTube URL | required |
| `format` | `mp3`, `wav`, `m4a` | `mp3` |
| `quality` | `64`, `128`, `192`, `320` | `192` |

**Example:**
```
GET https://your-api.railway.app/convert?url=https://youtube.com/watch?v=dQw4w9WgXcQ&format=mp3&quality=320
```

---

## Deploy FREE on Railway (Recommended)

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo
4. Railway auto-detects the Dockerfile and deploys
5. Copy the public URL → use it in your website

**Free tier:** 500 hours/month (enough for a personal tool)

---

## Deploy FREE on Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo
4. Set:
   - **Environment:** Docker
   - **Instance type:** Free
5. Deploy → copy the URL

---

## Connect to Your Website

Replace the API URL in your frontend JavaScript:

```javascript
const API_BASE = "https://your-api.railway.app"; // ← your deployed URL

// Fetch video info
const res = await fetch(`${API_BASE}/info?url=${encodeURIComponent(youtubeUrl)}`);
const info = await res.json();

// Download audio
window.location.href = `${API_BASE}/convert?url=${encodeURIComponent(youtubeUrl)}&format=mp3&quality=192`;
```

---

## Run Locally (for testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# Install ffmpeg (Mac)
brew install ffmpeg

# Run
python app.py
# API now at http://localhost:5000
```

---

## Notes
- Files are auto-deleted from server after 10 minutes
- Works with youtube.com, youtu.be, YouTube Shorts
- Does NOT work with private/age-restricted videos
- For personal use only — respect copyright laws
