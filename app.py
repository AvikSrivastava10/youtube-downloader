from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():

    url = request.form.get("url")
    file_type = request.form.get("type")

    # URL Validation
    if not url:
        return "No URL provided"

    if "youtube.com" not in url and "youtu.be" not in url:
        return "Invalid YouTube URL"

    unique_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_id)

    try:

        # MP4 Download
        if file_type == "mp4":

            ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': f'{output_path}.%(ext)s',
    'restrictfilenames': True,
    'merge_output_format': 'mp4',
    'quiet': True,
    'cookiefile': 'cookies.txt',

    'http_headers': {
        'User-Agent': 'Mozilla/5.0'
    },

    'extractor_args': {
        'youtube': {
            'player_client': ['android']
        }
    },

    'sleep_interval_requests': 1,
}

        # MP3 Download
        else:

            ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{output_path}.%(ext)s',
    'restrictfilenames': True,
    'quiet': True,
    'cookiefile': 'cookies.txt',

    'http_headers': {
        'User-Agent': 'Mozilla/5.0'
    },

    'extractor_args': {
        'youtube': {
            'player_client': ['android']
        }
    },

    'sleep_interval_requests': 1,

    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

        print(f"Downloading: {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = os.listdir(DOWNLOAD_FOLDER)

        for file in files:

            if unique_id in file:

                file_path = os.path.join(DOWNLOAD_FOLDER, file)

                print(f"Sending File: {file_path}")

                return send_file(
                    file_path,
                    as_attachment=True
                )

        return "Download failed"

    except Exception as e:
        print("Error:", e)
        return f"Error occurred: {str(e)}"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )