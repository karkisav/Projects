from dotenv import load_dotenv
import spotipy
from flask import session
from spotipy.cache_handler import FlaskSessionCacheHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os, time

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
scope='playlist-modify-private'
cache_handler = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    cache_handler=cache_handler,
    scope=scope,
    show_dialog=True
)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_recommendations(seed_genres=None, seed_artists=None, seed_tracks=None, limit=20, **kwargs):
    try:
        if not (seed_genres or seed_artists or seed_tracks):
            raise ValueError("At least one of seed_genres, seed_artists, or seed_tracks must be provided.")
        
        rec = sp.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, limit=limit, **kwargs)
        return rec['tracks']
    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None
    
def get_genre():
    return sp.recommendation_genre_seeds()

def get_spotify_client():
    if 'token_info' not in session:
        return None

    token_info = session['token_info']

    # Check if token has expired
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return spotipy.Spotify(auth=token_info['access_token'])

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return token_info