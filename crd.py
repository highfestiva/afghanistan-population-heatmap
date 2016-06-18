class crd:
	def __init__(self, x, y):
		self.x,self.y = x,y
	def lat(self):
		return -self.y
	def lng(self):
		return self.x
	def to_coord(self):
		return crd(self.x,-self.y)
	def __add__(self, v):
		return crd(self.x+v.x, self.y+v.y)
	def __sub__(self, v):
		return crd(self.x-v.x, self.y-v.y)
	def __mul__(self, f):
		return crd(self.x*f, self.y*f)
	def __truediv__(self, d):
		return crd(self.x/d, self.y/d)
	def __str__(self):
		return 'lat:%3.3f, lng:%3.3f' % (self.lat(),self.lng())
	def to_coord_str(self):
		return 'x:%3.3f, y:%3.3f' % (self.x,self.y)

def latlng(lat, lng):
	'''Use left-handed coordinate system, as that's what used for images.
	   Positive latitude thus defined as negative Y.'''
	return crd(lng,-lat)
