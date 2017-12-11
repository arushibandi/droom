#This class just makes it easier to do the preprocessing in the original image
#To find large areas to turn into POIs and try to find recommendations for
class Rect(object):
	def __init__(self, x, y, w, h):
		self.left = x
		self.right = x+w
		self.top = y
		self.bottom = y+h
		self.area = w*h
		self.cX = int(self.left + w/2)
		self.cY = int(self.top + h/2)


	def __eq__(self, other):
		return isinstance(other, Rect) and self.left == other.left and self.right == other.right \
									   and self.top == other.top and self.bottom == other.bottom
	def __repr__(self):
		return ("rect: l=%d, r=%d, t=%d, b=%d, A: %d" % (self.left, self.right, self.top, self.bottom, self.area)	)

	def overlap(self, other):
		if self.right < other.left or other.right < self.left or self.bottom < other.top or other.bottom < self.top: return False
		return True

	def inside(self, other):
		if self.left > other.left and self.right < other.right \
			and self.bottom < other.bottom and self.top > other.top: return True
		return False
	def maxRect(self, other):
		left, top = min(self.left, other.left), min(self.top, other.top)
		right, bottom = max(self.right, other.right), max(self.bottom, other.bottom)
		width, height = right-left, bottom-top
		return Rect(left, top, width, height)

	def dist(self, other):
		return ( (self.cX - other.cX)**2 + (self.cY - other.cY)**2 )**0.5

	def hasPoint(self, x, y):
		if self.left <= x <= self.right and self.top <= y <= self.bottom:
			return True
		return False

	#CITATION: Some of this algorithm came from: https://stackoverflow.com/questions/33984151/combining-rectangle-square-areas-into-bigger-ones-imshow-python
	@staticmethod
	def cluster(rects):
		clusters = [];
		for rect in rects:
		    matched = 0;
		    for cluster in clusters:
		        if ( rect.overlap(cluster) ):
		            matched=1
		            cluster = cluster.maxRect(rect)
		
		    if ( not matched ):
		        clusters.append( rect );
		return clusters