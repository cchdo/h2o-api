from flask import Flask
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

@app.route("/register", mehtods=["POST"])
def register():
    data = request.get_json()



@app.route("/login", methods=["POST"])
def index():
    print(request.get_json())
    token = {"sub":1,}
    token = jwt.encode(token, app.config["SECRET_KEY"], algorithm='HS256')
    token = token.decode('utf-8')

    return jsonify(access_token=token)

if __name__ == "__main__":
    app.run()

