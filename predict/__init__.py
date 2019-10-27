from flask import Flask

# Set app in __init__ so it's easily accessible throughout the app
app = Flask('predict', template_folder='templates')

# need to import after creating app so that the view definitions run on import
import predict.views
