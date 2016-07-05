from flask import Flask
import click

from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/cchdoapi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "SOME SECRET"
db = SQLAlchemy(app)

from flask import jsonify, request
from werkzeug.exceptions import Unauthorized

import jwt

from .models import User


# Temporary workaround until #941 is fixed
# https://github.com/pallets/flask/issues/941
exceptions = (Unauthorized, )

def handle_http_exception(error):
	return jsonify({
            'status_code': error.code,
            'message': str(error),
            'description': error.description
        }), error.code

for exception in exceptions:
    app.errorhandler(exception)(handle_http_exception)

@app.route("/test_jwt")
def test_jwt():
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Barrer "):
        token = auth.split("Barrer ")[1].strip()
        try:
            token = jwt.decode(token, app.config["SECRET_KEY"])
        except:
            raise Unauthorized()
        return str(token)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

@app.route("/login", methods=["POST"])
def index():
    credentials = request.get_json()
    email = credentials.get("email")
    password = credentials.get("password")
    if email is not None:
        try:
            user = User.query.filter_by(email=email).one()
        except Exception as e:
            raise Unauthorized()

    if user.verify(password):
        token = {"sub":user.id,}
        token = jwt.encode(token, app.config["SECRET_KEY"], algorithm='HS256')
        token = token.decode('utf-8')

        return jsonify(access_token=token)

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

