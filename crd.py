class crd:
	def __init__(self, x, y):
		self.x,self.y = x,y
	def lat(self):
		return -self.y
	def lng(self):
		return self.x
	def __add__(self, v):
		return crd(self.x+v.x, self.y+v.y)
	def __sub__(self, v):
		return crd(self.x-v.x, self.y-v.y)
	def __mul__(self, s):
		return crd(self.x*s, self.y*s)
	def __div__(self, s):
		return crd(self.x/s, self.y/s)

def latlng(lat, lng):
	return crd(lng,-lat)
