import os
import shutil
import subprocess
import pyautogui
import time
import eyed3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from youtubesearchpython import VideosSearch
from unidecode import unidecode

# Edit these variables to your liking
# This is the URL for the playlist you want to download, edit this to your liking
playlist_link = "https://open.spotify.com/collection/tracks"
# Specify the approixmate number of songs in your playlist
num_songs = 814
# Set this to True if you want to get more details on song downloading like download speed, size and progress
debug = False
# Set this to True if you want to use a private playlist or a liked song playlist
private = True
# Set this to the path to your ffmpeg.exe file
ffmpeg_path = "/Users/aymanisam/Downloads/ffmpeg"
# Set this to true if trying to download albums from artists
album = False
# Set this option to the browser you're using, options are "Chrome", "Firefox" and "Edge". If you decide to use
# firefox, you have to download the webdriver and include its path. For Chrome, you have to install the chrome test
# browser. Edge has a built-in webdriver so that's not needed
browser = "Edge"
# OS, needed for the correct command for downloading albums
OS = "macOS"

if browser == "Chrome":
    driver = webdriver.Chrome()

elif browser == "Edge":
    edge_options = Options()
    edge_options.add_argument("--guest")
    driver = webdriver.Edge(options=edge_options)

elif browser == "Firefox":
    driver = webdriver.Firefox()

login_link = "https://accounts.spotify.com/en/login"
song_element = "IjYxRc5luMiDPhKhZVUH.UpiE7J6vPrJIa59qxts4"
name_element = "Text__TextElement-sc-if376j-0.ksSRyh.encore-text-body-medium.btE2c3IKaOXZ4VNAb8WQ.standalone-ellipsis-one-line"
author_element = "Text__TextElement-sc-if376j-0.gYdBJW.encore-text-body-small"
img_element = "mMx2LUixlnN_Fu45JpFB.IqDKYprOtD_EJR1WClPv.Yn2Ei5QZn19gria6LjZj"
album_element = "_TH6YAXEzJtzSxhkGSqu"
album_img = "mMx2LUixlnN_Fu45JpFB.CmkY1Ag0tJDfnFXbGgju._EShSNaBK1wUIaZQFJJQ.Yn2Ei5QZn19gria6LjZj"


def main():
    if private:
        login()
    time.sleep(2)
    songs = get_songs()
    get_links(songs)
    remove_images()
    driver.quit()


def login():
    driver.get(login_link)
    driver.maximize_window()

    email_field = driver.find_element(By.ID, "login-username")
    password_field = driver.find_element(By.ID, "login-password")

    email = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')

    email_field.send_keys(email)
    password_field.send_keys(password)

    login_button = driver.find_element(By.ID, "login-button")
    login_button.click()


def download_image(img_url, filename):
    driver.execute_script(f'window.open("{img_url}","_blank");')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(2)
    pyautogui.click(x=400, y=400)
    time.sleep(2)
    if OS == "macOS":
        pyautogui.hotkey('command', 's')
    else:
        pyautogui.hotkey('ctrl', 's')
    time.sleep(5)
    pyautogui.write(filename)
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])

    driver.close()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])


def set_image(mp3_file_path, image_file_path):
    audio_file = eyed3.load(mp3_file_path)
    if audio_file.tag is None:
        audio_file.initTag()
    audio_file.tag.images.remove('')
    with open(image_file_path, 'rb') as img_file:
        audio_file.tag.images.set(3, img_file.read(), 'image/jpeg')
    audio_file.tag.save()


def set_metadata(mp3_file_path, title, artist, album):
    audio_file = eyed3.load(mp3_file_path)
    if audio_file.tag is None:
        audio_file.initTag()

    audio_file.tag.title = title
    audio_file.tag.artist = artist
    audio_file.tag.album = album

    audio_file.tag.save()


