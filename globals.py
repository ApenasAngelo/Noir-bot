import sqlite3

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import os
from dotenv import load_dotenv

conn = sqlite3.connect('noir_database.sqlite')
cursor = conn.cursor()

guild_queue_list = {}


load_dotenv()
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('spotify.ClientID'),
    client_secret=os.getenv('spotify.ClientSecret')
    )
spotipy = spotipy.Spotify(auth_manager=auth_manager)