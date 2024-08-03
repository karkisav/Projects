from flask import request, jsonify, render_template, session, url_for, redirect
from app import app, spotify_recommendation_parameters, process_model_output
from app.spotify_client import get_recommendations, get_spotify_client, get_token
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from spotipy import Spotify
import os, spotipy

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

sp1 = Spotify(auth_manager=sp_oauth)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_spotify_playlist', methods=['POST'])
def create_spotify_playlist():
    token_info = get_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({'success': False, 'authUrl': auth_url})
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    track_uris = request.json.get('trackUris')
    mood = request.json.get('mood', 'My Mood')
    
    try:
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user_id, f"{mood} Playlist", public=False)
        sp.playlist_add_items(playlist['id'], track_uris)
        return jsonify({'success': True, 'playlistId': playlist['id']})
    except spotipy.SpotifyException as e:
        app.logger.error(f"Spotify API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Spotify API error'}), 500
    except Exception as e:
        app.logger.error(f"Error creating playlist: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    user_input = request.json.get('mood', '').strip()
    app.logger.info(f"Received mood: {user_input}")

    try:
        # Classify emotions
        emotions = spotify_recommendation_parameters(user_input)
        app.logger.info(f"Classified emotions: {emotions}")

        # Process emotions
        sorted_emotions = sorted(zip(emotions['labels'], emotions['scores']), key=lambda x: x[1], reverse=True)
        app.logger.info(f"Processed emotions: {sorted_emotions}")

        # Map emotions to Spotify features
        try:
            target_features = ['valence', 'energy', 'danceability', 'acousticness', 'instrumentalness', 'speechiness', 'liveness']
            spotify_features = process_model_output(emotions, target_features=target_features)
        except Exception as e:
            app.logger.error(f"Error in process_model_output: {str(e)}")
            return jsonify({'error': 'Error mapping emotions to features'}), 500

        app.logger.info(f"Spotify features: {spotify_features}")

        # Generate playlist recommendations
        try:
            playlist = get_recommendations(**spotify_features, seed_genres=['pop', 'rap', 'hip-hop', 'chill'], limit=21)
            track_uris = [track['uri'] for track in playlist]
            return jsonify({'playlist': playlist, 'trackUris': track_uris})
        except Exception as e:
            app.logger.error(f"Error in get_recommendations: {str(e)}")
            return jsonify({'error': 'Error getting recommendations'}), 500
        
    except Exception as e:
        app.logger.error(f"Error generating playlist: {str(e)}")
        return jsonify({'error': 'An error occurred while generating the playlist'}), 500
    