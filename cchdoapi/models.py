from random import getrandbits

from passlib.apps import custom_app_context as pwd_context
import jwt

from . import db
from . import app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    session = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.new_session()

    def verify(self, password):
        return pwd_context.verify(password, self.password)

    def new_session(self):
        self.session = "{:x}".format(getrandbits(64))

    @property
    def jwt(self):
        payload = {
                "sub": self.id,
                "ses": self.session,
                }
        token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm='HS256')
        token = token.decode('utf-8')
        return token

    @classmethod
    def from_dict(cls, dict):
        email = dict.get("email")
        password = dict.get("password")
        return cls(email, password)
