from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
from pymongo import MongoClient
import ipdb
import random

app = Flask(__name__, static_folder='static', static_url_path='')
app.debug = True
app.secret_key = 'development'

client = MongoClient('localhost', 27017)
badgeit = client.badgeit
users = badgeit.users
challenges = badgeit.challenges
emails = badgeit.emails

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='yAlhD1bSfKYUBVMSmVzzzfqGW',
    consumer_secret='ct0zXMT0ThmpTW70EvHajTcIJRw1pwjJJdsvRcXh6pOT1Ep3dT',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/challenges', methods=['GET'])
def get_challenges():
    chals = reversed([challenge for challenge in challenges.find()])
    return render_template('challenges.html', challenges=chals)

@app.route('/create_challenge_page')
def create_challenge_page():
    return render_template('challenge_create.html')

@app.route('/create_challenge', methods=['POST'])
def create_challenge():
    number = str(random.randint(0, 1000000))
    fh = open("static/badges/" + number, "wb")
    fh.write(request.form['badgeImage'][22:].decode('base64'))
    fh.close()
    challenges.insert({'badgeImage': number, 'badgeTitle': request.form['badgeTitle'], 'badgeText': request.form['badgeText'],'name': g.user['screen_name'], 'claimed': []})
    return url_for('get_challenges')

@app.route('/email', methods=['POST'])
def email():
    emails.insert({'email': request.form['email']})
    return render_template('splash.html')

@app.route('/analytics', methods=['POST'])
def analytics():
    return render_template('splash.html')

@app.route('/challenge', methods=['GET'])
def challenge():
    name = request.args.get('name')
    challenge = challenges.find({'badgeImage': name})
    challenge = [c for c in challenge]
    showButton = True
    if challenge[0]['name'] == g.user['screen_name'] or challenge[0]['name'] in [item['name'] for item in challenge[0]['claimed']] or g.user == None:
        showButton = False
    return render_template('challenge_page.html', challenge=challenge[0], showButton=showButton)


@app.route('/claim_challenge', methods=['GET'])
def claim_challenge():
    name = request.args.get('name')
    doc = {}
    user = users.find_one({'name': g.user['screen_name']})
    doc['name'] = g.user['screen_name']
    doc['profile_image_url'] = user['profile_image_url']
    doc['validated'] = False
    challenges.update(
            {'badgeImage': name},
            {"$push": {'claimed': doc}}
    )
    return get_challenges()

@app.route('/highfive', methods=['get'])
def highfive():
    name = request.args.get('name')
    badgeImage = request.args.get('badgeImage')
    name = request.args.get('name')
    challenge = challenges.find_one({'badgeImage': badgeImage})
    doc_we_want = {}
    if challenge:
        if challenge['name'] == g.user['screen_name']:
            for doc in challenge['claimed']:
                if doc['name'] == name:
                    doc_we_want = doc
                    challenges.update(
                        {'badgeImage': badgeImage},
                        {'$pull': {'claimed': doc_we_want}}
                    )
                    doc_we_want['validated'] = True
                    challenges.update(
                        {'badgeImage': badgeImage},
                        {"$push": {'claimed': doc}}
                    )
    return redirect(url_for('challenge', name=badgeImage))

@app.route('/')
def index():
    tweets = None
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        userResp = twitter.request('users/show.json?screen_name='+ g.user['screen_name'])
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Unable to load tweets from Twitter.')
        if len([item for item in users.find({'name': g.user['screen_name']})]) == 0:
            users.insert({'name': g.user['screen_name'], 'victories': [], 'profile_image_url': userResp.data['profile_image_url']})
        return redirect(url_for('get_challenges'))
    else:
        return render_template('splash.html', tweets=tweets)



@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })
    if resp.status == 403:
        flash('Your tweet was too long.')
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
