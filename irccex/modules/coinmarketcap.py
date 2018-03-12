#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# coinmarketcap.py

import http.client
import json
import time

class CoinMarketCap(object):
	def __init__(self):
		self.cache = self.api()

	def api(self):
		conn = http.client.HTTPSConnection('api.coinmarketcap.com', timeout=15)
		conn.request('GET', '/v1/ticker/?limit=0')
		response = conn.getresponse().read().replace(b'null', b'"0"')
		data = json.loads(response)
		conn.close()
		return self.cleanup(data)

	def cleanup(self, data):
		results = dict()
		for item in data:
			results[item['symbol']] = item
		return results

	def get(self):
		if time.time() - int(self.cache['BTC']['last_updated']) < 300:
			return self.cache
		else:
			self.cache = self.api()
			return self.cache
