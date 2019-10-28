from flask import Flask
import flask_login

# Set app in __init__ so it's easily accessible throughout the app
app = Flask('predict', template_folder='templates')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config.update(
    SECRET_KEY = 'secret_xxx'
)

# TODO: Later on this hash of users will be converted into database calls. These users are not neccessarily authenticated.
users = {}
# end login stuff

# need to import after creating app so that the view definitions run on import
import predict.views
