import flask
import flask_login
import werkzeug.security
import sqlalchemy

import predict.db
import predict.models


def create_user(username, password):
    """Attempts to create a new user

    Args:
        username (str): The username for the new user
        password (str): The password for the new user
    Returns:
        True if the user was successfully created, False otherwise.
    """

    with predict.db.create_session() as session:
        user = session.query(predict.models.User).filter_by(username=username).scalar()

        if user is None:
            password_hash = werkzeug.security.generate_password_hash(password)
            new_user = predict.models.User(username=username, password_hash=password_hash)
            session.add(new_user)

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
    with predict.db.create_session() as session:
        user = session.query(predict.models.User).filter_by(username=username).first()

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
    with predict.db.create_session() as session:
        user = session.query(predict.models.User).filter_by(username=username).first()

        return user
