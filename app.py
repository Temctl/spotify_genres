from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)


token = ''

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

        if (not session.get('token')):
            #get user's token
            pass
        else:
            text = get_playlist(session['token'])

        _request = request.form['text']
        text = _request
        app.logger.error(text)
        return render_template("index.html", text=text)


@app.route("/callback")
def pass_token():
    _request = request.form['token']



def get_playlist(token):
    url=''
    return url
