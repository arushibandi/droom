#This is called webscraping_practice because it used to be my practice file but now is the real thing
#It does webscraping on 6 (7?) websites and returns a list of lists with the product - 
#name, url, image url, price. 

import requests
from bs4 import BeautifulSoup

def getHomeDepot(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'data-rectype': 'product'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img', {'alt':True})
		prices = products[count].find('div', {'class': 'price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = (str(prices.text).strip()).split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","").replace("/","")
				for char in price:
					if char.isalpha(): price = price.replace(char, "")
				try:
					p = float(price[:-2] + "." + price[-2:])
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def getChairish(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'class':'product should-hover'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img')
		prices = products[count].find('span', {'class': 'product-price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = (str(prices.text)).split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def get1stdibs(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'class':'product-container'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img')
		prices = products[count].find('span', {'data-usd':True})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = (str(prices['data-usd'])).split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def getArroHome(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'class':lambda val: val and 'product-data' in val})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a', {'rel':False})
		img = products[count].find('img', {'class':'lazy'})
		prices = products[count].find('span', {'class':'new-price'})
		if prices == None: prices = products[count].find('span', {'class':'price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = str(prices.text).strip().split("\n")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				for char in price: 
					if char.isalpha(): price = price.replace(char, "")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def getWorldMarket(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'class':'ml-grid-view-item'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img')
		prices = products[count].find('span', {'class': 'ml-item-price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = str(prices.text).strip().split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def getOneKingsLane(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('div', {'class':'ml-grid-view-item'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img')
		prices = products[count].find('span', {'class': 'ml-item-price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = str(prices.text).strip().split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

def getUncommonGoods(base_url, parser):
	results = []
	count = 0
	products = parser.find_all('article', {'class':'product'})
	while len(results) < 5 and count < len(products):
		a = products[count].find('a')
		img = products[count].find('img')
		prices = products[count].find('p', {'class': 'body-small price'})
		if a != None and img != None and prices != None:
			link = a['href'] if a['href'].startswith('http') else base_url + a['href']
			src = img['src'] if img['src'].startswith('http') else base_url + img['src']
			name = img['alt']
			prices = str(prices.text).strip().split(" ")
			ps = []
			for price in prices:
				price = price.replace("$", "").replace(",","")
				try:
					p = float(price)
					ps.append(p)
				except: continue
			if len(ps) == 0: break
			finprice = min(ps)
			results.append( [link, src, name, finprice] )
		count += 1
	return results

url_dict = {'uncommongoods':getUncommonGoods,
			'onekingslane':getOneKingsLane,
			'worldmarket':getWorldMarket,
			'arrohome':getArroHome,
			'1stdibs':get1stdibs,
			'chairish':getChairish,
			'homedepot':getHomeDepot
			}

base_urls = ["https://www.uncommongoods.com", 'https://www.onekingslane.com', 'https://www.worldmarket.com', 'https://www.arrohome.com', 'https://www.1stdibs.com', \
			 'https://www.chairish.com', 'https://www.homedepot.com']
search_urls = ["https://www.uncommongoods.com/search.html/find/?q=", 'https://www.onekingslane.com/search.do?query=', "https://www.worldmarket.com/search.do?query=", \
			   "https://www.arrohome.com/us/catalogsearch/result/?q=", 'https://www.1stdibs.com/search/?q=', 'https://www.chairish.com/search?q=', 'https://www.homedepot.com/s/']
num_urls = 7

def getAllResults(keyword):
	results = []
	for n in range(num_urls):
		search_url = search_urls[n] + keyword.replace(" ", "+")
		print(search_url)
		results += getTopResults(base_urls[n], search_url, getWebName(base_urls[n]))
		print(len(results))
	return results

def getWebName(url):
	split_url = url.split(".")
	return split_url[1]

def getTopResults(base_url, search_url, kw):
	website = requests.get(search_url)
	source = website.text
	parser = BeautifulSoup(source,'html.parser')
	results = url_dict[kw](base_url, parser)
	return results









