from passlib.apps import custom_app_context as pwd_context

from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.encrypt(password)

    def verify(self, password):
        return pwd_context.verify(password, self.password)

    @classmethod
    def from_dict(cls, dict):
        email = dict.get("email")
        password = dict.get("password")
        return cls(email, password)
