from flask import Flask
import click

from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/cchdoapi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "SOME SECRET"
db = SQLAlchemy(app)

from flask import jsonify, request

import jwt

from .models import User

@app.route("/testdb")
def test_db():
    return "ok"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

@app.route("/login", methods=["POST"])
def index():
    print(request.get_json())
    token = {"sub":1,}
    token = jwt.encode(token, app.config["SECRET_KEY"], algorithm='HS256')
    token = token.decode('utf-8')

    return jsonify(access_token=token)

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

