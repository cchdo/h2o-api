from flask import Flask
from flask import g
import click

from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/cchdoapi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = app.config["DEBUG"]
app.config["SECRET_KEY"] = "SOME SECRET"
db = SQLAlchemy(app)

from flask import jsonify, request
from werkzeug.exceptions import Unauthorized, BadRequest

import jwt

from .models import User


# Temporary workaround until #941 is fixed
# https://github.com/pallets/flask/issues/941
exceptions = (Unauthorized, BadRequest)

def handle_http_exception(error):
	return jsonify({
            'status_code': error.code,
            'message': str(error),
            'description': error.description
        }), error.code

for exception in exceptions:
    app.errorhandler(exception)(handle_http_exception)

@app.before_request
def get_user():
    auth = request.headers.get("Authorization")

    if auth and auth.startswith("Barrer "):
        untrusted_token = auth.split("Barrer ")[1].strip()

        try:
            token = jwt.decode(untrusted_token, app.config["SECRET_KEY"])
        except:
            raise Unauthorized()

        try:
            user = User.from_token(token)
        except:
            raise Unauthorized()

        g.user = user


@app.before_request
def get_permissions():
    pass

@app.route("/logout", methods=["POST"])
def logout():
    user = g.get("user")

    if user:
        user.new_session()
        db.session.add(user)
        db.session.commit()
    return ""

@app.route("/dummy")
def dummy():
    return g.user.email


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)

@app.route("/login", methods=["POST"])
def login():
    credentials = request.get_json(force=True)
    email = credentials.get("email")
    password = credentials.get("password", "")
    user = None

    if email is not None:
        try:
            user = User.query.filter_by(email=email).one()
        except Exception as e:
            raise Unauthorized()

    if user is not None and user.verify(password):
        return jsonify(access_token=user.jwt)

    raise Unauthorized()

@app.cli.command()
@click.option("--clean", is_flag=True)
def initdb(clean):
    if clean:
        db.drop_all()
    db.create_all()

@app.cli.command()
@click.option('--email', prompt=True)
@click.password_option()
def create_superuser(email, password):
    user = User(email, password)
    user.active = True
    db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    app.run()

