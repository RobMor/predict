# Predict Developer Instructions

## To install predict:

1. Please ensure that your command line has `python3` installed

2. In the same folder as the `setup.py` folder, which is `predict\prod\` do the following:  If you only have `python3` installed, use `$ pip install .` to install application dependencies. If your command line has both `python` and `python3` install the application with `$ python3 -m pip install -e .` or `$ pip3 install -e .`

## To run the webserver (no registration and login required):

1. `$ predict` or `$ predict up`

## To run the webserver in secured mode (registration and login required):

1. `$ predict up --secured`

### Navigate over to `localhost:5000` in your web browser of choice to view the application

## To run the tests:

1. `$ python -m unittest`

## To configure flask to to run in debug mode:

This way you can view stack traces in the web browser

1. Windows `set FLASK_ENV=development` and Linux `$ export FLASK_ENV=development`

2. You can change the mode back to production with `$ set FLASK_ENV=production` and `$ export FLASK_ENV=production` on Windows and Linux, respectively

## Locating your configuration file (and database file):

1. By default the Predict configuration file is stored in the user's home directory `~/.predict/config.ini`. Please note, the `.predict` folder is a hidden folder and may require hidden folders to be visible if you are using a GUI file browser or the command `$ ls -a` to view the `~/.predict/` folder

2. The predict database is also located in the same folder as `~/.predict/db.sqlite`

## Further Notes:

- Templates go in predict/templates. The templating engine we are using is called jinja2: https://jinja.palletsprojects.com/en/2.10.x/

- The code for the views goes in predict/views.py. There are examples already in there. The views are
associated with various endpoints. These endpoints can have variables in them.
There are also examples of the endpoints

- After your template and views are all set up you can run the webserver