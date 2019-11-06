from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, DateTime


Model = declarative_base()


class User(UserMixin, Model):
     __tablename__ = "users"

     username = Column(String, primary_key=True)
     password_hash = Column(String, nullable=False)

     def __repr__(self):
          return "<User username={self.username}>"

     def get_id(self):
          return self.username


class Label(Model):
     __tablename__ = "labels"

     cve = Column(String, primary_key=True)
     username = Column(String, ForeignKey("users.username"), primary_key=True)
     fix_file = Column(String, primary_key=True)
     intro_file = Column(String, primary_key=True, nullable=True)

     fix_hash = Column(String)
     intro_hash = Column(String)

     repo_user = Column(String)
     repo_name = Column(String)

     edit_date = Column(DateTime)
