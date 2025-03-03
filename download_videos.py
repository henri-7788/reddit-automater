import os
import requests
import configparser
import logging
from moviepy.editor import VideoFileClip
import shutil

import praw

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Lade Konfiguration
config = configparser.ConfigParser()
config.read("config.ini")

CLIENT_ID = config["reddit"]["client_id"]
CLIENT_SECRET = config["reddit"]["client_secret"]
USER_AGENT = config["reddit"]["user_agent"]
SUBREDDIT_NAME = config["reddit"]["subreddit"]
TIME_FILTER = config["settings"].get("time_filter", "day")

# Erstelle Ordner für Downloads falls nicht vorhanden
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Datei für bereits heruntergeladene IDs
DOWNLOADED_IDS_FILE = "downloaded_ids.txt"
if not os.path.exists(DOWNLOADED_IDS_FILE):
    with open(DOWNLOADED_IDS_FILE, "w") as f:
        pass

# Lese bereits verarbeitete IDs
def load_downloaded_ids():
    with open(DOWNLOADED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

downloaded_ids = load_downloaded_ids()

# Speichert eine neue ID in der Datei
def save_downloaded_id(post_id):
    with open(DOWNLOADED_IDS_FILE, "a") as f:
        f.write(post_id + "\n")

# Initialisiere Reddit API via PRAW
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        return True
    except Exception as e:
        logging.error(f"Fehler beim Herunterladen von {url}: {e}")
        return False

def convert_gif_to_mp4(gif_path, mp4_path):
    try:
        clip = VideoFileClip(gif_path)
        clip.write_videofile(mp4_path, codec="libx264", audio=False, logger=None)
        clip.close()
        os.remove(gif_path)  # Entferne das GIF nach der Konvertierung
        return True
    except Exception as e:
        logging.error(f"Fehler bei der Konvertierung {gif_path}: {e}")
        return False

def process_post(post):
    # Überspringe, falls bereits heruntergeladen
    if post.id in downloaded_ids:
        logging.info(f"Post {post.id} wurde bereits verarbeitet.")
        return

    video_url = None
    filename = None

    # Prüfe, ob es ein Reddit-Video ist
    if post.is_video and post.media and "reddit_video" in post.media:
        video_url = post.media["reddit_video"].get("fallback_url")
        filename = f"{post.id}.mp4"
    # Prüfe auf GIF oder gifv (gifv sind oft bereits als mp4 verfügbar)
    elif post.url.endswith(".gif") or post.url.endswith(".gifv"):
        # Falls gifv, ersetze die Endung mit mp4
        if post.url.endswith(".gifv"):
            video_url = post.url[:-5] + ".mp4"
            filename = f"{post.id}.mp4"
        else:
            # Bei .gif: lade zunächst das GIF herunter und konvertiere es
            video_url = post.url
            filename = f"{post.id}.gif"
    else:
        logging.info(f"Post {post.id} enthält kein unterstütztes Medium.")
        return

    # Download-Pfad
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    logging.info(f"Lade {post.id} von {video_url} herunter...")

    # Download durchführen
    if not download_file(video_url, file_path):
        logging.error(f"Download von {post.id} fehlgeschlagen.")
        return

    # Falls es ein GIF war, konvertiere es zu MP4
    if filename.endswith(".gif"):
        mp4_path = os.path.join(DOWNLOAD_DIR, f"{post.id}.mp4")
        if convert_gif_to_mp4(file_path, mp4_path):
            logging.info(f"Post {post.id} (GIF) wurde erfolgreich als MP4 gespeichert.")
        else:
            logging.error(f"Konvertierung von GIF zu MP4 für {post.id} fehlgeschlagen.")
            return
    else:
        logging.info(f"Post {post.id} wurde erfolgreich heruntergeladen.")

    # Speichere die Post-ID, um Doppel-Downloads zu vermeiden
    save_downloaded_id(post.id)

def main():
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    logging.info(f"Verarbeite Top-Posts aus r/{SUBREDDIT_NAME} (Timefilter: {TIME_FILTER})")

    # Hole Top-Posts basierend auf dem konfigurierten Zeitfilter
    for post in subreddit.top(time_filter=TIME_FILTER, limit=50):
        process_post(post)

if __name__ == "__main__":
    main()
