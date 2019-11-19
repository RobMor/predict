from predict.plugins import FilterPlugin
import predict.auth
import socket

class CurrentUser(FilterPlugin):
	id="current_user"
	description="Only Me"

	def __init__(self, l):
			self.username = predict.auth.current_user()
			self.l = l

	def filterl(self):
		nl = [self.l[0]]
		for item in self.l:
			if item[1] == self.username:
				nl += [item]
		return nl