def safe_name(name):
    name = unidecode(name)
    for char in ['(', ')', '&', '/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(char, '')
    while '  ' in name:
        name = name.replace('  ', ' ')
    return name


def get_songs():
    # To get the web link of the playlist to not have open in app popups
    playlist_link_index = playlist_link.index('?') if '?' in playlist_link else None
    if playlist_link_index:
        playlist_web_link = playlist_link[:playlist_link_index]
    else:
        playlist_web_link = playlist_link
    driver.get(playlist_web_link)
    driver.maximize_window()
    time.sleep(10)

    image_dir = "./images"
    os.makedirs(image_dir, exist_ok=True)

    if album:
        album_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        album_img_url = driver.find_element(By.CSS_SELECTOR, "img." + album_img).get_attribute("src")
        album_img_filename = os.path.join(f"{safe_name(album_name)}.jpeg")
        download_image(album_img_url, album_img_filename)
        src = os.path.join('/Users/aymanisam/Downloads', album_img_filename)
        dst = os.path.join(image_dir, album_img_filename)
        shutil.move(src, dst)

    try:
        cookie_popup = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        cookie_popup.click()
        body = driver.find_element(By.TAG_NAME, "body")
        time.sleep(2)
        body.click()
    except (NoSuchElementException, TimeoutException):
        pass
    scroll_range = num_songs // 10
    actions = ActionChains(driver)
    song_list = []
    song_set = set()
    for i in range(scroll_range):
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(0.5)
        if (i + 2) % 3 == 0:
            song_divs = driver.find_elements(By.CSS_SELECTOR, "div." + song_element)
            for song_div in song_divs:
                song = song_div.find_element(By.CSS_SELECTOR, "div." + name_element).text.strip()
                try:
                    if album:
                        authors = song_div.find_element(By.CSS_SELECTOR, "span." + author_element).text.strip()
                    else:
                        authors = song_div.find_element(By.CSS_SELECTOR, "div." + author_element).text.strip()
                        img_src = song_div.find_element(By.CSS_SELECTOR, "img." + img_element).get_attribute("src")
                        img_url = img_src.replace("4851", "1e02")
                        album_name = song_div.find_element(By.CSS_SELECTOR, "div." + album_element).text.strip()
                except NoSuchElementException:
                    continue

                filename = album_img_filename if album else os.path.join(f"{safe_name(song)}_{safe_name(authors)}.jpeg")
                dst = os.path.join(image_dir, filename)
                mp3_file_path = os.path.join('./downloads', f"{safe_name(authors)} - {safe_name(song)}.mp3")

                if not os.path.exists(dst) and not os.path.exists(mp3_file_path):
                    if not album:
                        max_attempts = 3
                        for attempt in range(max_attempts):
                            try:
                                if not os.path.exists(dst):
                                    download_image(img_url, filename)
                                    src = os.path.join('/Users/aymanisam/Downloads', filename)
                                    shutil.move(src, dst)
                                break
                            except FileNotFoundError:
                                print(f"Attempt {attempt + 1} to move file {filename} failed. Retrying download.")
                                if attempt + 1 == max_attempts:
                                    print(f"Skipping file {filename} after {max_attempts} failed attempts.")

                if (song, authors) not in song_set:
                    song_set.add((song, authors))
                    song_list.append((song, authors, filename, album_name))
    return song_list


def get_links(songs):
    print(f"Number of songs: {len(songs)}")
    for song, authors, filename, album_name in songs:
        safe_song = safe_name(song)
        safe_authors = safe_name(authors)
        output_dir = "./downloads"
        mp3_file_path = os.path.join(output_dir, safe_authors + " - " + safe_song + ".mp3")

        if os.path.exists(mp3_file_path):
            continue

        search = VideosSearch(authors + song + 'official lyric video', limit=1)
        results = search.result()['result']
        if results:
            link = search.result()['result'][0]['link']
            download(link, song, authors, filename, album_name)
        else:
            print(f"\033[91mNo videos found for {song} by {authors}\033[0m")
            search = VideosSearch(authors + song, limit=1)
            results = search.result()['result']
            if results:
                link = search.result()['result'][0]['link']
                download(link, song, authors, filename, album_name)
            else:
                print(f"\033[91mStill no videos found for {song} by {authors}, skipping this song.\033[0m")
                with open("missing_songs.txt", "a") as file:
                    file.write(f"{song} by {authors}\n")


def download(link, song, authors, image_file_path, album_name):
    safe_song = safe_name(song)
    safe_authors = safe_name(authors)
    output_dir = "./downloads"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    mp3_file_path = os.path.join(output_dir, safe_authors + " - " + safe_song + ".mp3")
    command = ["yt-dlp", "-x", "--audio-format", "mp3", "--remux-video", "mp3", "--ffmpeg-location",
               ffmpeg_path, "-o", mp3_file_path, link]
    try:
        print(f"Downloading \033[95m{song}\033[0m by \033[96m{authors}\033[0m from link {link}")
        if debug:
            subprocess.run(command, check=True)
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\033[92mDownload Complete for \033[95m{song}\033[0m by \033[96m{authors}\033[0m\033[0m")
        # Set the image to the mp3 file
        set_image(mp3_file_path, os.path.join('images', image_file_path))
        set_metadata(mp3_file_path, song, authors, album_name)
    except subprocess.CalledProcessError:
        print(
            f"\033[91mAn Error Has Occured while downloading \033[95m{song}\033[0m by \033[96m{authors}\033[0m\033[0m")


def remove_images():
    images_folder_path = './images'
    if os.path.exists(images_folder_path):
        shutil.rmtree(images_folder_path)
    else:
        print("Images could not be removed")


main()
