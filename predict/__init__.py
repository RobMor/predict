import sqlite3

from flask import Flask
import flask_login
import flask_sqlalchemy


# Configure App
app = Flask("predict")

# Configure SQLAlchemy
# TODO get database location from config...
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = flask_sqlalchemy.SQLAlchemy(app)

# Configure LoginManager
login_manager = flask_login.LoginManager(app)
login_manager.login_view = "login"
# TODO might want to get this key from a config file...
app.config["SECRET_KEY"] = "secret_xxx"

import predict.auth
login_manager.user_loader(predict.auth.load_user)

# Configure Data Models
import predict.models
db.create_all()

# Configure Views
import predict.views
