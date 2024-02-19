import os
import time
import subprocess
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from youtubesearchpython import VideosSearch

# Edit these variables to your liking
# This is the URL for the playlist you want to download, edit this to your liking
playlist_link = "https://open.spotify.com/playlist/23C00A7OMiPgeSVZCG0nWE"
# Specify the approixmate number of songs in your playlist
num_songs = 700
# Set this to True if you want to get more details on song downloading like download speed, size and progress
debug = False
# Set this to True if you want to use a private playlist or a liked song playlist
private = False
# Set this to the path to your ffmpeg.exe file
ffmpeg_path = "C:\\ProgramData\\chocolatey\\lib\\ffmpeg\\tools\\ffmpeg\\bin\\"
# Set this to true if trying to download albums from artists
album = False
# Set this option to the browser you're using, options are "Chrome", "Firefox" and "Edge". If you decide to use
# firefox, you have to download the webdriver and include its path. For Chrome, you have to install the chrome test
# browser. Edge has a built-in webdriver so that's not needed
browser = "Edge"

if browser == "Chrome":
    driver = webdriver.Chrome()

elif browser == "Edge":
    edge_options = Options()
    edge_options.add_argument("--guest")
    driver = webdriver.Edge(options=edge_options)

elif browser == "Firefox":
    driver = webdriver.Firefox()

login_link = "https://accounts.spotify.com/en/login"
song_element = "iCQtmPqY0QvkumAOuCjr"
name_element = ("Text__TextElement-sc-if376j-0.ksSRyh.encore-text-body-medium.t_yrXoUO3qGsJS4Y6iXX.standalone-ellipsis-one-line")
author_element = "Text__TextElement-sc-if376j-0.gYdBJW.encore-text-body-small"


def main():
    if private:
        login()
    time.sleep(2)
    songs = get_songs()
    get_links(songs)
    driver.quit()


def login():
    driver.get(login_link)
    driver.maximize_window()

    email_field = driver.find_element(By.ID, "login-username")
    password_field = driver.find_element(By.ID, "login-password")

    email_field.send_keys(os.environ.get('EMAIL'))
    password_field.send_keys(os.environ.get('PASSWORD'))

    login_button = driver.find_element(By.ID, "login-button")
    login_button.click()


def get_songs():
    # To get the web link of the playlist to not have open in app popups
    playlist_link_index = playlist_link.index('?') if '?' in playlist_link else None
    if playlist_link_index:
        playlist_web_link = playlist_link[:playlist_link_index]
    else:
        playlist_web_link = playlist_link
    driver.get(playlist_web_link)
    driver.maximize_window()
    time.sleep(2)
    try:
        time.sleep(10)
        cookie_popup = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        cookie_popup.click()
        body = driver.find_element(By.TAG_NAME, "body")
        time.sleep(2)
        body.click()
    except (NoSuchElementException, TimeoutException):
        pass
    scroll_range = num_songs // 5
    actions = ActionChains(driver)
    song_list = []
    for i in range(scroll_range):
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(0.5)
        if (i + 2) % 3 == 0:
            song_divs = driver.find_elements(By.CSS_SELECTOR, "div." + song_element)
            for song_div in song_divs:
                song = song_div.find_element(By.CSS_SELECTOR, "div." + name_element).text.strip()
                if album:
                    authors_span = song_div.find_element(By.CSS_SELECTOR, "span." + author_element)
                    authors = authors_span.text.strip()
                else:
                    authors = song_div.find_element(By.CSS_SELECTOR, "div." + author_element).text.strip()
                if (song, authors) not in song_list:
                    song_list.append((song, authors))
    return song_list


def safe_name(name):
    for char in ['(', ')', '&', '/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(char, '')
    return name


def get_links(songs):
    for song, authors in songs:
        search = VideosSearch(authors + song + 'official lyric video', limit=1)
        results = search.result()['result']
        if results:
            link = search.result()['result'][0]['link']
            download(link, song, authors)
        else:
            print(f"No videos found for {song} by {authors}")
        driver.quit()


def download(link, song, authors):
    safe_song = safe_name(song)
    safe_authors = safe_name(authors)
    output_dir = "./downloads"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    command = ["yt-dlp", "-x", "--audio-format", "mp3", "--remux-video", "mp3", "--ffmpeg-location",
               ffmpeg_path, "-o",
               os.path.join(output_dir, safe_authors + " - " + safe_song + ".%(ext)s"), link]
    try:
        print(f"Downloading \033[95m{song}\033[0m by \033[96m{authors}\033[0m from link {link}")
        if debug:
            subprocess.run(command, check=True)
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\033[92mDownload Complete for \033[95m{song}\033[0m by \033[96m{authors}\033[0m\033[0m")
    except subprocess.CalledProcessError:
        print(
            f"\033[91mAn Error Has Occured while downloading \033[95m{song}\033[0m by \033[96m{authors}\033[0m\033[0m")


main()
