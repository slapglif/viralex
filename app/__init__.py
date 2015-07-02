from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

## set up flask and create database
app = Flask(__name__)
db = SQLAlchemy(app)
db.init_app(app)
engine = create_engine('mysql://root:Fuc5M4n15!@db.freebieservers.com/viralex', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt

bcrypt = Bcrypt(app)

from .models import User

def init_db():
    import app.models
    from app import views
    Base.metadata.create_all(bind=engine)

init_db()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()