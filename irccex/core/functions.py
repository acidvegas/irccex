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

def coin_info(data, table=False):
	value   = clean_value(data['price_usd'])
	percent = {'1h':data['percent_change_1h'],'24h':data['percent_change_24h'],'7d':data['percent_change_7d']}
	for item in percent:
		percent[item] = color('{0:,.2f}%'.format(float(percent[item])), percent_color(percent[item]))
	if table:
		name   = data['symbol'].ljust(8)
		volume = '${:,}'.format(int(data['24h_volume_usd'].split('.')[0])).rjust(15)
		cap	   = '${:,}'.format(int(data['market_cap_usd'].split('.')[0])).rjust(16)
		return ' {0} | {1} | {2}   {3}   {4} | {5} | {6} '.format(name,value.rjust(11),percent['1h'].rjust(14),percent['24h'].rjust(14),percent['7d'].rjust(14),volume,cap)
	else:
		sep     = color('|', constants.grey)
		sep2    = color('/', constants.grey)
		rank    = color(data['rank'], constants.pink)
		name    = '{0} ({1})'.format(color(data['name'], constants.white), data['symbol'])
		percent = sep2.join(percent.values())
		volume  = '{0} {1}'.format(color('Volume:', constants.white), '${:,}'.format(int(data['24h_volume_usd'].split('.')[0])))
		cap     = '{0} {1}'.format(color('Market Cap:', constants.white), '${:,}'.format(int(data['market_cap_usd'].split('.')[0])))
		return f'[{rank}] {name} {sep} {value} ({percent}) {sep} {volume} {sep} {cap}'

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
