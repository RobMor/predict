from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, DateTime


Model = declarative_base()


class User(UserMixin, Model):
     __tablename__ = "users"

     username = Column(String, primary_key=True)
     password_hash = Column(String, nullable=False)

     def get_id(self):
          return self.username


class Label(Model):
     __tablename__ = "labels"

     cve_id = Column(String, primary_key=True)
     username = Column(String, ForeignKey("users.username"), primary_key=True)
     repo_user = Column(String, primary_key=True)
     repo_name = Column(String, primary_key=True)
     fix_file = Column(String, primary_key=True)
     intro_file = Column(String, primary_key=True, nullable=True)

     fix_hash = Column(String, nullable=False)
     intro_hash = Column(String)

     edit_date = Column(DateTime, nullable=False)
