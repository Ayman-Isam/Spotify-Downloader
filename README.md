# Spotify Downloader

This project is a Python script that downloads songs from a Spotify playlist as MP3 files. It uses Selenium to scrape song information from Spotify and `yt-dlp` to download the songs from YouTube.

## Features

- Downloads songs from a Spotify playlist as MP3 files
- Supports both public and private playlists
- Provides debug information for song downloading
- Supports Chrome, Firefox, and Edge browsers

## Requirements

- Modern version of Microsoft Edge, Google Chrome, or Mozilla Firefox
- Python 3
- Selenium
- yt-dlp
- ffmpeg

## Usage

1. Clone this repository.
2. Install the required Python packages: `pip install -r requirements.txt`
3. Install ffmpeg and add the path to it to the `ffmpeg_path` variable in `scraper.py`
4. Set the `playlist_link` variable in `scraper.py` to the URL of the Spotify playlist you want to download and the `num_songs` variable to the approximate number of songs in the playlist.
5. If the playlist is private, set the `private` variable to `True` and set your Spotify email and password as environment variables `EMAIL` and `PASSWORD`.
6. Set the `browser` variable in `scraper.py` to the browser you're using. Options are "Chrome", "Firefox", and "Edge". If you decide to use Firefox, you have to download the webdriver and include its path. For Chrome, you have to install the chrome test browser. Edge has a built-in webdriver so that's not needed.
7. Run `scraper.py`: `python scraper.py`

The songs will be downloaded as MP3 files in the `downloads` directory.

## Note

This script searches for the official lyric video of each song on YouTube, so it might not find all songs, especially if they are very new or obscure. If a song is not found, it will print a message and continue with the next song.