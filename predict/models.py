from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime


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
     group_num = Column(Integer, primary_key=True)
     label_num = Column(Integer, primary_key=True)

     repo_user = Column(String)
     repo_name = Column(String)
     fix_file = Column(String)
     intro_file = Column(String)

     fix_hash = Column(String)
     intro_hash = Column(String)

     comment = Column(String)

     edit_date = Column(DateTime, nullable=False)
