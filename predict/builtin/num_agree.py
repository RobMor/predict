from predict.plugins import DataPlugin


class NumAgree(DataPlugin):
	id="num_agree"
	description="Number In Agreement"

	
	def __init__(self, llist, q):
		self.llist = llist
		self.query = q
		
	def add_data(self):
		nlist = self.llist
		nlist[0] = nlist[0] + ["Number in Agreement"]
		for i in range(1, len(nlist)):
			count = 0
			for j in range(1, len(nlist)):
				if i != j and nlist[i][0] == nlist[j][0] \
						and nlist[i][4] == nlist[j][4] and nlist[i][5] == nlist[j][5] and \
						nlist[i][6] == nlist[j][6] and nlist[i][7] == nlist[j][7]:
					count += 1
			nlist[i] = nlist[i] + [count]
							
			
		return nlist