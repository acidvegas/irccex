#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python (https://acid.vegas/irccex)
# functions.py

import calendar
import datetime
import random
import time

import constants

def check_pair(from_symbol, to_symbol):
	if from_symbol == 'USD':
		return True if to_symbol in ('BTC','ETH','LTC') else False
	elif to_symbol == 'USD':
		return True if from_symbol in ('BTC','ETH','LTC') else False
	elif from_symbol == to_symbol:
		return False
	elif from_symbol in ('BTC','ETH') or to_symbol in ('BTC','ETH'):
		return True
	else:
		return False

def clean_float(value):
	if value > 24.99:
		return int(value)
	elif 'e-' in str(value):
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
	value    = clean_value(data['price'])
	perc_1h  = color('{:,.2f}%'.format(data['percent']['1h']), percent_color(data['percent']['1h']))
	perc_24h = color('{:,.2f}%'.format(data['percent']['24h']), percent_color(data['percent']['24h']))
	perc_7d  = color('{:,.2f}%'.format(data['percent']['7d']), percent_color(data['percent']['7d']))
	percent  = sep2.join((perc_1h,perc_24h,perc_7d))
	volume   = '{0} {1}'.format(color('Volume:', constants.white), '${:,}'.format(data['volume']))
	cap      = '{0} {1}'.format(color('Market Cap:', constants.white), '${:,}'.format(data['market_cap']))
	return f'[{rank}] {name} {sep} {value} ({percent}) {sep} {volume} {sep} {cap}'

def coin_matrix(data): # very retarded way of calculating the longest strings per-column
	results = {'symbol':list(),'value':list(),'perc_1h':list(),'perc_24h':list(),'perc_7d':list(),'volume':list(),'cap':list()}
	for item in data:
		results['symbol'].append(item['symbol'])
		results['value'].append(clean_value(item['price']))
		for perc in ('1h','24h','7d'):
			results['perc_' + perc].append('{:,.2f}%'.format(item['percent'][perc]))
		results['volume'].append('${:,}'.format(item['volume']))
		results['cap'].append('${:,}'.format(item['market_cap']))
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
		value    = clean_value(item['price']).rjust(matrix['value'])
		perc_1h  = color('{:,.2f}%'.format(item['percent']['1h']).rjust(matrix['perc_1h']), percent_color(item['percent']['1h']))
		perc_24h = color('{:,.2f}%'.format(item['percent']['24h']).rjust(matrix['perc_24h']), percent_color(item['percent']['24h']))
		perc_7d  = color('{:,.2f}%'.format(item['percent']['7d']).rjust(matrix['perc_7d']), percent_color(item['percent']['7d']))
		volume   = '${:,}'.format(item['volume']).rjust(matrix['volume'])
		cap      = '${:,}'.format(item['market_cap']).rjust(matrix['cap'])
		lines.append(' {0} | {1} | {2} {3} {4} | {5} | {6} '.format(symbol,value,perc_1h,perc_24h,perc_7d,volume,cap))
	return lines

def color(msg, foreground, background=None):
	if background:
		return f'\x03{foreground},{background}{msg}{constants.reset}'
	else:
		return f'\x03{foreground}{msg}{constants.reset}'

def days(date_obj):
	return (date_obj-datetime.date.today()).days

def fee(amount, percent):
	return amount-(amount*percent)

def is_amount(amount, star=True):
	if amount[:1] == '$':
		amount = amount[1:]
	if amount.isdigit():
		return True if int(amount) > 0.0 else False
	else:
		try:
			float(amount)
			return True if float(amount) > 0.0 else False
		except ValueError:
			return True if star and amount == '*' else False

def month_days():
	now = datetime.datetime.now()
	return calendar.monthrange(now.year, now.month)[1]

def percent_color(percent):
	percent = float(percent)
	if percent == 0.0:
		return constants.grey
	elif percent < 0.0:
		return constants.brown if percent > -10.0 else constants.red
	else:
		return constants.green if percent < 10.0 else constants.light_green

def random_int(min, max):
	return random.randint(min, max)

def uptime(start):
	uptime = datetime.datetime(1,1,1) + datetime.timedelta(seconds=time.time() - start)
	return f'{uptime.day-1} Days, {uptime.hour} Hours, {uptime.minute} Minutes, {uptime.second} Seconds'
