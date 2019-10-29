import flask_login
import flask
from predict import app, login_manager
#from predict.models import User
import predict.sqlite3_helper as sql3h
from predict.models import User

'''User callback function for getting the current user.  "This callback is used to reload the user object from the
user ID stored in the session. Called whenever a user has logged in." Authentication function.'''
@login_manager.user_loader
def load_user(username):
    print ("callback called with " + str(username))
    current_user = sql3h.check_UserNameExists(username)
    if current_user:
        print ("found! " + str(current_user))
        return User(username, sql3h.get_Password(username))
    else:
        print ("not found.")
        return None

@app.route("/logout")
@flask_login.login_required
def logout():
    print ("logout function called!")
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
        return flask.redirect(flask.url_for("login"))
    else:
        return "The user tried to logout when there was no user! (This should be a webpage or an error code.)"
