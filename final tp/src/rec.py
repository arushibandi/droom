#CLass file for a recommendation. This is the user-y part of it,
#So it stores tuff like name,image,price and generates a 'score'
#To rank it amongst peer recommendations and ultimately choose the best one
import urllib
import ssl
import numpy as np
import cv2
import poi

class Rec(object):
	def __init__(self, url, img_url, name, price, poi_id, poi_map):
		self.poi_id = poi_id
		self.url=url
		for c in name:
			if not (c.isalpha() or c == " "): name = name.replace(c, "")
		self.name = name.replace(" in ", "").replace("in.", "").replace(" x ", "").strip()
		self.image = self.readFromUrl(img_url)
		self.price = price
		self.score = self.getScore(poi_map)

	def __eq__(self, other):
		if isinstance(other, Rec) and self.url == other.url: return True
		return False

	def __repr__(self):
		return str(self.name) + "  ,  " + str(self.price) + "  ,  " + str(self.poi_id)

	def readFromUrl(self,url):
		context = ssl._create_unverified_context()
		resp = urllib.request.urlopen(url, context=context)
		image = np.asarray(bytearray(resp.read()), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image

	def getRGBImage(self):
		return cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

	def getScore(self, poi_map):
		p = poi_map[self.poi_id]
		return p.matchScore(self)