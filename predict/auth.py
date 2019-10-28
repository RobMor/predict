import flask_login
from flask_login import UserMixin

from predict import login_manager


class User(UserMixin):
    def __init__(self, username):
        self.username = username
        self.password = password

    def get_id(self):
        return self.name


'''User callback function for getting the current user.  "This callback is used to reload the user object from the
user ID stored in the session. Called whenever a user has logged in." Authentication function.'''
@login_manager.user_loader
def load_user(username):
    print ("callback called with " + username)
    if username in users:
        print ("found!")
        return users[username]
    else:
        print ("not found.")
        return None
