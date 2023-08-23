import spotipy
from spotipy import SpotifyClientCredentials
import pandas as pd
import numpy as np

cid = '2a8aceae04c540199bb94acaee3c7c5c'
secret = '33bf3db97bde4db685bc84b8bea02771'

client_credientials_manager = SpotifyClientCredentials(client_id = cid, client_secret = secret)

sp = spotipy.Spotify(client_credentials_manager = client_credientials_manager)

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

print("Hello!")

playlist_id_1 = input("Please enter the first playlist id: ")
print("Great! Preparing the first playlist now...")
df1 = call_playlist("spotify", playlist_id_1)
#df1.to_csv("playlist_1_data.csv", index = True)
print("The first playlist has been loaded successfully! " + str(len(df1.index)) + " songs were found!")

playlist_id_2 = input("Please now enter the second playlist id: ")
print("Great! Preparing the second playlist now...")
df2 = call_playlist("spotify", playlist_id_2)
#df2.to_csv("playlist_2_data.csv", index = True)
print("The second playlist has been loaded successfully! " + str(len(df2.index)) + " songs were found!")
           
def average_features(df, feature_cols):
    return df[feature_cols].mean().values

feature_cols = ["danceability", "energy", "mode", "speechiness", "instrumentalness", "liveness", "valence"]
avg_features_df1 = average_features(df1, feature_cols)
avg_features_df2 = average_features(df2, feature_cols)

def euclidean_distance_np(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)

distance = euclidean_distance_np(avg_features_df1, avg_features_df2)
print("Euclidean Distance between the playlists:", distance)

#def scaled_exponential_similarity(distance, alpha=2.5):
#    return np.exp(-alpha * distance)

#alpha_values = [1, 2, 3, 5, 10]
#for alpha in alpha_values:
#    similarity_score = scaled_exponential_similarity(distance, alpha)
#    print(f"Similarity Score (alpha={alpha}):", similarity_score)

alpha = 2.5

similarity_score = np.exp(-alpha * distance)
print("Similarity Score: ", similarity_score)

test