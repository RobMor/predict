from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker


SessionFactory = sessionmaker()


@contextmanager
def create_session():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
