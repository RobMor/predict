from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


SessionFactory = sessionmaker()
Session = scoped_session(SessionFactory)


def teardown_session(e):
    """Tears down the thread-local DB session. Called when a request ends."""
    Session.remove()