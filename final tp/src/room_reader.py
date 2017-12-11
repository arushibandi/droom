#This file ties all of the product finding, recommendation scraping, etc stuff together 
#and does all the broad/general image processing, as well as acting as a middle man 
#between some of the GUI and background algorithm stuff

import cv2
import numpy as np
import rect
import poi
import rec
from PIL import ImageTk, Image
import webscraping_practice
import budget_optimization
import rec
from tkinter import messagebox
import user_prefs

class RoomReader(object):

	def __init__(self, fname):
		self.image = cv2.imread(fname)
		self.image = self.fitToDisplay(self.image, 600, 600)[0]
		self.h, self.w, self.chs = self.image.shape
		self.displayW, self.displayH = 600, 600
		self.original = self.fitToDisplay(self.image, self.displayW, self.displayH)[0]
		self.edited, self.displayRatio = self.fitToDisplay(self.image, self.displayW, self.displayH)
		self.pois = []
		self.poi_map = {}
		self.recs = []

	def removePOI(self, poi_id):
		self.poi_map.pop(poi_id)
		for p in range(len(self.pois)):
			if self.pois[p].id == poi_id: 
				self.pois.pop(p)
				break
		self.updateRecs()
		newEdited = self.original.copy()
		for p in self.pois:
			newEdited = p.placeResult(newEdited, self.displayRatio)
		self.edited = newEdited

	def updateRecs(self):
		self.recs = []
		for p in self.pois:
			self.recs.append(p.rec)

	def poiClicked(self, x, y):
		for p in self.pois:
			if p.inPOI(x/self.displayRatio, y/self.displayRatio): return p
		return None

	def updatePOI(self, p, style, budget):
		results = p.getRecommendations(0, self.w, self.h, style)
		u_rec = p.getBestRec(results, self.recs, self.poi_map, budget)
		p.rec = u_rec
		self.edited = p.placeResult(self.edited, self.displayRatio)

	def addPOI(self, x, y, style, budget):
		h, w, chs = self.image.shape
		box_size = int(((self.image.shape[1] + self.image.shape[0])/2) * 0.15)
		left = max(int(x/self.displayRatio - box_size/2), 0)
		top = max(int(y/self.displayRatio - box_size/2), 0)
		right = min(left+box_size, w)
		bottom = min(top+box_size, h)
		new_roi = self.image[top:bottom, left:right]
		new_poi = poi.POI(int(x/self.displayRatio), int(y/self.displayRatio), new_roi)
		new_poi.setId(len(self.recs))
		self.poi_map[len(self.recs)] = new_poi
		results = new_poi.getRecommendations(0, self.w, self.h, style)
		new_poi.rec = new_poi.getBestRec(results, self.recs, self.poi_map, budget)
		self.edited = new_poi.placeResult(self.edited, self.displayRatio)
		self.pois.append(new_poi)
		self.recs.append(new_poi.rec)

	def getDisplayImage(self):
		rgb = cv2.cvtColor(self.edited, cv2.COLOR_BGR2RGB)
		return ImageTk.PhotoImage(Image.fromarray(rgb))

	def fitToDisplay(self, image, w, h):
		i_w, i_h, i_chs = image.shape
		ratio = min( w/i_w, h/i_h)
		return cv2.resize(image, (int(i_h * ratio), int(i_w * ratio))), ratio

	def drawPOIs(self):
		for poi in self.pois:
			cv2.circle(self.edited, (poi.x, poi.y), 3, (0,0,0), -1)

	def drawPoint(self, x, y):
		cv2.circle(self.edited, (x, y), 3, (255, 255,255), -1)

	def getRecommendations(self, up):
		recs = [ [] for i in range(len(self.pois))]
		count = 0
		for p in self.pois:
			p.setId(count)
			self.poi_map[count] = p
			results = p.getRecommendations(count, self.w, self.h, up.style)
			results = sorted(results, key = lambda r: float(r[3]))
			for res in results:
				try: 
					if res[2] == "": 
						continue
					else: recs[count].append( rec.Rec(res[0], res[1], res[2], res[3], count, self.poi_map) )
				except: 
					continue
			count += 1

		results = sorted(budget_optimization.getAllOptions(recs, len(self.pois)-1, up.budget), \
											key=lambda v: sum(r.score + (r.price/100) for r in v) )
		results = [res for res in results if res != []]
		self.recs = results[0]
		for p in self.pois: 
			for r in self.recs: 
				if r.poi_id == p.id: 
					p.rec = r
					self.edited = p.placeResult(self.edited, self.displayRatio)
					break

	def findPOIs(self):
		# CITATION: OpenCV tutorial helped me: https://docs.opencv.org/2.4/doc/tutorials/imgproc/shapedescriptors/find_contours/find_contours.html
		preImg = RoomReader.preProcess(self.image, 4)
		w, h, chs = preImg.shape
		edges = cv2.Canny(preImg, 127, 200)
		cImg, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		contours = sorted(contours, key=lambda x: cv2.arcLength(x,False), reverse=True)
		contours = contours[:20] if len(contours) >= 20 else contours

		clusters = RoomReader.getClusters(contours, w, h, 0.08)
		print(len(clusters))
		for c in clusters:
			roi = self.image[c.top:c.bottom, c.left:c.right]
			print(self.imageIsUniform(roi))
			if len(roi) > 0 and self.imageIsUniform(roi): 
				self.pois.append(poi.POI(c.cX, c.cY, roi))

	def imageIsUniform(self, roi):
		# CITATION: after looking at a bunch of algorithms online/on OpenCV, I found a bunch here on stackoverflow,
		# and mine is based off of that with modified thresholds : https://stackoverflow.com/questions/46444286/measure-of-uniformity-homogeniy-in-an-image-c-opencv
		thresh = 0.1
		image = roi.copy().astype(np.float32)/255
		count = 0
		prev_blur = cv2.GaussianBlur(image, (11, 11), 2)
		blur = cv2.GaussianBlur(prev_blur, (11, 11), 2)
		ssd = np.sum((blur - prev_blur)**2)
		while(ssd > thresh):
			blur = cv2.GaussianBlur(prev_blur, (11, 11), 2)
			ssd = np.sum((blur - prev_blur)**2)
			prev_blur = blur
			count += 1
		return count < 25

	@staticmethod
	def getClusters(contours, i_w, i_h, thresh):
		boxes, clusters = [], []
		for c in contours:
			x, y, w, h = cv2.boundingRect(c)
			if w*h > i_w*i_h*thresh: clusters.append(rect.Rect(x,y,w,h))
			else: boxes.append(rect.Rect(x,y,w,h))

		clusters += rect.Rect.cluster(boxes)
		clusters = [clusters[c] for c in range(len(clusters)) if clusters[c].area > i_w*i_h*thresh]

		distThresh = ((i_w + i_h)/2)*(thresh/2)
		final = []
		for c1 in clusters:
			tooClose = False
			for c2 in clusters:
				if c1 != c2 and c1.dist(c2) < distThresh: 
					r = c1.maxRect(c2)
					tooClose = True
					if r not in final: final.append(r)
					break
			if tooClose == False: final.append(c1)
		return final

	@staticmethod
	def preProcess(img, k):
		# CITATION: Followed process in OpenCV tutorial: https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_ml/py_kmeans/py_kmeans_opencv/py_kmeans_opencv.html
		kernel = np.ones((5,5), np.uint8)
		img= cv2.erode(img, kernel, iterations=1)
		Z = img.reshape((-1,3))
		# convert to np.float32
		Z = np.float32(Z)
		# define criteria, number of clusters(K) and apply kmeans()
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
		ret,label,center=cv2.kmeans(Z,k,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
		# Now convert back into uint8, and make original image
		center = np.uint8(center)
		res = center[label.flatten()]
		res2 = res.reshape((img.shape))
		#cv2.imshow("res2", res2)
		return res2

