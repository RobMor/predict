# Predict Developer Introduction

Predict is a Python application and requires at least version Python 3.5 to
operate correctly. 

## Getting Started

Ensure that you have at least Python 3.5 or above installed. 

```
$ python3 --version
Python 3.5.3
```

Navigate to the directory of this repository containing the `setup.py` file and
run:

```
$ python3 -m pip install -e .
```

This command installs predict and it's dependencies on your machine. It also
sets the repository up so that you can edit the source files of predict without
having to re-install by including the `-e` option. It is also recommended that
you enable Flask's debug mode so that you can edit the code and Flask will
automatically reload the application. You can do this by setting the environment
variable `FLASK_ENV` to `development`

Now you should be able to run the `predict` command to start the application.
Navigating to `localhost:5000` should present you with the dashboard of predict.

If you are testing the security aspects of Predict you may want to start the app
with the `--secured` option like so:

```
$ predict up --secured
```

This will enable the login mechanisms and require that any users accessing the
app log in.

## Running the Tests

To run the unit test suite for predict you can run the following command from
the base directory of this repository:

```
$ python -m unittest
```

## Locating the Configuration file and Database

The configuration file is by default located in your home directory under a 
folder named `.predict`. More information is in CONFIGURATION.md. The location
of the database is specified in the config. The default location is in the same
`.predict` folder.

## Program Structure

Predict is a Flask application. As most Flask applications do, Predict centers
around a single Python module in which it stores all the backend logic, the
templates, and static files associated with the app. In this repository this is
`predict/`. Tests reside in the `tests/` directory and follow the standard
Python unittest format. Documentation resides in the `docs/` directory. Any
package related files remain at the top level of the repository. This includes
the `setup.py` file to allow users to easily pip install the program. It also
includes the files necessary to set predict up on a webserver in `predict.conf`
and `predict.wsgi`.

### `predict/`

Within the `predict` directory there are multiple Python modules and several
folders. Here we will enumerate the high-level purpose of each of these files
and then delve into the sub directories.

* `auth.py`: Authentication
* `cli.py`: Command Line Interface
* `config.py`: Configuration File
* `conflict_resolution.py`: Conflict Resolution
* `cve.py`: CVE Entry Web Scraping
* `db.py`: Database
* `github.py`: GitHub Commit and Blame Web Scraping
* `labels.py`: Labeling
* `models.py`: Database ORM (SQL-Alchemy) Models
* `plugins.py`: Plugins
* `views.py`: Front End Serving (Putting it all together)

#### `predict/builtin/`

This sub folder of predict houses the Python modules making up the plugins
included with predict. A plugin has the ability to change how data is exported
from predict.

* `comments.py`: Defines additional data in the form of comments
* `csv.py`: Defines the CSV data format
* `current_user.py`: Defines the filter which limits data to the current user
* `majority.py`: Defines the majority rule conflict resolution strategy
* `num_agree.py`: Defines additional data in the form of number of agreements

#### `predict/static`

This sub folder of predict houses the static files of the app. These mostly
correspond to the front end of the application. All CSS goes in the `css`
subfolder, all JavaScript in the `js` folder and all vector graphics go in the
`svg` folder. 

#### `predict/templates`

This sub folder contains all the Jinja 2 templates used by the application. The
code in `views.py` renders these templates which tells Jinja to fill in the
sections surrounded by `{{ }}`.

* `base.html`: The base template. All other templates should at least inherit from this.
* `blame_diff.html`: The code section of the blame page
* `blame.html`: The other parts of the blame page
* `conflict_resolution.html` The conflict resolution page
* `dashboard.html`: The dashboard page
* `error.html`: The error page. Users are directed here on 404 errors.
* `info_diff.html`: The code sections of the info page (included multiple times)
* `info.html`: The other parts of the info page
* `label_group.html`: A group of labels that shows up in the CVE sidebar
* `label.html`: A single label that shows up in a label group
* `login.html`: The login page
* `register.html`: The registration page
* `sidebar_base.html`: The basic empty sidebar template
* `sidebar_cve.html`: The sidebar filled with CVE info and labeling tools
