# Predict Developer Instructions

Templates go in predict/templates. The templating engine we are using is called
jinja2: https://jinja.palletsprojects.com/en/2.10.x/. The code for the views
goes in predict/views.py. There are examples already in there. The views are
associated with various endpoints. These endpoints can have variables in them.
There are also examples of the endpoints. After your template and view are all
set up you can run the webserver and navigate to localhost:5000 in your web
browser in order to test your stuff...

## To run the webserver:

In the same folder as the `setup.py` folder, which is `\prod\` run: 

1. `$ pip install .`
2. `$ predict`

## To configure flask to to run in debug mode:
### This way you can view stack traces in the web browser

Windows `set FLASK_ENV=development` and Linux `export FLASK_ENV=development`
you can change the mode back to production with set `FLASK_ENV=production`


