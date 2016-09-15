"""
Database Models
------------------
Some text here
"""
from collections import defaultdict
from random import getrandbits

from passlib.apps import custom_app_context as pwd_context
import jwt

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from . import app

def repr(instance, **kwargs):
    repr_string = "<{classname} ".format(
            classname=instance.__class__.__name__
            )

    key_values = []
    for key, value in kwargs.items():
        key_values.append(
            "{key}='{value}'".format(
                key=key,
                value=value
                )
            )
    repr_string += ", ".join(key_values)
    repr_string += ">"
    return repr_string

class User(db.Model):
    """User class
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    session = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.new_session()

    def __repr__(self):
        return repr(self, 
                email=self.email, 
                active=self.active,
                session=self.session
                )

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
    def from_token(cls, token):
        """Find and return a user object corresponding to the payload of a
        decoded JSON Web Token.

        :param dict token: Decoded JWT payload, at a minimum it must
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
                    id=token["sub"],
                    session=token["ses"],
                ).one()


class Permission(db.Model):
    """Permission class
    """
    __tablename__ = "permission"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    default = db.Column(db.Boolean, nullable=False, default=False)

#class APIKey(db.Model):
#    pass


type_relations = db.Table(
        "type_relations",
        db.Column("left_id",
            db.Integer, 
            db.ForeignKey("type.id"),
            primary_key=True,
            ),
        db.Column("right_id", 
            db.Integer, 
            db.ForeignKey("type.id"), 
            primary_key=True,
            ),
        )

class Type(db.Model):
    """Type class
    """
    __tablename__ = "type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    schema = db.Column(JSONB, nullable=False)
    context = db.Column(JSONB)

    _relations = relationship("Type", 
                secondary=type_relations,
                primaryjoin=id==type_relations.c.left_id,
                secondaryjoin=id==type_relations.c.right_id,
                lazy="joined",
                join_depth=1,
            )

    def __repr__(self):
        return repr(self,
                name=self.name
                )

    @property
    def relations(self):
        return tuple(self._relations)

    def link(self, other):
        if self not in other._relations:
            other._relations.append(self)
        if other not in self._relations:
            self._relations.append(other)

    def unlink(self, other):
        if self in other._relations:
            other._relations.remove(self)
        if other in self._relations:
            self._relations.remove(other)


#class TypePermission(db.Model):
#    pass
#
#class Attachment(db.Model):
#    pass
#

class ItemRelations(db.Model):
    __tablename__ = "item_relations"

    left_id = db.Column(
            db.Integer, 
            db.ForeignKey("item.id"),
            primary_key=True,
            )
    right_id = db.Column(
            db.Integer, 
            db.ForeignKey("item.id"), 
            primary_key=True,
            )

    left_type_id = db.Column(db.Integer, nullable=False)
    right_type_id = db.Column(db.Integer, nullable=False)
    ForeignKeyConstraint(
            [left_type_id, right_type_id],
            ["type_relations.left_id", "type_relations.right_id"],
            )

    role_name = db.Column(db.String)

    self_item = relationship("Item", foreign_keys=[left_id])
    item = relationship("Item", foreign_keys=[right_id])

    def __init__(self, left, right, role=None):
        self.self_item = left
        self.item = right
        self.role_name = role
        self.left_type_id = left._type.id
        self.right_type_id = right._type.id

class Item(db.Model):
    """The :py:class:`.Item` class represents the actual data of some
    :py:class:`.Type`.
    """
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(JSONB, nullable=False, index=True)

    links = relationship("ItemRelations", 
            primaryjoin=id==ItemRelations.left_id,
            lazy="joined",
            cascade="all, delete-orphan",
            )

    linked_items = association_proxy("links", "item")


    _type_id = db.Column(db.Integer, 
            db.ForeignKey("type.id"), 
            nullable=False,
            )
    _type = relationship("Type",
            lazy="joined",
            )

    def to_dict(self, depth=1):
        """Dump the value to a python dict.

        .. todo::
            Figure out how to handle the filtering of attached items, the
            sqlalchemy docs suggest that is should be possible to push the
            filtering down to the database level, in which case this method can
            always return the entire object

            http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#using-contains-eager-to-load-a-custom-filtered-collection-result
        """
        d = defaultdict(list)
        d.update(self.value)
        d["id"] = self.id

        if depth > 0:
            for link in self.links:
                link_dict = link.item.to_dict(depth=depth-1)
                if link.role_name:
                    link_dict["roleName"] = link.role_name
                d[link.item._type.name].append(link_dict)

        return d

    @property
    def type_name(self):
        return self._type.name

    def __repr__(self):
        return repr(self,
                id=self.id,
                type_name=self.type_name,
                value=self.value,
                )

    def unlink(self, other):
        """Unlink two :py:class:`.Item` instances.
        """
        if other in self.linked_items:
            self.linked_items.remove(other)
        if self in other.linked_items:
            other.linked_items.remove(self)

    def link(self, other, role=None):
        """Links two :py:class:`.Item` instances and optionally allows a role
        name to be added to the link. Calling this method on two already linked
        instances will update the role name of that relationship (including
        setting it to None).
        """
        link = ItemRelations(self, other, role=role)
        reverse_link = ItemRelations(other, self, role=role)

        # Sqlalchemy is smart enough to turn a remove then add again into an
        # SQL UPDATE rather than a DELETE and INSERT
        if other in self.linked_items:
            self.unlink(other)

        if other not in self.linked_items:
            self.links.append(link)
            object_session(self).add(link)
        if self not in other.linked_items:
            other.links.append(reverse_link)
            object_session(other).add(reverse_link)

#class ItemHistory(db.Model):
#    pass
#
#class Queue(db.Model):
#    pass
#
