from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time, json
import text2emotion as te

app = Flask(__name__)


app.secret_key = 'henta!'

CLIENT_ID = 'f55bea887a4443b4b81dac5b70630ea2'
CLIENT_SECRET = '6c057c30b75744cf95a6383406f47a9d'



@app.route("/")
@app.route("/home", methods = ['GET', 'POST'])
def home():
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
                test = get_genres()
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
    #return render_template("index.html", text=session['token_info'])
    return str(get_top_tracks(get_token_info(), 2))


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


#for now it gets top tracks and sends it back
def get_top_tracks(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    data = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')
    dict = {}

    for i in data['items']:
        id = i["id"]
        name = i["name"]
        artists = []
        for g in i["artists"]:
            artists.append(g["id"]) # its not appending fix it
            app.logger.error(g["id"])
        dict[id] = [name, artists] # its gonna be {"id" : "name", [artists_id]}
        
    return dict



#get top artists
def get_top_artists(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    data = sp.current_user_top_artists(limit=10, offset=0, time_range='medium_term')
    dict = {}


    for i in data['items']:
        id = i['id']
        name = i['name']
        genres = i['genres']
        dict[id] = [name, genres] # its gonna be {"id" : "name", [genres]}

    return dict



def get_genres():
    sp = spotipy.Spotify(auth=get_token_info()['access_token'])
    artists = str(get_top_artists(get_token_info()))
    tracks = str(get_top_tracks(get_token_info()))
    genres_count = {}

    test = {}
    for i in artists:
        for genre in i:
            if(genre in genres_count):
                genres_count[genre] = genres_count[genre] + 1
            else:
                genres_count[genre] = 1
    for track in tracks:
        for artist_id in track:
            app.logger.error(track)
            app.logger.error(artist_id)
            test = sp.artist(artist_id)
    return test
        





def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('pass_token', _external=True),
        scope = "user-top-read"
    )