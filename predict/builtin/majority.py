from predict.plugins import ConflictPlugin


class Majority(ConflictPlugin):
	id="majority"
	description="Majority Rule"
	
	def __init__(self, l, query):
		self.l = l
		self.query = query

	def resolve(self):
		nl = []
		l = self.l
		templ = []
		already = False
		"""
		for i in range(1, len(l)):
			for k in range(1, len(nl)):
				if l[i][0] == nl[k][0]:
					already = True
			if not already:
				for k in range(1, len(l)):
					if l[i][0] == l[k][0] and l[i][2] == l[k][2] and l[i][3] == l[k][3]:
						if l[i][4] == l[k][4] and l[i][5] == l[k][5] and l[i][6] == l[k][6] and l[i][7] == l[k][7]:
							
			already = False	
			"""
		return nl