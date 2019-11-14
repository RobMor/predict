import re
import socket

import flask
import flask_login
import werkzeug.security
import sqlalchemy

import predict.db
import predict.models


def current_user():
    """Return the currently authenticated user, or a placeholder"""
    return flask_login.current_user.get_id() or socket.gethostname()


def create_user(username, password):
    """Attempts to create a new user

    Args:
        username (str): The username for the new user
        password (str): The password for the new user
    Returns:
        True if the user was successfully created, False otherwise.
    """
    user = load_user(username)

    if user is None:
        password_hash = werkzeug.security.generate_password_hash(password)
        new_user = predict.models.User(username=username, password_hash=password_hash)
        predict.db.Session.add(new_user)
        predict.db.Session.commit()

        return True
    else:
        return False


def authenticate_user(username, password):
    """Checks if the given credentials are correct

    Args:
        username (str): username to check
        password (str): password to check
    Returns:
        True if the given credentials refer to a valid user, False otherwise
    """
    user = load_user(username)

    if user is not None:
        auth = werkzeug.security.check_password_hash(user.password_hash, password)

        if auth:
            flask_login.login_user(user)
            return True

    return False


def load_user(username):
    """Loads the user object with the given username

    Args:
        username: The username of the user to load
    Returns:
        The user with the given username or None if the user doesn't exist.
    """
    user = (
        predict.db.Session.query(predict.models.User)
        .filter_by(username=username)
        .scalar()
    )
    return user


def valid_username(username):
    """Checks that a given username conforms to our constraints.

    Args:
        username (str): The username to be vetted

    Returns:
        True if the username is valid, False otherwise.
    """
    return re.fullmatch(flask.current_app.config['USERNAME_REGEX'], username) is not None


def valid_password(password):
    """Checks that a given password conforms to our constraints.

    Args:
        password (str): The password to be vetted

    Returns:
        True if the password is valid, False otherwise.
    """

    return re.fullmatch(flask.current_app.config['PASSWORD_REGEX'], password) is not None
