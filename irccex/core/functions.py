#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# functions.py

import random

import constants

def clean_float(value):
	if 'e-' in str(value):
		return '{0:.8f}'.format(float(value))
	else:
		return '{0:.8g}'.format(float(value))

def clean_value(value):
	value = float(value)
	if value < 0.01:
		return '${0:,.8f}'.format(value)
	elif value < 24.99:
		return '${0:,.2f}'.format(value)
	else:
		return '${:,}'.format(int(value))

def coin_info(data):
	sep      = color('|', constants.grey)
	sep2     = color('/', constants.grey)
	rank     = color(data['rank'], constants.pink)
	name     = '{0} ({1})'.format(color(data['name'], constants.white), data['symbol'])
	value    = clean_value(data['price_usd'])
	perc_1h  = color('{:,.2f}%'.format(float(data['percent_change_1h'])), percent_color(data['percent_change_1h']))
	perc_24h = color('{:,.2f}%'.format(float(data['percent_change_24h'])), percent_color(data['percent_change_24h']))
	perc_7d  = color('{:,.2f}%'.format(float(data['percent_change_7d'])), percent_color(data['percent_change_7d']))
	percent  = sep2.join((perc_1h,perc_24h,perc_7d))
	volume   = '{0} {1}'.format(color('Volume:', constants.white), '${:,}'.format(int(data['24h_volume_usd'].split('.')[0])))
	cap      = '{0} {1}'.format(color('Market Cap:', constants.white), '${:,}'.format(int(data['market_cap_usd'].split('.')[0])))
	return f'[{rank}] {name} {sep} {value} ({percent}) {sep} {volume} {sep} {cap}'

def coin_matrix(data): # very retarded way of calculating the longest strings per-column
	results = {'symbol':list(),'value':list(),'perc_1h':list(),'perc_24h':list(),'perc_7d':list(),'volume':list(),'cap':list()}
	for item in data:
		results['symbol'].append(item['symbol'])
		results['value'].append(clean_value(item['price_usd']))
		for perc in ('1h','24h','7d'):
			results['perc_' + perc].append('{:,.2f}%'.format(float(item['percent_change_' + perc])))
		results['volume'].append('${:,}'.format(int(item['24h_volume_usd'].split('.')[0])))
		results['cap'].append('${:,}'.format(int(item['market_cap_usd'].split('.')[0])))
	for item in results:
		results[item] = len(max(results[item], key=len))
	if results['symbol'] < len('Symbol'):
		results['symbol'] = len('Symbol')
	if results['value'] < len('Value'):
		results['value'] = len('Value')
	if results['volume'] < len('Volume'):
		results['volume'] = len('Volume')
	if results['cap'] < len('Market Cap'):
		results['cap'] = len('Market Cap')
	return results

def coin_table(data):
	matrix = coin_matrix(data)
	header = color(' {0}   {1}   {2} {3} {4}   {5}   {6} '.format('Symbol'.center(matrix['symbol']), 'Value'.center(matrix['value']), '1H'.center(matrix['perc_1h']), '24H'.center(matrix['perc_24h']), '7D'.center(matrix['perc_7d']), 'Volume'.center(matrix['volume']), 'Market Cap'.center(matrix['cap'])), constants.black, constants.light_grey)
	lines  = [header,]
	for item in data:
		symbol   = item['symbol'].ljust(matrix['symbol'])
		value    = clean_value(item['price_usd']).rjust(matrix['value'])
		perc_1h  = color('{:,.2f}%'.format(float(item['percent_change_1h'])).rjust(matrix['perc_1h']),   percent_color(item['percent_change_1h']))
		perc_24h = color('{:,.2f}%'.format(float(item['percent_change_24h'])).rjust(matrix['perc_24h']), percent_color(item['percent_change_24h']))
		perc_7d  = color('{:,.2f}%'.format(float(item['percent_change_7d'])).rjust(matrix['perc_7d']),   percent_color(item['percent_change_7d']))
		volume   = '${:,}'.format(int(item['24h_volume_usd'].split('.')[0])).rjust(matrix['volume'])
		cap      = '${:,}'.format(int(item['market_cap_usd'].split('.')[0])).rjust(matrix['cap'])
		lines.append(' {0} | {1} | {2} {3} {4} | {5} | {6} '.format(symbol,value,perc_1h,perc_24h,perc_7d,volume,cap))
	return lines

def color(msg, foreground, background=None):
	if background:
		return f'\x03{foreground},{background}{msg}{constants.reset}'
	else:
		return f'\x03{foreground}{msg}{constants.reset}'

def fee(amount, percent):
	return amount-(amount*percent)

def is_amount(amount, star=True):
	if amount.startswith('$'):
		amount = amount[1:]
	if amount.isdigit():
		if int(amount) > 0.0:
			return True
		else:
			return False
	else:
		try:
			float(amount)
			if float(amount) > 0.0:
				return True
			else:
				return False
		except ValueError:
			if star and amount == '*':
				return True
			else:
				return False

def percent_color(percent):
	percent = float(percent)
	if percent == 0.0:
		return constants.grey
	elif percent < 0.0:
		if percent > -10.0:
			return constants.brown
		else:
			return constants.red
	else:
		if percent < 10.0:
			return constants.green
		else:
			return constants.light_green

def random_int(min, max):
	return random.randint(min, max)
