import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from youtubesearchpython import VideosSearch

driver = webdriver.Edge()

login_link = "https://accounts.spotify.com/en/login"
song_element = "h4HgbO_Uu1JYg5UGANeQ.wTUruPetkKdWAR1dd6w4"
name_element = ("Text__TextElement-sc-if376j-0.ksSRyh.encore-text-body-medium.t_yrXoUO3qGsJS4Y6iXX.standalone-ellipsis"
                "-one-line")
author_element = "Type__TypeElement-sc-goli3j-0.bGROfl"

# Edit these variables to your liking
# This is the URL for the playlist you want to download, the default one is for liked songs, edit this to your liking
playlist_link = "https://open.spotify.com/playlist/4nAy3PPMFuOcX5OjNqTBhF?si=6f3811d096e144d7"
# Specify the approixmate number of songs in your playlist
num_songs = 44
# Set this to True if you want to get more details on song downloading
debug = False
# Set this to True if you want to use a private playlist or a liked song playlist
private = False
# Set this to the path to your ffmpeg.exe file
ffmpeg_path = "C:\\ProgramData\\chocolatey\\lib\\ffmpeg\\tools\\ffmpeg\\bin\\"


def main():
    if private:
        login()
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

    time.sleep(2)


def get_songs():
    driver.get(playlist_link)
    driver.maximize_window()
    time.sleep(5)
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
