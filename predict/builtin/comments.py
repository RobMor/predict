from predict.plugins import DataPlugin


class Comments(DataPlugin):
	id="comments"
	description="Comments"
	
	def __init__(self, llist, q):
		self.llist = llist
		self.query = q
		
	def add_data(self):
		nlist = self.llist
		clist = [l.comment for l in self.query]
		nlist[0] = nlist[0] + ["Comment"]
		for i in range(1, len(nlist)):
			nlist[i] = nlist[i] + [clist[i - 1]]
			
		return nlist
