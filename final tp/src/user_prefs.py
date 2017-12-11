#Class file to store user preferences

from tkinter import messagebox

class UserPrefs(object):

	styles = {'modern', 'contemporary', 'minimalist', 'industrial', 'mid-century modern', 'scandinavian', 'traditional', \
			  'transitional', 'country', 'bohemian', 'rustic', 'shabby chic', 'hollywood glam'}
	areas = {'wall', 'floor', 'corner', 'ceiling', 'window'}
	types = {'quotation', 'art', 'portrait', 'plant', 'wood', 'b&w', 'colorful', 'neon', 'floral', 'printed', 'eco-friendly'}
	objects = {'frame', 'lighting', 'mirror', 'decor', 'furniture', 'clock', 'vase', 'accent', 'rug', 'curtain'}
	furnitures = {'bed', 'sofa', 'couch', 'chair', 'table', 'bench', 'shelf'}

	def __init__(self):
		self.budget = None
		self.style = None
		self.keyWords = set()
		self.webs = set()

	def setStyle(self, style):
		self.style = str(style)

	def addKeyword(self, word):
		self.keyWords.add(word)

	def setBudget(self, budget):
		try:
			self.budget = float(budget)
		except:
			messagebox.showinfo("Please enter a valid number.")

	def addWebpage(self, url):
		self.webs.add(url)
