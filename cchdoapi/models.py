"""
Database Models
------------------
Some text here
"""
from random import getrandbits

from passlib.apps import custom_app_context as pwd_context
import jwt

from . import db
from . import app

class User(db.Model):
    """User class
    """
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
    def from_token(cls, token_payload):
        """Find and return a user object corresponding to the payload of a
        decoded JSON Web Token.

        :param dict token_payload: Decoded JWT payload, at a minimum it must
                                    have the key ``sub`` containing the user
                                    id, and the key ``ses`` which has the user
                                    session.
        :return: An SQLAlchemy ORM object instance
        :rtype: cchdoapi.models.User
        :raises sqlalchemy.orm.exc.NoResultFound: if no matching user is found,
                                    can be caused if the user session has been 
                                    invalidated.
        :raises sqlalchemy.orm.exc.MultipleResultsFound: if more than one
                                    matching user object is found, this is a
                                    serious situation which requires manual
                                    intervention.
        """
        return cls.query.filter_by(
                    id=token_payload["sub"],
                    session=token_payload["ses"],
                ).one()


#class Permission(db.Model):
#    pass
#
#class Type(db.Model):
#    pass
#
#class TypePermission(db.Model):
#    pass
#
#class Attachment(db.Model):
#    pass
#
#class Item(db.Model):
#    
#    pass
#
#class ItemHistory(db.Model):
#    pass
#
#class Queue(db.Model):
#    pass
#
#class APIKey(db.Model):
#    pass
