import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import spotipy.oauth2 as oauth2
import os
from flask import session


class SpotifyApi:

    def __init__(self, authentication):
        """
        Authentication service
        """
        self.api = spotipy.Spotify(auth_manager=authentication)

    def get_user(self):
        return self.api.me()

    def top_tracks(self):
        return self.api.current_user_top_tracks(limit=10)

    def top_artists(self):
        return self.api.current_user_top_artists(limit=10)