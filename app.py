from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid
import threading
import time
import re

app = Flask(__name__)
CORS(app)  # Allow requests from your website

DOWNLOAD_DIR = "/tmp/yt_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Auto-delete files after 10 minutes
def delete_file_later(path, delay=600):
    def _delete():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=_delete, daemon=True).start()

def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip()[:80]

# ─── GET VIDEO INFO (title, duration, thumbnail) ───────────────────────
@app.route("/info", methods=["GET"])
def get_info():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title", "Unknown"),
                "channel": info.get("uploader", "Unknown"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
                "view_count": info.get("view_count", 0),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── CONVERT & DOWNLOAD ─────────────────────────────────────────────────
@app.route("/convert", methods=["GET"])
def convert():
    url      = request.args.get("url", "").strip()
    fmt      = request.args.get("format", "mp3").lower()   # mp3 | mp4 | m4a | wav
    quality  = request.args.get("quality", "192")           # 64 | 128 | 192 | 320

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    allowed_formats = ["mp3", "mp4", "m4a", "wav"]
    if fmt not in allowed_formats:
        return jsonify({"error": f"Format must be one of {allowed_formats}"}), 400

    allowed_qualities = ["64", "128", "192", "320"]
    if quality not in allowed_qualities:
        quality = "192"

    file_id = str(uuid.uuid4())
    out_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    # Build yt-dlp options based on format
    if fmt in ["mp3", "wav", "m4a"]:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_path,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": quality,
            }],
        }
    else:  # mp4 — best audio only (no video)
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": out_path,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": quality,
            }],
        }
        fmt = "m4a"  # mp4 container but audio only

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get("title", "audio"))

        # Find the output file
        final_path = None
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                final_path = os.path.join(DOWNLOAD_DIR, f)
                break

        if not final_path or not os.path.exists(final_path):
            return jsonify({"error": "Conversion failed, file not found"}), 500

        delete_file_later(final_path)  # clean up after 10 min

        mime_map = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
        }
        mime = mime_map.get(fmt, "audio/mpeg")

        return send_file(
            final_path,
            mimetype=mime,
            as_attachment=True,
            download_name=f"{title}.{fmt}"
        )

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── HEALTH CHECK ────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "YT Audio API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
