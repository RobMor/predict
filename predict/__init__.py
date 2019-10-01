from flask import Flask

# Set app in __init__ so it's easily accessible throughout the app
app = Flask(__name__)

# need to import after creating app so that the view definitions run on import
import predict.views
