import requests, time, datetime
from bs4 import BeautifulSoup

import matplotlib, random

matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg
import pylab

import pygame
from pygame.locals import *
import sys

pygame.init()

downSound = pygame.mixer.Sound('sound/collide.wav')
upSound = pygame.mixer.Sound('sound/point.wav')

window = pygame.display.set_mode((600, 400), DOUBLEBUF)
pygame.display.set_caption('CommSec - nkukarl')
screen = pygame.display.get_surface()

fig = pylab.figure(figsize = [6, 4], dpi = 100)
ax = fig.gca()

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

stockCode = 'ORG'
url = 'https://www2.commsec.com.au/Private/MarketPrices/Popup/QuoteSearch/QuoteSearch.aspx?stockCode=' + stockCode

soup = BeautifulSoup(s.get(url).content, 'html.parser')

N = 60

prices = []

while True:
	
	soup = BeautifulSoup(s.get(url).content, 'html.parser')

	price = float(soup.find('span', {'id': 'ctl00_BodyPlaceHolder_QuoteSearchView1_ucBuySellQuoteHeader_ucBuySellBar_lblLast_field'}).text)
	
	if prices:
		if price < prices[-1]:
			downSound.play()
		elif price > prices[-1]:
			upSound.play()

	prices.append(price)
	if len(prices) > N:
		prices.pop(0)

	times = [i for i in range(len(prices))]

	ax.cla()
	ax.plot(times, prices)
	ax.axis([-1, N + 1, min(prices) * 0.9, max(prices) * 1.1])

	ax.set_title(stockCode)
	ax.set_xlabel('time')
	ax.set_ylabel('stock price ($)')

	ax.xaxis.set_ticklabels([])

	canvas = agg.FigureCanvasAgg(fig)
	canvas.draw()
	renderer = canvas.get_renderer()
	raw_data = renderer.tostring_rgb()

	size = canvas.get_width_height()

	surf = pygame.image.fromstring(raw_data, size, "RGB")
	screen.blit(surf, (0, 0))
	pygame.display.flip()

	
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()