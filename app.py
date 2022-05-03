from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

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
            app.logger.error(session)
            if (session.get('token_info')):
                text = get_playlist(session['token_info'])
                return render_template("index.html", text=text)
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
    app.logger.error(session['token_info'])
    #return render_template("index.html", text=session['token_info'])
    return get_playlist(session['token_info'])


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
def get_playlist(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    data = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')
    return data


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('pass_token', _external=True),
        scope = "user-top-read"
    )