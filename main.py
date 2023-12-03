import os
import random
import yt_dlp
import time
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yt_dlp.postprocessor import FFmpegPostProcessor


download_path = os.environ.get('DOWNLOAD_PATH')
port = os.environ.get('PORT')
ffmpeg_location = os.environ.get('FFMPEG_LOCATION')


if download_path is None \
        or port is None\
        or ffmpeg_location is None:
    raise Exception('application environment not set properly')


FFmpegPostProcessor._ffmpeg_location.set(ffmpeg_location)


class YtVideoDownloadRequestBody(BaseModel):
    url: str


def generate_random_file_name():
    timestamp_ms = int(time.time() * 1000)
    random_number = random.random()
    return f"{timestamp_ms}{random_number}"


app = FastAPI()


@app.get("/")
def health():
    return {"success": "true", "message": f'downloader service running on port {port}'}


@app.post("/api/download")
def download_video(body: YtVideoDownloadRequestBody):
    file_extension = 'mp3'
    file_name = f'{generate_random_file_name(file_extension)}'
    urls = [body.url]
    ydl_opts = {
        'outtmpl': {
            'default': "/".join([download_path, file_name]),
        },
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

    if error_code == 0:
        file_path = os.path.join(download_path, file_name)
        return FileResponse(file_path, filename=file_name, media_type=f'audio/{file_extension}')
    else:
        raise HTTPException(500, detail="Download failed for internal server error")