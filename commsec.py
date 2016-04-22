import requests, time, datetime
from bs4 import BeautifulSoup

import matplotlib, random

matplotlib.use("Agg")
font = {'family': 'helvetica', 'size': 4}
matplotlib.rc('font', **font)

import matplotlib.backends.backend_agg as agg
import pylab

import pygame
from pygame.locals import *
import sys

# <login>

url_signin = 'https://www2.commsec.com.au/Public/HomePage/Login.aspx'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}

s = requests.Session()
s.headers.update(headers)

r = s.get(url_signin)
soup = BeautifulSoup(r.content, 'html.parser')

VIEWSTATE = soup.find(id = '__VIEWSTATE')['value']
VIEWSTATEGENERATOR = soup.find(id = '__VIEWSTATEGENERATOR')['value']

f = open('commsec_login.txt', 'r')
[username, password] = f.read().split('\n')
f.close()

login_data = {
'__VIEWSTATE': VIEWSTATE,
'__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
'ctl00$cpContent$txtLogin': username,
'ctl00$cpContent$txtPassword': password,
'ctl00$cpContent$btnLogin': 'Login'
}

r = s.post(url_signin, data = login_data)

# </login>

# <pygame setup>

pygame.init()

# play sound to indicate price change (up or down)
downSound = pygame.mixer.Sound('sound/down.wav')
upSound = pygame.mixer.Sound('sound/up.wav')

window = pygame.display.set_mode((1200, 800), DOUBLEBUF)
pygame.display.set_caption('CommSec - nkukarl')
screen = pygame.display.get_surface()

# <stocks>
urlBase = 'https://www2.commsec.com.au/Private/MarketPrices/Popup/QuoteSearch/QuoteSearch.aspx?stockCode='

stockCodes = ['ORG', 'BHP', 'WPL', 'STO']
urls = [urlBase + stockCode for stockCode in stockCodes]
# </stocks>

# figures
locations = [(0, 0), (600, 0), (0, 400), (600, 400)]

figs = [pylab.figure(figsize = [3, 2], dpi = 200) for _ in range(len(stockCodes))]
axs = [fig.gca() for fig in figs]

# number of points to be displayed
N = 60

# prices array
prices = [[] for _ in range(len(stockCodes))]


# save to files
fileHandles = [open('database/'+ stockCode + '.txt', 'w+') for stockCode in stockCodes]

# main loop
while True:

	for i in range(len(urls)):
		
		url = urls[i] # get url for each stock

		# create soup object and extract price
		soup = BeautifulSoup(s.get(url).content, 'html.parser')
		price = float(soup.find('span', {'id': 'ctl00_BodyPlaceHolder_QuoteSearchView1_ucBuySellQuoteHeader_ucBuySellBar_lblLast_field'}).text)
		
		# play sound to indicate price change
		if prices[i]:
			if price < prices[i][-1]:
				downSound.play()
			elif price > prices[i][-1]:
				upSound.play()

		fileHandles[i].write(str(datetime.datetime.now())[:-7] + '\t' + str(price) + '\n')

		# update price array
		prices[i].append(price)
		if len(prices[i]) > N:
			prices[i].pop(0)

		# time array
		times = [j for j in range(len(prices[i]))]

		# plot
		axs[i].cla() # clear original figure
		axs[i].plot(times, prices[i])
		axs[i].axis([-1, N + 1, min(prices[i]) * 0.99, max(prices[i]) * 1.01])

		# layout setting
		axs[i].set_title(stockCodes[i])
		axs[i].set_xlabel('time')
		axs[i].set_ylabel('stock price ($)')
		axs[i].xaxis.set_ticklabels([])

		# render and blit
		canvas = agg.FigureCanvasAgg(figs[i])
		canvas.draw()
		renderer = canvas.get_renderer()
		raw_data = renderer.tostring_rgb()
		size = canvas.get_width_height()
		surf = pygame.image.fromstring(raw_data, size, "RGB")
		screen.blit(surf, locations[i])
	
	# update display
	pygame.display.flip()

	# exit
	for event in pygame.event.get():
		if event.type == QUIT:
			for i in range(len(stockCodes)):
				fileHandles[i].close()
			pygame.quit()
			sys.exit()