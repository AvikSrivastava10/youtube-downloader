from flask import Flask, render_template, request, send_file, after_this_request
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

    if not url:
        return "No URL provided"

    if "youtube.com" not in url and "youtu.be" not in url:
        return "Invalid YouTube URL"

    unique_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_id)

    try:

        # MP4
        if file_type == "mp4":

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{output_path}.%(ext)s',
                'restrictfilenames': True,
                'merge_output_format': 'mp4',
                'quiet': True
            }

        # MP3
        else:

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}.%(ext)s',
                'restrictfilenames': True,
                'quiet': True,

                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_file = None

        for file in os.listdir(DOWNLOAD_FOLDER):

            if unique_id in file:
                downloaded_file = os.path.join(DOWNLOAD_FOLDER, file)
                break

        if not downloaded_file:
            return "Download failed"

        # Auto delete after response
        @after_this_request
        def remove_file(response):

            try:
                os.remove(downloaded_file)
                print(f"Deleted: {downloaded_file}")

            except Exception as e:
                print("Delete Error:", e)

            return response

        return send_file(
            downloaded_file,
            as_attachment=True
        )

    except Exception as e:
        print("Error:", e)
        return f"Error occurred: {str(e)}"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )