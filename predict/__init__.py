import sqlite3

from flask import Flask
import flask_login
import sqlalchemy
import configparser

import predict.config

def configure_app(config):
    # Configure App
    app = Flask("predict", static_url_path="")

    # Whether or not the whitelist exists will function as our whitelist enabled
    # flag
    if config.getboolean("WHITELIST", "WHITELIST_ENABLED"):
        config.remove_option("WHITELIST", "WHITELIST_ENABLED")
        app.config["WHITELIST"] = config["WHITELIST"].keys()

    app.config["USERNAME_REGEX"] = config["AUTHENTICATION"]["USERNAME_REGEX"]
    app.config["USERNAME_FEEDBACK"] = config["AUTHENTICATION"]["USERNAME_FEEDBACK"]
    app.config["PASSWORD_REGEX"] = config["AUTHENTICATION"]["PASSWORD_REGEX"]
    app.config["PASSWORD_FEEDBACK"] = config["AUTHENTICATION"]["PASSWORD_FEEDBACK"]

    # Configure SQLAlchemy
    import predict.db

    engine = sqlalchemy.create_engine("sqlite:///" + config["DATABASE"]["LOCATION"])
    predict.db.SessionFactory.configure(bind=engine)
    app.teardown_appcontext(predict.db.teardown_session)

    # Configure LoginManager
    app.config["SECRET_KEY"] = config["SECURITY"]["SECRET_KEY"]
    app.config["LOGIN_DISABLED"] = not config.getboolean("SECURITY", "LOGIN_REQUIRED")
    login_manager = flask_login.LoginManager(app)
    login_manager.login_view = "main.login"

    import predict.auth

    login_manager.user_loader(predict.auth.load_user)

    # Configure Data Models
    import predict.models

    predict.models.Model.metadata.create_all(engine)

    # Configure Views
    import predict.views

    app.register_blueprint(predict.views.blueprint)

    # Allow us to hash filenames so we can link to the info page
    app.jinja_env.globals.update(hash=hash)

    # Give us a consistent function to display datetimes with
    app.jinja_env.globals.update(datetime_format=predict.views.datetime_format)

    # Allow us to load svg images within templates.
    app.jinja_env.globals.update(svg=predict.views.svg)

    return app
