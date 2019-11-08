import sqlite3

from flask import Flask
import flask_login
import sqlalchemy


def configure_app(config):
    # Configure App
    app = Flask("predict")

    app.config["WHITELIST"] = config["WHITELIST"].keys()
    app.config["USERNAME_REGEX"] = config["AUTHENTICATION"]["USERNAME_REGEX"]
    app.config["PASSWORD_REGEX"] = config["AUTHENTICATION"]["PASSWORD_REGEX"]

    # Configure SQLAlchemy
    import predict.db

    # TODO get database location from the config
    engine = sqlalchemy.create_engine("sqlite:///db.sqlite")
    predict.db.SessionFactory.configure(bind=engine)
    app.teardown_appcontext(predict.db.teardown_session)

    # Configure LoginManager
    app.config["SECRET_KEY"] = config["SECURITY"]["SECRET_KEY"]
    app.config["LOGIN_DISABLED"] = not config["SECURITY"].getboolean("LOGIN_REQUIRED")
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

    return app
