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
		initi = False
		for i in l[0]:
			if("Number in Agreement" == i):
				initi = True
		if not initi:
			l[0] = l[0] + ["Number in Agreement"]
			for i in range(1, len(l)):
				count = 0
				for j in range(1, len(l)):
					if i != j and l[i][0] == l[j][0] \
							and l[i][4] == l[j][4] and l[i][5] == l[j][5] and \
							l[i][6] == l[j][6] and l[i][7] == l[j][7]:
						count += 1
				l[i] = l[i] + [count]
			
		loc = 0
		for i in range(0, len(l[0])):
			if l[0][i] == "Number in Agreement":
				loc = i
		nl += [l[0]]
		for item in range(1, len(l)):
			already = False
			for i in nl:
				if l[item][0] == i[0]:
					already = True
			if not already:
				highest = l[item][loc]
				hi = l[item]
				for i in range(1, len(l)):
					if (l[i][loc] > highest):
						highest = l[i][loc]
						hi = l[i]
				nl += [hi]
		
		if not initi:
			temp = []
			for i in range(0, len(nl)):
				temp2 = []
				for j in range(0, len(nl[i])):		
					if j != loc and j != 1:
						temp2 += [nl[i][j]]
				temp += [temp2]
			nl = temp
		else:
			temp = []
			for i in range(0, len(nl)):
				temp2 = []
				for j in range(0, len(nl[i])):		
					if j != 1:
						temp2 += [nl[i][j]]
				temp += [temp2]
			nl = temp
		return nl