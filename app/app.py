from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
import google.generativeai as genai
import os
from spotipy.oauth2 import SpotifyOAuth
import time
# import text2emotion as te
# import config
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import requests

app = Flask(__name__)

genai.configure(api_key='AIzaSyAWAzGxBU6TezSlqLUvvnY80kSNaH-zi2E')
app.secret_key = "test"

CLIENT_ID = "f55bea887a4443b4b81dac5b70630ea2"
CLIENT_SECRET = "6c057c30b75744cf95a6383406f47a9d"

personalities = ['ISTJ',
        'ESTJ',
        'ISFJ',
        'ESFJ',
        'ISTP',
        'ESTP',
        'ISFP',
        'ESFP',
        'INTJ',
        'ENTJ',
        'INTP',
        'ENTP',
        'INFJ',
        'ENFJ',
        'INFP',
        'ENFP',
]


@app.route("/")
@app.route("/home", methods = ['GET', 'POST'])
def home():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        #return render_template("index.html", playlist=url_for_the_playlist) we could pass the url for the playlist in spotidy or maybe able to use widget
        #for now just gonna pass back the text
        if(request.form['text'] != ""):
            print(request)
            if (session.get('token_info')):
                test = str(get_personality())
                # test, _ = generate_playlist(request.form['text'])
                return render_template("index.html", text=test)
            else:
                #get user's token
                auth = create_spotify_oauth()
                auth_url = auth.get_authorize_url()
                return redirect(auth_url)
        else:
            return render_template("index.html")
        


@app.route("/callback")
def pass_token():
    app.logger.error("pass_token passed")
    code = request.args.get('code')
    auth = create_spotify_oauth()
    token = auth.get_access_token(code)
    session['token_info'] = token
    return home()


def generate_playlist(prompt: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    print(response.text)
    return response.text

#returns token_info
def get_token_info():
    token_info = session.get('token_info', None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if(is_expired):
        auth = create_spotify_oauth()
        token_info = auth.refresh_access_token(token_info['refresh_token'])
    return token_info


def get_top_track_analyse(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    tracks = sp.current_user_top_tracks(limit=1, offset=0, time_range='medium_term')
    data = {
        "acousticness": [],
        "danceability": [],
        "energy": [],
        "instrumentalness": [],
        "liveness": [],
        "loudness": [],
        "speechiness": [],
        "tempo": [],
        "valence": []
    }
    audio_analysises = sp.audio_features([i["id"] for i in tracks['items']])
    print(audio_analysises)
    for audio_analysis in audio_analysises:
        data["acousticness"].append(audio_analysis['acousticness'])
        data['danceability'].append(audio_analysis['danceability'])
        data['energy'].append(audio_analysis['energy'])
        data['instrumentalness'].append(audio_analysis['instrumentalness'])
        data['liveness'].append(audio_analysis['liveness'])
        data['loudness'].append(audio_analysis['loudness'])
        data['speechiness'].append(audio_analysis['speechiness'])
        data['tempo'].append(audio_analysis['tempo'])
        data['valence'].append(audio_analysis['valence'])
        
    return data



#get top artists
def get_top_artists(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    data = sp.current_user_top_artists(limit=3, offset=0, time_range='medium_term')
    dict = {}
    for i in data['items']:
        id = i['id']
        name = i['name']
        genres = i['genres']
        dict[id] = [name, genres] # its gonna be {"id" : "name", [genres]}

    return dict



def get_personality():
    analyze = get_top_track_analyse(get_token_info())

    data = {
        "acousticness": [0.351, 0.676, 0.822, 0.681, 0.061, 0.0969, 0.928, 0.0227, 0.582, 0.132, 0.287, 0.25, 0.907, 0.813, 0.715, 0.0339],
        "danceability": [0.278, 0.692, 0.149, 0.695, 0.574, 0.928, 0.663, 0.77, 0.339, 0.817, 0.39, 0.491, 0.547, 0.614, 0.28, 0.557],
        "energy": [0.427, 0.497, 0.206, 0.282, 0.913, 0.526, 0.168, 0.775, 0.34, 0.599, 0.397, 0.802, 0.257, 0.235, 0.344, 0.54],
        "instrumentalness": [0, 0, 0.000649, 0.0267, 0.00158, 0.263, 0.0000568, 0.00262, 0.00297, 0.000311, 0, 0, 0.183, 0.00000568, 0.00642, 0.00248],
        "liveness": [0.145, 0.259, 0.115, 0.0767, 0.156, 0.153, 0.361, 0.297, 0.116, 0.0873, 0.207, 0.387, 0.0935, 0.161, 0.133, 0.179],
        "loudness": [-8.688, -7.316, -13.888, -15.359, -4.793, -6.486, -13.725, -9.571 -12.049, -9.249, -9.963, -9.966, -7.106, -12.358, -11.8, -12.577, -10.484],
        "speechiness": [0.0311, 0.119, 0.0323, 0.0295, 0.133, 0.161, 0.0448, 0.0495, 0.034, 0.0328, 0.0513, 0.0392, 0.0252, 0.0537, 0.0293, 0.0347],
        "tempo": [150.836, 81.308, 79.764, 91.681, 115.728, 109.958, 85.005, 116.935, 83.495, 108.873, 144.031, 119.25, 75.752, 75.178, 171.143, 129.171],
        "valence": [0.243, 0.475, 0.264, 0.445, 0.423, 0.753, 0.678, 0.802, 0.198, 0.548, 0.246, 0.472, 0.169, 0.413, 0.232, 0.394]
    }

    personality_traits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]  # Personality traits for simplicity
    X = np.array([data["acousticness"], data["danceability"], data["energy"], data["instrumentalness"], data["liveness"], data["loudness"], data["speechiness"], data["tempo"], data["valence"]]).T
    y = np.array(personality_traits)
    model = LinearRegression()
    model.fit(X, y)

    # Convert new data to numpy array
    X_new = np.array([analyze[key] for key in data.keys()]).T

    # Make prediction using the trained model
    predicted_personality = model.predict(X_new)
    main_personality_trait = int(round(np.mean(predicted_personality)))
    return personalities[main_personality_trait - 1]
    
        
def create_spotify_oauth():

    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('pass_token', _external=True),
        scope = "user-top-read"
    )

if __name__ == '__main__':  
   app.run()
