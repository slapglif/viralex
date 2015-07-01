##My Personal Boiler Plate for all FLASK Apps ##
from app.models import User
import re, requests, time, datetime
from app import app, engine, db_session

from flask import Flask, redirect, url_for, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn

app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
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

db = db_session
lm = LoginManager(app)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('dashboard/index.html')




@app.route('/logout')
def logout():
    logout_user()
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
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


from subprocess import (PIPE, Popen)




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
