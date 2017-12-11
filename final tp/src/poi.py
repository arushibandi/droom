#Class file for POI, or Point Of Interest.
#This stores alot of the information and functions relating to the image and user preferences for
#a point in the image that is of interest due to being where a product will be added

import numpy as np
import cv2
import colors
import room_reader
import urllib
import ssl
import rec
import webscraping_practice
import random
from scipy import stats

class POI(object):

	def __init__(self, x, y, ROI, kws=[], colors=[]):
		self.x = x
		self.y = y
		self.ROI = ROI
		self.kws = []
		self.colors = set()
		self.area = ''
		self.product = ''
		self.prod_type = ''
		self.fur = ''
		self.rec = None
		self.id = None
		self.left = int(self.x - self.ROI.shape[1] / 2)
		self.top = int(self.y - self.ROI.shape[0] / 2)

	def __eq__(self, other):
		if isinstance(other, POI) and self.x == other.x and self.y == other.y and self.id == other.id: return True
		return False

	def setKeywords(self, up_style):
		style = ''
		if up_style != None: style = up_style
		if self.product == 'furniture':
			if self.fur != '': 
				self.kws = [ (style.strip() + " " + col.strip() + " " + \
							self.prod_type.strip() + " " + self.fur.strip()).strip() for col in list(self.colors)]
			else:
				self.kws = [ (style.strip() + " " + col.strip() + " " + \
							self.prod_type.strip() + " " + self.product.strip()).strip() for col in list(self.colors)]
		else:
			self.kws = [ (style.strip() + " " + col.strip() + " " + self.prod_type.strip() + \
							" " + self.area.strip() + " " + self.product.strip()).strip() for col in list(self.colors)]
		print(self.kws)

	def setId(self, id):
		self.id = id

	def inPOI(self, x, y):
		if self.left <= x <= self.left + self.ROI.shape[1] and self.top <= y <= self.top + self.ROI.shape[0]: return True
		return False

	def setArea(self, h):
		if h*(2/3) <= self.y and self.y < h:
			self.area = 'floor'
		elif h * (1/5) <= self.y and self.y < h * (2/3):
			self.area = 'wall'
		else:
			self.area = 'ceiling'

	def setColors(self):
		self.getROIColors()

	def getROIColors(self):

		def camelToUnderscore(word):
			new = ""
			for l in word:
				if l.isupper(): new += " %s" % l.lower()
				else: new += l
			return new

		arr = np.float32(self.ROI)
		pixels = arr.reshape((-1, 3))

		n_colors = 3
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
		flags = cv2.KMEANS_RANDOM_CENTERS
		_, labels, centroids = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)

		palette = np.uint8(centroids)
		quantized = palette[labels.flatten()]
		quantized = quantized.reshape(self.ROI.shape)
		dominant_color = palette[np.argmax(stats.itemfreq(labels)[:, -1])]
		r, g, b = dominant_color[2], dominant_color[1], dominant_color[0]
		dom_col = camelToUnderscore(colors.ColorNames.findNearestColorName(r, g, b, colors.ColorNames.WebColorMap))
		cr, cg, cb = colors.ColorNames.complement(r, g, b)
		com_col = camelToUnderscore(colors.ColorNames.findNearestColorName(cr, cg, cb, colors.ColorNames.WebColorMap))
		self.colors.add(dom_col)
		self.colors.add(com_col)

	def setProductType(self, bigA):
		w, h, chs = self.ROI.shape
		if w*h > 0.2*bigA:
			self.product = "furniture" if self.area != "floor" else "rug"
		else: self.product = "decor"

	def placeResult(self, image, displayRatio):
		rec = self.rec
		placed = image.copy()
		w, h, chs = rec.image.shape
		roi_w, roi_h = int(self.ROI.shape[1] * displayRatio), int(self.ROI.shape[0] * displayRatio)
		new_w, new_h = self.fitToROI(w, h, roi_w, roi_h)
		rec_img = cv2.copyMakeBorder(rec.image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(25,65,95))
		rec_img = cv2.resize(rec_img, (new_w, new_h))
		top = int(self.y * displayRatio - new_h/ 2)
		left = int(self.x * displayRatio - new_w/ 2)
		print(new_w, new_h)
		print(rec_img.shape == (new_h, new_w, 3))
		placed[top:top + new_h, left:left+new_w] = rec_img
		return placed

	def getRecommendations(self, p_id, w, h, style):
		if self.area == '': self.setArea(h)
		self.setColors()
		if self.product == '': self.setProductType(w*h)
		self.setKeywords(style)
		i = random.randint(0, len(self.kws) - 1)
		results = webscraping_practice.getAllResults(self.kws[i])
		results = sorted(results, key = lambda r: float(r[3]))
		return results

	def matchScore(self, rec):
		dist = 0
		rec_kws = set(r.lower() for r in rec.name.split(" "))
		poi_kws = set(w.strip() for w in self.kws[0].split(" "))
		if '' in rec_kws: rec_kws.remove('')
		if '' in poi_kws: poi_kws.remove('')		
		dist = poi_kws.intersection(rec_kws)
		return len(poi_kws) - len(dist)

	def getBestRec(self, results, curr_recs, poi_map, budget):
		recs = []
		for res in results:
			try: 
				if res[2] == "": 
					continue
				else: recs.append( rec.Rec(res[0], res[1], res[2], res[3], self.id, poi_map) )
			except: 
				continue
		recs = [rec for rec in recs if rec not in curr_recs]
		curr_total = sum(r.price for r in curr_recs)
		if budget != None: recs = [r for r in recs if r.price <= (budget - curr_total)]
		recs = sorted(recs, key=lambda r: r.score + (r.price/100) )
		if len(recs) > 0: print("add res", recs[0])
		new_rec = recs[0]
		return new_rec

	def fitToROI(self, w, h, roi_w, roi_h):
		ratio = min( roi_w/w, roi_h/h)
		return int(w * ratio), int(h * ratio)

	def readFromUrl(self,url):
		context = ssl._create_unverified_context()
		resp = urllib.request.urlopen(url, context=context)
		image = np.asarray(bytearray(resp.read()), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image
