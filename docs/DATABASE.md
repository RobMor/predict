# Database Configuration

We are currently using an sqlite3 database backend with a SQLAlchemy interface.
All of the data models are described in `predict.models`.

## Basics

To run a query to get a piece of information you first need to acquire a
database session. You can do this with `predict.db.create_session`. This
method is a context manager and is meant to be used with a `with` statement.
Here's an example query finding a user with the username `username`:

```py
with predict.db.create_session() as session:
    user = session.query(predict.models.User).filter_by(username=username).first()

    return user
```

We get the session using the with block, then query the session for our User
data model and filter by entries with the username we're looking for.

There are more details in the sqlalchemy documentation.


## Tables

Right now there are only two tables, `users` and `labels`.

Users have the following fields

* Username
* Password Hash

Labels have the following fields

* CVE ID
* Username of the user who made this label
* GitHub Repository user
* GitHub Repository name
* Name of the fix file
* Fix Hash
* Name of the intro file
* Intro Hash
* Date of last edit

More details are in `predict.models`
