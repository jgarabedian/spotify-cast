from flask import (Flask, flash, Markup, redirect, render_template, request,
                   Response, session, url_for)
from flask_session import Session
import os
import uuid
from api import SpotifyApi
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import spotipy.oauth2 as oauth2

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.debug = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    auth = spotipy.oauth2.SpotifyOAuth(
        scope="user-top-read user-library-read",
        cache_path=session_cache_path(),
        show_dialog=True
    )
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    if request.args.get('code'):
        auth.get_access_token(request.args.get('code'))
        return redirect('/')

    if not auth.get_cached_token():
        auth_url = auth.get_authorize_url()
        return render_template("login.html", auth_url=auth_url)

    # api = spotipy.Spotify(auth_manager=auth)
    api = SpotifyApi(authentication=auth)
    session['logged_in'] = True
    return render_template('user.html', user=api.get_user())


@app.route('/logout')
def logout():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
        session['logged_in'] = False
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/favorites')
def favorites():
    auth = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth.get_cached_token():
        redirect('/')
    api = SpotifyApi(auth)

    artists = api.top_artists()
    tracks = api.top_tracks()
    return render_template("favorites.html", artists=artists, tracks=tracks)
    # return render_template("tracks.html", tracks=tracks)


def main():
    app.run()


if __name__ == "__main__":
    main()