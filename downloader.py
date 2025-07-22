import os
import threading
import yt_dlp
import requests
from urllib.parse import urlparse
from PyQt5.QtCore import QObject, pyqtSignal
from core.utils import ensure_downloads_folder

MAX_PARALLEL_DOWNLOADS = 10
active_downloads = 0
lock = threading.Lock()

class DownloadSignals(QObject):
    progress = pyqtSignal(int, int)
    title = pyqtSignal(int, str)
    done = pyqtSignal(int)

def sanitize_filename(title):
    return "".join(c for c in title if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()

def download_handler(url, format, callback=None, progress_callback=None, row_id=None, title_callback=None, output_path=None):
    signals = DownloadSignals()
    if progress_callback:
        signals.progress.connect(progress_callback)
    if title_callback:
        signals.title.connect(title_callback)
    if callback:
        signals.done.connect(callback)

    def thread_job():
        global active_downloads
        with lock:
            if active_downloads >= MAX_PARALLEL_DOWNLOADS:
                print("⚠ Max concurrent reached.")
                return
            active_downloads += 1

        try:
            folder = output_path or ensure_downloads_folder()
            if format in ['mp3','m4a','webm_audio','mp4_1080p','mp4_720p','mp4_480p','webm_720p']:
                _download_video(url, format, row_id, folder, signals)
            elif format == 'image':
                _download_image(url, row_id, folder, signals)
            else:
                print("✖ Unsupported format:", format)
        except Exception as e:
            print("✖ Error:", e)
        finally:
            with lock:
                active_downloads -= 1

    threading.Thread(target=thread_job, daemon=True).start()

def _download_video(url, format, row_id, folder, signals):
    holder = {}

    def hook(d):
        if d.get('status') == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total:
                pct = int(downloaded * 100 / total)
                signals.progress.emit(row_id, pct)

        if d.get('status') == 'finished':
            signals.done.emit(row_id)

    ydl_opts = {
    'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
    'noplaylist': True,
    'progress_hooks': [hook],
    'merge_output_format': 'mp4',
    'quiet': False,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    }


    if format == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]
        })
    elif format == 'm4a':
        ydl_opts['format']='bestaudio[ext=m4a]/bestaudio/best'
    elif format == 'webm_audio':
        ydl_opts['format']='bestaudio[ext=webm]/bestaudio/best'
    elif format.startswith('mp4') or format.startswith('webm'):
        pass  # handled above

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ✅ Step 1: Extract info before download
            info = ydl.extract_info(url, download=False)

            # ✅ Step 2: Get title and extension
            t = sanitize_filename(info.get('title', 'untitled'))
            e = info.get('ext') or 'mp4'
            fname = f"{t}.{e}"

            # ✅ Step 3: Emit title early
            signals.title.emit(row_id, fname)

            # ✅ Step 4: Start actual download
            ydl.download([url])

        print("✅ Download complete.")
    except Exception as e:
        print("❌ yt-dlp fail:", e)
        signals.done.emit(row_id)


def _download_image(url, row_id, folder, signals):
    fname = os.path.basename(urlparse(url).path) or "image.jpg"
    path = os.path.join(folder, fname)
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        c = 0
        with open(path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk); c += len(chunk)
                if total:
                    signals.progress.emit(row_id, int(c*100/total))
        signals.title.emit(row_id, fname)
        signals.done.emit(row_id)
        print("✅ Image done")
    except Exception as e:
        print("✖ Image error:", e)
        signals.done.emit(row_id)