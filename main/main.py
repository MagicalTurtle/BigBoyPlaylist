from typing import Final, final
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, USERNAME

import requests
from bs4 import BeautifulSoup
import selenium as se
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math


def getToken():
    scope = 'user-read-recently-played user-library-read user-top-read playlist-modify-public'
    return spotipy.util.prompt_for_user_token(username=USERNAME, scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)


def getData():
    topSongs = []
    # current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
    topS1 = sp.current_user_top_tracks(
        limit=50, offset=0, time_range='short_term')
    for t1 in topS1['items']:
        topSongs.append(t1['id'])  # can switch to t['id']

    topS2 = sp.current_user_top_tracks(
        limit=50, offset=50, time_range='short_term')
    for t2 in topS1['items']:
        topSongs.append(t2['id'])  # can switch to t['id']
    # print(len(topSongs))

    recentSongs = []
    # current_user_recently_played(limit=50, after=None, before=None)
    recentS = sp.current_user_recently_played(
        limit=50, after=None, before=None)
    for r in recentS['items']:
        recentSongs.append(r['track']['id'])
    # print(recentSongs)

    librarySongs = []
    # current_user_saved_tracks(limit=20, offset=0, market=None)
    libraryS1 = sp.current_user_saved_tracks(limit=50, offset=0, market=None)
    for l1 in libraryS1['items']:
        librarySongs.append(l1['track']['id'])

    libraryS2 = sp.current_user_saved_tracks(limit=50, offset=50, market=None)
    for l2 in libraryS2['items']:
        librarySongs.append(l2['track']['id'])
    # print(librarySongs)

    # combine 3 lists to one
    approvedSongs = []
    for i in topSongs:
        if i not in approvedSongs:
            approvedSongs.append(i)

    for i in recentSongs:
        if i not in approvedSongs:
            approvedSongs.append(i)

    for i in librarySongs:
        if i not in approvedSongs:
            approvedSongs.append(i)

    return(approvedSongs)


def getRec(list):
    recList = []
    options = se.webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = se.webdriver.Chrome(
        ".\driver\chromedriver.exe")

    # print("length of list: " + str(len(list)))
    for s in list:
        # print("this is the song: " + s)
        URL = "https://www.chosic.com/playlist-generator/?track=" + s
        driver.get(URL)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-more")))
            print("SWAG MONEY")
        except:
            print("NOT SWAG MONEY")
            pass

        songs = driver.find_elements(By.CLASS_NAME, "track-list-item")
        songCodes = []
        for i in songs:
            code = i.get_attribute("data-id")
            songCodes.append(code)

        for c in songCodes:
            recList.append(c)
    return(recList)

    driver.close()


token = getToken()
sp = spotipy.Spotify(auth=token)
songs = getData()

print("len of songs: " + str(len(songs)))
rec = getRec(songs)

newSongs = []
for i in rec:
    newSongs.append(i)
print("New Songs Length: " + str(len(newSongs)))

finalSongs = []
for i in songs:
    if i not in finalSongs:
        finalSongs.append(i)
for i in newSongs:
    if i not in finalSongs:
        finalSongs.append(i)

print("Final Playlist Length: "+str(len(finalSongs)))

token = getToken()
sp = spotipy.Spotify(auth=token)

sp.user_playlist_create(user=USERNAME, public=True,
                        description="This playlist was generated using magic!", collaborative=False, name="Generated Playlist")

prePlaylist = sp.user_playlists(user=USERNAME)
playlist = prePlaylist['items'][0]['id']

songsAdded = len(finalSongs)
for i in list(range(math.ceil(len(finalSongs)/100))):
    batch = finalSongs[0:100]
    sp.user_playlist_add_tracks(
        user=USERNAME, playlist_id=playlist, tracks=batch)
    del finalSongs[:100]

print(str(int(songsAdded)-int(len(finalSongs))) + " Songs Added!")
