from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin
from app import db_session,Base, app
from sqlalchemy import Column, Integer, String, Boolean, BLOB
from sqlalchemy.ext.hybrid import hybrid_property

from . import bcrypt
BCRYPT_LOG_ROUNDS = 12

class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    aid = Column(Integer)
    type = Column(String(64), nullable=True)
    url = Column(String(128), nullable=True)
    gender = Column(String(64), nullable=True)
    countries = Column(String(128), nullable=True)
    ppc = Column(Integer)
    status = Column(Boolean(), nullable=True)


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    social_id = Column(String(64), nullable=True, unique=True)
    nickname = Column(String(64), nullable=True, unique=True)
    email = Column(String(64), nullable=True, unique=True)
    vpoints = Column(String(64), nullable=True)
    email_confirmed = Column(Boolean(), nullable=True)
    _password = Column(String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        if bcrypt.check_password_hash(self._password, plaintext):
                return True

        return False

    @staticmethod
    def get_or_create(email):
        rv = User.query.filter_by(email=email).first()
        if rv is None:

            return rv
