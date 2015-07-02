##My Personal Boiler Plate for all FLASK Apps ##
from app.models import User
import re, requests, time, datetime
from app import app, engine, db_session
from mandril import drill
from flask import Flask, redirect, url_for, render_template, flash, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from itsdangerous import URLSafeTimedSerializer
from subprocess import (PIPE, Popen)
from flask.ext.login import login_user
import json

app.config['SECRET_KEY'] = 'top secret!'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '470154729788964',
        'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}



ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
lm = LoginManager(app)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    user = None
    if 'user' in session:
        user = User.query.filter_by(id=session['user']).first()
    output = render_template('dashboard/index.html',user=user)

    return output


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.form.get("email"):
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user.is_correct_password(request.form.get("password")):
            login_user(user)
            print "password is correct"
            session['user'] = json.dumps(str(user))
            return redirect(url_for('index'))
        else:
            print "password is not correct"
            return redirect(url_for('login'))
    print "no password"
    return render_template('dashboard/login.html')


@app.route("/register")
def register():

    output = render_template('dashboard/register.html')
    return output


@app.route('/register/create', methods=["GET", "POST"])
def create_account():
    if request.form.get("email"):
        email = request.form.get("email")
        password = request.form.get("password")
        user = User(nickname=request.form.get("username"), email=request.form.get("email"), password=request.form.get("password"), vpoints=0, email_confirmed=0)
        db_session.add(user)
        db_session.commit()

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

        # We'll assume that send_email has been defined in myapp/util.py
        drill(user.email, subject, html)

        return redirect(url_for("index"))

    x = request.form.get("email")

    print "x is %s"%x

    return render_template("dashboard/register.html")



@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        return "404"

    user = User.query.filter_by(email=email).first()

    user.email_confirmed = True

    db_session.add(user)
    db_session.commit()
    session['user'] = user.id


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

@app.route("/mypages")
def mypages():
    return render_template("dashboard/mypages.html",content=None)

@app.route("/earn/<ss>")
def earn(ss):
    output = render_template("dashboard/earn.html",earn=ss,content=None)
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
