from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time, json
import text2emotion as te
import config

app = Flask(__name__)


app.secret_key = config.SECRET_KEY

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET



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
            description = request.form['text']

            if (session.get('token_info')):
                token_info = get_token_info()
                artists = str(get_top_artists(token_info))
                tracks = str(get_top_tracks(token_info))
                #emotion = str(te.get_emotion(description))
                test = str(get_genres())
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
    return str(get_top_tracks(get_token_info()))


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


def get_top_tracks(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    data = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')
    dict = {}

    for i in data['items']:
        id = i["id"]
        name = i["name"]
        artists = []
        for g in i["artists"]:
            artists.append(g["id"]) 
        dict[id] = [name, artists] # its gonna be {"id" : "name", [artists_id]}
        
    return dict



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



def get_genres():
    sp = spotipy.Spotify(auth=get_token_info()['access_token'])
    artists = get_top_artists(get_token_info())
    tracks = get_top_tracks(get_token_info())
    genres_count = {}
    total = 0
    genres_percentage = {}

    for i in artists:
        for genre in artists[i][1]:
            if(genre in genres_count):
                #app.logger.error(genre + " exists as genre")
                genres_count[genre] = genres_count.get(genre, 0) + 1
                total += 1

    for track in tracks:
        for artist_id in tracks[track][1]:
            artist_info = sp.artist(artist_id)
            artist_genres = artist_info['genres']
            for i in artist_genres:
                #app.logger.error(i + " exists as i")
                genres_count[i] = genres_count.get(i, 0) + 1
                total += 1

    app.logger.error(total)
    for key in genres_count:
        persentage = (genres_count[key] / 100) * total
        genres_percentage[key] = str(persentage) + "%" 

    return genres_percentage
        


def get_personality():
    genres_count = get_genres()
    return ""




def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('pass_token', _external=True),
        scope = "user-top-read"
    )