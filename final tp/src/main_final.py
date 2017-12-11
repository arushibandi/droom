
#This is the main file that controls all the button clicks, image uploads, user interactions, GUI Stuff
#It calls all the other files that are being used, but doesn't do any of the background algorithmic stuff

import tkinter as tk
import numpy as np
from PIL import ImageTk, Image, ImageOps
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import Toplevel
import room_reader
import rec
import user_prefs
import poi

class GUI(object):
	def __init__(self):
		self.root = tk.Tk()
		self.root.configure(background="#686aa8")
		self.UP = user_prefs.UserPrefs()
		self.initImagePanel()
		self.initUserPanel()
		self.initResultsPanel()
		self.RR = None
		print('hi')

	def initImagePanel(self):
		self.iPanel = tk.Label(self.root, bg="#686aa8", text = "Welcome to DROOM! \n Get the best finds from all over the interweb to design your DREAM ROOM! \n " + \
																"Take a picture of your room, then ... \n Click the upload button to get started now!")
		self.iPanel.bind("<Button-1>", lambda event: self.imageClick(event.x, event.y))
		self.iPanel.grid(row=0,column=0)

	def initUserPanel(self):
		self.pref_frame = tk.Frame(self.root, bg="#686aa8")
		self.pref_frame.grid(row=0, column=1)
		self.new_button = tk.Button(self.pref_frame, text="Upload New Room", command=self.newRoom)
		self.new_button.grid(row=1, column=0)
		self.save_button = tk.Button(self.pref_frame, text="Save this Room", command=self.saveRecs)
		self.save_button.grid(row=1, column=1)
		tk.Label(self.pref_frame, bg="#686aa8", text="Enter budget: ").grid(row=2, column=0)
		self.budget_entry = tk.Entry(self.pref_frame)
		self.budget_entry.grid(row=2, column=1)

		tk.Label(self.pref_frame, bg="#686aa8", text="Pick a Style: ").grid(row=3, column=0)
		self.style_var = tk.StringVar()
		self.style_var.set('modern')
		self.style_menu = tk.OptionMenu(self.pref_frame, self.style_var, *self.UP.styles)
		self.style_menu.grid(row=3, column=1)

		self.pref_button = tk.Button(self.pref_frame, text="Update Preferences", command=self.updateUser)
		self.pref_button.grid(row=5, column=0, columnspan=2)
		self.dirPanel = tk.Label(self.pref_frame, bg="#686aa8", text="Click somewhere to add an object! \n Click on an object to customize it! \n " + 
																	 "To save your room with links, click 'Save this Room'! \n Don't forget to keep a budget! \n")
		self.dirPanel.grid(row=10, column=0, columnspan=2)
		self.quit_button = tk.Button(self.pref_frame, text="QUIT", fg="red",command=quit)
		self.quit_button.grid(row=11,column=0, columnspan=2)


	def initResultsPanel(self):
		self.res_frame = tk.Frame(self.root, bg="#686aa8")
		self.res_frame.grid(row=1, column=0)

	def run(self):
		self.root.mainloop()
		print('bye')

	def saveRecs(self):
		if self.RR == None:
			messagebox.showinfo("Invalid Request", "You must upload a room before trying to save one!")
		else:
			with open("room.txt", "w") as f:
				for r in self.RR.recs:
					f.write("\n")
					f.write(str(r.name) + ", " + str(r.price) + "\n" + str(r.url))

	def newRoom(self):
		filename = askopenfilename()
		image = Image.open(filename)
		image = self.fitToDisplay(image, 600, 600)
		image_tk = ImageTk.PhotoImage(image)
		self.drawImageOnLabel(image_tk, self.iPanel, lambda label: label.grid(row=0, column=0))
		messagebox.showinfo("Hello!", "Your room is being processed ... stay tuned!")
		self.initRoomReader(filename)
		if len(self.RR.pois) > 0: self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))

	def initRoomReader(self, fname):
		self.RR = room_reader.RoomReader(fname)
		self.RR.findPOIs()
		if len(self.RR.pois) < 1: 
			messagebox.showinfo("DROOM Speaking", "Hmmm... we're not quite sure what you want. Click somewhere to get started!")
		else:
			self.RR.getRecommendations(self.UP)
			self.image = self.RR.getDisplayImage()
			self.RR.updateRecs()
			self.addResults(self.RR.recs)

	def addResults(self, recs):
		self.removeOldRecs()
		resnum = len(recs)# if len(recs) < 3 else 3
		for n in range(resnum):
			frame = tk.Frame(self.res_frame, bg="#686aa8", bd=10)
			frame.grid(row=0, column=n)
			image_tk = ImageTk.PhotoImage(Image.fromarray(recs[n].getRGBImage()).resize((100, 100), Image.ANTIALIAS))
			t = recs[n].name if len(recs[n].name) <= 20 else str(recs[n].name[:17] + "...")
			text = tk.Label(frame, text=t)
			price = tk.Label(frame, text='${:,.2f}'.format(recs[n].price))
			text.grid(row=0, column=0)
			price.grid(row=1, column=0)
			self.drawImageOnLabel(image_tk, tk.Label(frame), lambda label: label.grid(row=2, column=0))

	def drawImageOnLabel(self, image, label, grid_func):
		label.configure(image = image)
		label.image = image
		grid_func(label)

	def imageClick(self, x, y):
		p = self.RR.poiClicked(x, y)
		if p != None:
			self.getPOIOptions(p, x, y)
		else:
			messagebox.showinfo("DROOM Speaking", "Looks like you want to make your room dreamier ... \n We'll be right back with suggestions!")
			self.RR.drawPoint(x, y)
			self.image = self.RR.getDisplayImage()
			self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))
			self.RR.addPOI(x, y, self.UP.style, self.UP.budget)
			self.image = self.RR.getDisplayImage()
			self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))
			self.RR.updateRecs()
			self.addResults(self.RR.recs)
	
	def getPOIOptions(self, p, x, y):

		area_var = tk.StringVar()
		prod_var = tk.StringVar()
		type_var = tk.StringVar()
		fur_var = tk.StringVar()

		tl = tk.Toplevel()
		tk.Label(tl, bg="#686aa8", text="Choose a room area: ").grid(row=1, column=0)
		area_var.set(p.area)
		area_menu = tk.OptionMenu(tl, area_var, *self.UP.areas)
		area_menu.grid(row=1, column=1)	


		tk.Label(tl, bg="#686aa8", text="Choose a product style: ").grid(row=3, column=0)
		type_var.set('')
		type_menu = tk.OptionMenu(tl, type_var, *self.UP.types)
		type_menu.grid(row=3, column=1)	

		if p.product == 'furniture':
			tk.Label(tl, bg="#686aa8", text="Choose a furniture type: ").grid(row=4, column=0)
			fur_var.set(p.product)
			fur_menu = tk.OptionMenu(tl, fur_var, *self.UP.furnitures)
			fur_menu.grid(row=4, column=1)
		else:	
			tk.Label(tl, bg="#686aa8", text="Choose a product type: ").grid(row=2, column=0)
			prod_var.set('')
			prod_menu = tk.OptionMenu(tl, prod_var, *self.UP.objects)
			prod_menu.grid(row=2, column=1)	


		def removePOI():
			self.RR.removePOI(p.id)
			tl.destroy()
			self.image = self.RR.getDisplayImage()
			self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))
			self.RR.updateRecs()
			self.addResults(self.RR.recs)

		def addPrefs(p = p, a = area_var, prod = prod_var, t = type_var, f = fur_var):
			p.area, p.product, p.prod_type, p.fur = a.get(), prod.get(), t.get(), f.get()
			self.RR.updatePOI(p, self.UP.style, self.UP.budget)
			self.image = self.RR.getDisplayImage()
			self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))
			self.RR.updateRecs()
			self.addResults(self.RR.recs)

		def close(top=tl):
			addPrefs()
			tl.destroy()

		remove_poi_button = tk.Button(tl, text="I don't want this :(", command=removePOI)
		remove_poi_button.grid(row=10, column=0, columnspan=2)

		destroy_button = tk.Button(tl, text="find something new!", fg="red",command=close)
		destroy_button.grid(row=11,column=0, columnspan=2)


	def fitToDisplay(self, image, w, h):
		i_w, i_h = image.size[1], image.size[0]
		ratio = min( w/i_w, h/i_h)
		return image.resize((int(i_h * ratio), int(i_w * ratio)), Image.ANTIALIAS)


	def updateUser(self):
		self.UP.setBudget(self.budget_entry.get())
		self.UP.setStyle(self.style_var.get())
		messagebox.showinfo("Update", "Your preferences have been updated! \n We'll be back with fresh finds in a bit!")
		self.RR.getRecommendations(self.UP)
		self.image = self.RR.getDisplayImage()
		self.drawImageOnLabel(self.image, self.iPanel, lambda label: label.grid(row=0, column=0))
		self.RR.updateRecs()
		self.removeOldRecs()
		self.addResults(self.RR.recs)


	def removeOldRecs(self):
		for w in self.res_frame.winfo_children():
			w.destroy()

	def saveRoom(self):
		pass

def main():
	app = GUI()
	app.run()

main()