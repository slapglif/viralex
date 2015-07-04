##My Personal Boiler Plate for all FLASK Apps ##
from app.models import User, Page
import re, requests, time, datetime
from app import app, engine, db_session
from mandril import drill
from flask import Flask, redirect, url_for, render_template, flash, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from oauth import OAuthSignIn
from itsdangerous import URLSafeTimedSerializer
from subprocess import (PIPE, Popen)
from flask_oauth import OAuth
import json

app.config['SECRET_KEY'] = 'top secret!'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1589724287960064',
        'secret': '9f737bb729717ce5d2b944b6a582713e'
    },
    'twitter': {
        'id': '3300611698-hUe5gp2oS1c6UQOhVZ1idF1JbW0o059jgXc4Syf',
        'secret': 'gPWBRQXjkGgYSLCYlfMgOrLnLUO3U2tDhQhcZ8tCZRVnD'
    }
}




oauth = OAuth()

# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1/',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authenticate',
    # the consumer keys from the twitter application registry.
    consumer_key='vc5zMaa1FJ1xrWL6E0YTE8G3I',
    consumer_secret='g0fINwUZU4RpNi3ilWDskK2PWtk7UYqLrilDUE6G9uiHpgTphy'
)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = User.query.get(session['user'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response




ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
lm = LoginManager(app)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    user = None
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
    output = render_template('dashboard/index.html',user=user)

    return output



@app.route('/social')
def social():
    user = None
    output = render_template('dashboard/social.html',user=user)
    if current_user.is_authenticated():
        if 'user' in session:
            user = User.query.filter_by(id=session['user']).first()
            if user.email == None:
                output = render_template('dashboard/social.html',user=user)
            else:
                output = redirect(url_for("index"))

    return output


@app.route("/login", methods=["GET", "POST"])
def login():


    if request.form.get("email"):
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user.is_correct_password(request.form.get("password")):
            login_user(user, True)
            print "password is correct"
            session['user'] = user.id
            return redirect(url_for('index'))
        else:
            print "password is not correct"
            return redirect(url_for('login'))
    print "no password"

    return render_template('dashboard/login.html')

@app.route("/twlogin")
def twlogin():
    # """Calling into authorize will cause the OpenID auth machinery to kick
    # in.  When all worked out as expected, the remote application will
    # redirect back to the callback URL provided.
    # """
    return twitter.authorize(callback=url_for('oauth_authorized',
      next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
  next_url = request.args.get('next') or url_for('index')
  if resp is None:
      return redirect(next_url)

  this_account = User.query.filter_by(nickname = resp['screen_name']).first()
  if this_account is None:
      new_account = User(nickname=resp['screen_name'], oauth_token=resp['oauth_token'], oauth_secret=resp['oauth_token_secret'])
      db_session.add(new_account)
      db_session.commit()
      login_user(new_account, True)
  else:
      login_user(this_account, True)

  return redirect(url_for("social"))


@twitter.tokengetter
def get_twitter_token():
  if current_user.is_authenticated():
      return (current_user.token, current_user.secret)
  else:
      return None



@app.route("/register")
def register():

    output = render_template('dashboard/register.html')
    return output


@app.route('/register/create', methods=["GET", "POST"])
def create_account():
    output = render_template("dashboard/register.html")
    if request.form.get("email"):
        output = redirect(url_for("index"))
        email = request.form.get("email")
        if request.form.get("password") != None:
            password = request.form.get("password")
        else:
            password = "test"
        exists = User.query.filter_by(email=email).first()
        if current_user.is_authenticated():
            user = User(nickname=request.form.get("username"), email=email, password=password, vpoints=0, email_confirmed=0, oauth_token=current_user.token, oath_secret=current_user.secret)
        else:
            user = User(nickname=request.form.get("username"), email=email, password=password, vpoints=0, email_confirmed=0)

        # Now we'll send the email confirmation link
        subject = "Confirm your email"

        token = ts.dumps(user.email, salt='email-confirm-key')

        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)

        html = render_template(
            'dashboard/email/activate.html',
            confirm_url=confirm_url)

        if exists == None:
            db_session.add(user)
            db_session.commit()
            login_user(user, True)
            drill(user.email, subject, html)
        else:
            print "x is %s"
            db_session.merge(user)
            db_session.commit()
            login_user(user, True)
            output = redirect(url_for("index"))


    return output




@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        return "404"

    user = User.query.filter_by(email=email).first()

    user.email_confirmed = True
    session['user'] = user.id
    db_session.commit()


    return redirect('/')



@app.route("/lostpw")
def lostpw():
    return render_template('dashboard/lostpw.html')



@app.route('/logout')
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db_session.add(user)
        db_session.commit()
    login_user(user, True)
    return redirect(url_for('index'))



## Get human readable date ##
dateList = []
today = datetime.date.today()
dateList.append(today)

## Useful if you need to access os cmd's ##
def cmd(command):
  return Popen(command, shell=True, stdout=PIPE)


@app.route("/addpage")
def addpage():
    return render_template("dashboard/addpage.html")

@app.route("/addpage/type/")
def types():
    type = request.args.get('value', '')
    return render_template("dashboard/types.html",type=type)

@app.route("/mypages", methods=['POST', 'GET'])
def mypages():
    user = None
    content = None
    pages = Page.query.filter(Page.url.isnot(None))

    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()

    output = render_template("dashboard/mypages.html",pages=pages,user=user)

    return output

@app.route("/mypages/add", methods=['POST', 'GET'])
def page():

    user = None
    content = None
    pages = Page.query.filter(Page.url.isnot(None))

    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
    if request.form.get("inputURL") != None:
        content = {"aid": user.id, "url": request.form.get("inputURL"),"gender": request.form.get("gender"),"countries": request.form.get("countries"),"ppc": request.form.get("points")}
        page = Page(aid=user.id, url=request.form.get("inputURL"), type=request.form.get("type"), gender=request.form.get("gender"), countries=request.form.get("countries"), ppc=request.form.get("points"), ex=0)
        db_session.add(page)
        db_session.commit()
    return render_template("dashboard/page.html",pages=pages,user=user)



@app.route("/earn/<ss>")
def earn(ss):
    pages = Page.query.filter(Page.url.isnot(None))
    types = Page.query.filter_by(type=ss)
    output = render_template("dashboard/earn.html",earn=ss,pages=pages,types=types)
    return output

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard/index.html")


@app.route("/buy")
def funds():
    return render_template("dashboard/buy.html")


@app.route("/vip")
def vip():
    return render_template("dashboard/vip.html")

@app.route("/checkout")
def checkout():
    return render_template("dashboard/checkout.html")

@app.route("/exchange")
def exchange():
    return render_template("dashboard/exchange.html")
