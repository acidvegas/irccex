#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python (https://acid.vegas/irccex)
# cmc.py

import json
import time

import requests

import config

class CoinMarketCap(object):
	def __init__(self):
		self.cache = {'global':dict(), 'ticker':dict()}
		self.last  = {'global':0     , 'ticker':0     }

	def _api(self, _endpoint, _params={}):
		session = requests.Session()
		session.headers.update({'Accept':'application/json', 'Accept-Encoding':'deflate, gzip', 'X-CMC_PRO_API_KEY':config.CMC_API_KEY})
		response = session.get('https://pro-api.coinmarketcap.com/v1/' + _endpoint, params=_params, timeout=15)
		return json.loads(response.text.replace(': null', ': "0"'))['data']

	def _global(self):
		if time.time() - self.last['global'] < 300:
			return self.cache['global']
		else:
			data = self._api('global-metrics/quotes/latest')
			self.cache['global'] = {
				'cryptocurrencies' : data['active_cryptocurrencies'],
				'exchanges'        : data['active_exchanges'],
				'btc_dominance'    : int(data['btc_dominance']),
				'eth_dominance'    : int(data['eth_dominance']),
				'market_cap'       : int(data['quote']['USD']['total_market_cap']),
				'volume'           : int(data['quote']['USD']['total_volume_24h'])
			}
			self.last['global'] = time.time()
			return self.cache['global']

	def _ticker(self):
		if time.time() - self.last['ticker'] < 300:
			return self.cache['ticker']
		else:
			data = self._api('cryptocurrency/listings/latest', {'limit':'5000'})
			self.cache['ticker'] = dict()
			for item in data:
				self.cache['ticker'][item['symbol']] = {
					'name'       : item['name'],
					'symbol'     : item['symbol'],
					'rank'       : item['cmc_rank'],
					'price'      : float(item['quote']['USD']['price']),
					'percent'    : {'1h':float(item['quote']['USD']['percent_change_1h']), '24h':float(item['quote']['USD']['percent_change_24h']), '7d':float(item['quote']['USD']['percent_change_7d'])},
					'volume'     : int(float(item['quote']['USD']['volume_24h'])),
					'market_cap' : int(float(item['quote']['USD']['market_cap']))
				}
			self.last['ticker'] = time.time()
			return self.cache['ticker']