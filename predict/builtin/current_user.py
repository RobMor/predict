from predict.plugins import FilterPlugin
import flask_login
import socket

class CurrentUser(FilterPlugin):
	id="current_user"
	description="Only Me"

	def __init__(self, query):
			self.username = predict.auth.current_user()
			self.query = query

	def filterq(self):
		return self.query.filter_by(username=self.username)