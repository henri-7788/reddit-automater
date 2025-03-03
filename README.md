# Reddit Video Downloader

Dieses Repository lädt die Top-Videos (und GIFs, die als Video konvertiert werden) aus einem konfigurierbaren Subreddit herunter und speichert sie im Ordner `downloads/`. Dabei wird eine Liste (`downloaded_ids.txt`) gepflegt, um doppelte Downloads zu vermeiden.

## Funktionen

- Verbindung zur Reddit API über [PRAW](https://praw.readthedocs.io/)
- Download der Top-Posts basierend auf einem Zeitfilter (z.B. day, week, etc.)
- Es werden ausschließlich Videos und GIFs heruntergeladen. GIFs werden mithilfe von MoviePy in ein MP4-Video konvertiert.
- Vermeidung von doppelten Downloads durch Speicherung der bereits heruntergeladenen Post-IDs

## Voraussetzungen

- Python 3.6 oder höher
- ffmpeg (muss installiert und im Systempfad verfügbar sein, damit MoviePy GIFs konvertieren kann)

## Installation

1. Repository klonen oder Dateien herunterladen.
2. In das Verzeichnis wechseln:
   ```bash
   cd reddit_video_downloader
