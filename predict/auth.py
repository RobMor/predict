import flask_login

from predict import db
import predict.models


def process_password(password, salt):
    """Processes the password by applying a salt and hash
    TODO
    """
    return password


def create_user(username, password):
    """Attempts to create a new user

    Args:
        username (str): The username for the new user
        password (str): The password for the new user
    Returns:
        True if the user was successfully created, False otherwise.
    """
    user = predict.models.User.query.filter_by(username=username).scalar()

    if user is None:
        salt = "qwerty" # TODO
        password = process_password(password, salt)
        new_user = predict.models.User(username=username, password=password, salt=salt)
        db.session.add(new_user)
        db.session.commit()

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
        password = process_password(password, user.salt)

        if user.password == password:
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
    user = predict.models.User.query.filter_by(username=username).first()

    return user
