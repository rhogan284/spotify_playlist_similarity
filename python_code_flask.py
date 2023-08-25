from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np

app = Flask(__name__)

cid = '2a8aceae04c540199bb94acaee3c7c5c'
secret = '33bf3db97bde4db685bc84b8bea02771'
redirect_uri = 'http://localhost:3000'
scope = "playlist-read-private playlist-read-collaborative user-library-read user-top-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri, scope=scope, cache_path='cache.txt'))

def call_playlist(creator, playlist_id):

    playlist_features_list = ["artist", "album", "track_name", "track_id", "danceability", "energy", "key", "loudness", "mode", "speechiness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]
    
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    playlist = sp.user_playlist_tracks(creator, playlist_id)["items"]

    for track in playlist:
            try:
                track_data = track.get("track", {})
                album_data = track_data.get("album", {})
                artists_data = album_data.get("artists", [{}])

                playlist_features = {
                    "artist": artists_data[0].get("name", ""),
                    "album": album_data.get("name", ""),
                    "track_name": track_data.get("name", ""),
                    "track_id": track_data.get("id", "")
                }

                audio_features = sp.audio_features(playlist_features["track_id"])[0]
                if not audio_features:
                    print(f"No audio features for track: {playlist_features['track_name']}")
                    continue

                for feature in playlist_features_list[4:]:
                    playlist_features[feature] = audio_features.get(feature, None)

                track_df = pd.DataFrame(playlist_features, index=[0])
                playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

            except Exception as e:
                print(f"Error processing track: {e}")
                continue

    return playlist_df

           
def average_features(df, feature_cols):
    return df[feature_cols].mean().values

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)

def get_distance(playlist_id_1, playlist_id_2):
 
    feature_cols = ["danceability", "energy", "mode", "speechiness", "instrumentalness", "liveness", "valence"]

    df1 = call_playlist("spotify", playlist_id_1)
    df2 = call_playlist("spotify", playlist_id_2)

    avg_features_df1 = average_features(df1, feature_cols)
    avg_features_df2 = average_features(df2, feature_cols)

    return euclidean_distance(avg_features_df1, avg_features_df2)


@app.route("/", methods=["GET", "POST"])
def index():
    similarity_score = None

    if request.method == "POST":
        playlist_id_1 = request.form['playlist1']
        playlist_id_2 = request.form['playlist2']

        distance = get_distance(playlist_id_1, playlist_id_2)

        alpha = 2.5
        similarity_score = np.exp(-alpha * distance)
    return render_template('index.html', similarity=similarity_score)

if __name__ == '__main__':
    app.run(debug=True)