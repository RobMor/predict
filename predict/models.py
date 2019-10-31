from flask_login import UserMixin
from predict import db


class User(UserMixin, db.Model):
     username = db.Column(db.String, primary_key=True)
     password_hash = db.Column(db.String, nullable=False)

     def __repr__(self):
          return f"<User username={self.username}>"

     def get_id(self):
          return self.username


class Label(db.Model):
     cve = db.Column(db.String, primary_key=True)
     username = db.Column(db.String, db.ForeignKey("user.username"), primary_key=True)
     fix_file = db.Column(db.String, primary_key=True)
     intro_file = db.Column(db.String, primary_key=True, nullable=True)

     fix_hash = db.Column(db.String)
     intro_hash = db.Column(db.String)

     repo_user = db.Column(db.String)
     repo_name = db.Column(db.String)

     edit_date = db.Column(db.DateTime)
