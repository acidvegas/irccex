#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# irc.py

import os
import pickle
import socket
import threading
import time

import config
import constants
import debug
import functions

if config.connection.ssl:
	import ssl

from coinmarketcap import CoinMarketCap


def color(msg, foreground, background=None):
	if background:
		return f'\x03{foreground},{background}{msg}{constants.reset}'
	else:
		return f'\x03{foreground}{msg}{constants.reset}'

class IRC(object):
	def __init__(self):
		self.db          = {'bank':dict(),'verify':dict(),'wallet':dict()}
		self.last        = 0
		self.maintenance = False
		self.slow        = False
		self.sock        = None

	def run(self):
		if os.path.isfile('data/db.pkl'):
			with open('data/db.pkl', 'rb') as db_file:
				self.db = pickle.load(db_file)
			debug.alert('Restored database!')
		threading.Thread(target=Loops.backup).start()
		threading.Thread(target=Loops.maintenance).start()
		threading.Thread(target=Loops.verify).start()
		self.connect()

	def cleanup(self, nick):
		for symbol in [symbol for symbol in self.db['wallet'][nick] if not self.db['wallet'][nick][symbol]]:
			del self.db['wallet'][nick][symbol]
		if not self.db['wallet'][nick]:
			del self.db['wallet'][nick]

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((config.connection.server, config.connection.port))
			self.register()
		except socket.error as ex:
			debug.error('Failed to connect to IRC server.', ex)
			Events.disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if config.connection.ipv6 else socket.AF_INET
		self.sock = socket.socket(family, socket.SOCK_STREAM)
		if config.connection.vhost:
			self.sock.bind((config.connection.vhost, 0))
		if config.connection.ssl:
			ctx = ssl.SSLContext()
			if config.cert.file:
				ctx.load_cert_chain(config.cert.file, config.cert.key, config.cert.password)
			if config.connection.ssl_verify:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(2048).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					debug.irc(line)
					if len(line.split()) >= 2:
						Events.handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				debug.error('Unexpected error occured.', ex)
				break
		Events.disconnect()

	def register(self):
		if config.login.network:
			Commands.raw('PASS ' + config.login.network)
		Commands.raw(f'USER {config.ident.username} 0 * :{config.ident.realname}')
		Commands.nick(config.ident.nickname)

class Commands:
	def action(chan, msg):
		Commands.sendmsg(chan, f'\x01ACTION {msg}\x01')

	def error(target, data, reason=None):
		if reason:
			Commands.sendmsg(target, '[{0}] {1} {2}'.format(color('!', constants.red), data, color('({0})'.format(reason), constants.grey)))
		else:
			Commands.sendmsg(target, '[{0}] {1}'.format(color('!', constants.red), data))

	def identify(nick, password):
		Commands.sendmsg('nickserv', f'identify {nick} {password}')

	def join_channel(chan, key=None):
		Commands.sendmsg(chan, 'I am the {0} bot. Type {1} to register an account and {2} for help!'.format(color('IRC Cryptocurrency Exchange', constants.white), color('!register', constants.light_blue), color('@irccex', constants.light_blue)))
		Commands.raw(f'JOIN {chan} {key}') if key else Commands.raw('JOIN ' + chan)

	def mode(target, mode):
		Commands.raw(f'MODE {target} {mode}')

	def nick(nick):
		Commands.raw('NICK ' + nick)

	def notice(target, msg):
		Commands.raw(f'NOTICE {target} :{msg}')

	def oper(user, password):
		Commands.raw(f'OPER {user} {password}')

	def raw(msg):
		Bot.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(target, msg):
		Commands.raw(f'PRIVMSG {target} :{msg}')

class Events:
	def connect():
		if config.settings.modes:
			Commands.mode(config.ident.nickname, '+' + config.settings.modes)
		if config.login.nickserv:
			Commands.identify(config.ident.nickname, config.login.nickserv)
		if config.login.operator:
			Commands.oper(config.ident.username, config.login.operator)
		Commands.join_channel(config.connection.channel, config.connection.key)

	def disconnect():
		Bot.sock.close()
		time.sleep(config.throttle.reconnect)
		Bot.connect()

	def invite(chan):
		if chan == config.connection.channel:
			Commands.join_channel(config.connection.channel, config.connection.key)

	def kick(chan, kicked):
		if kicked == config.ident.nickname and chan == config.connection.channel:
			time.sleep(config.throttle.rejoin)
			Commands.join_channel(chan, config.connection.key)

	def message(nick, chan, msg):
		try:
			if msg[:1] in '!@$':
				if time.time() - Bot.last < config.throttle.cmd:
					if not Bot.slow:
						Commands.sendmsg(chan, color('Slow down nerd!', constants.red))
						Bot.slow = True
				else:
					Bot.slow = False
					args = msg.split()
					cmd  = args[0][1:]
					if len(args) == 1:
						if msg == '@irccex':
							Commands.sendmsg(chan, constants.bold + 'IRC Cryptocurrency Exchange Bot (IRCCEX) - Developed by acidvegas in Python - https://git.supernets.org/acidvegas/irccex')
						elif msg.startswith('$'):
							msg = msg.upper()
							if ',' in msg:
								coin_list  = list(msg[1:].split(','))[:10]
								data_lines = list()
								for coin in coin_list:
									if coin in CMC.get():
										data_lines.append(CMC.get()[coin])
								if data_lines:
									if len(data_lines) == 1:
										coin = data_lines[0]
										Commands.sendmsg(chan, functions.coin_info(coin))
									else:
										Commands.sendmsg(chan, color('  Symbol       Value           1H          24H           7D         24H Volume        Market Cap    ', constants.black, constants.light_grey))
										for line in data_lines:
											Commands.sendmsg(chan, functions.coin_info(line, True))
											time.sleep(config.throttle.msg)
								else:
									Commands.error(chan, 'Invalid cryptocurrency names!')
							else:
								coin = msg[1:]
								if not coin.isdigit():
									if coin in CMC.get():
										Commands.sendmsg(chan, functions.coin_info(CMC.get()[coin]))
									else:
										Commands.error(chan, 'Invalid cryptocurrency name!')
						elif cmd == 'bank':
							if nick in Bot.db['bank']:
								Commands.sendmsg(chan, color('${:,}'.format(int(Bot.db['bank'][nick])), constants.green))
							else:
								Commands.error(chan, 'You don\'t have any money in the bank!', 'use !cashout to put money in the bank')
						elif cmd == 'cashout':
							if not Bot.maintenance:
								if nick in Bot.db['wallet']:
									if 'USD' in Bot.db['wallet'][nick]:
										if Bot.db['wallet'][nick]['USD'] >= config.limits.cashout:
											profit = Bot.db['wallet'][nick]['USD']-config.limits.init
											amount = functions.fee(profit, config.fees.cashout)
											if nick not in Bot.db['bank']:
												Bot.db['bank'][nick] = amount
											else:
												Bot.db['bank'][nick] += amount
											Bot.db['wallet'][nick]['USD'] = config.limits.init
											Commands.sendmsg(chan, 'Cashed out {0} to your bank account! {1}'.format(color('${:,}'.format(int(amount)), constants.green), color('(current balance: ${:,})'.format(int(Bot.db['bank'][nick])), constants.grey)))
										else:
											Commands.error(chan, 'Insufficent funds.', '${:,} minimum'.format(config.limits.cashout))
									else:
										Commands.error(chan, 'Insufficent funds.', 'you have no USD in your account')
								elif nick in Bot.db['verify']:
									Commands.error(chan, 'Your account is not verified!', 'try again later')
								else:
									Commands.error(chan, 'You don\'t have an account!', 'use !register to make an account')
							else:
								Commands.error(chan, 'Exchange is down for scheduled maintenance!', 'try again later')
						elif cmd == 'register':
							if not Bot.maintenance:
								if nick not in Bot.db['verify'] and nick not in Bot.db['wallet']:
									Commands.sendmsg(chan, 'Welcome to the IRC Cryptocurrency Exchange! ' + color('(please wait 24 hours while we verify your documents)', constants.grey))
									Bot.db['verify'][nick] = time.time()
								else:
									Commands.error(chan, 'Failed to register an account!', 'you already have an account')
							else:
								Commands.error(chan, 'Exchange is down for scheduled maintenance!', 'try again later')
						elif cmd == 'rich':
							if Bot.db['bank']:
								richest = sorted(Bot.db['bank'], key=Bot.db['bank'].get, reverse=True)[:10]
								for user in richest:
									Commands.sendmsg(chan, '[{0}] {1} {2}'.format(color(richest.index(user)+1, constants.pink), user.ljust(15), color('${:,}'.format(int(Bot.db['bank'][user])), constants.green)))
									time.sleep(config.throttle.msg)
								Commands.sendmsg(chan, '^ this could be u but u playin...')
							else:
								Commands.error(chan, 'Yall broke...')
						elif cmd == 'top':
							data = list(CMC.get().values())[:10]
							Commands.sendmsg(chan, color('  Symbol       Value           1H          24H           7D         24H Volume        Market Cap    ', constants.black, constants.light_grey))
							for item in data:
								Commands.sendmsg(chan, functions.coin_info(item, True))
								time.sleep(config.throttle.msg)
						elif cmd == 'wallet':
							if nick in Bot.db['wallet']:
								total = 0
								Commands.sendmsg(chan, color('  Symbol          Amount                  Value        ', constants.black, constants.light_grey))
								for symbol in Bot.db['wallet'][nick]:
									amount = Bot.db['wallet'][nick][symbol]
									if symbol == 'USD':
										value  = amount
									else:
										value = float(CMC.get()[symbol]['price_usd'])*amount
									Commands.sendmsg(chan, ' {0} | {1} | {2} '.format(symbol.ljust(8), functions.clean_float(amount).rjust(20), functions.clean_value(value).rjust(20)))
									total += float(value)
									time.sleep(config.throttle.msg)
								Commands.sendmsg(chan, color('                            ' + ('Total: ' + functions.clean_value(total)).rjust(27), constants.black, constants.light_grey))
							elif nick in Bot.db['verify']:
								Commands.error(chan, 'Your account is not verified yet!', 'try again later')
							else:
								Commands.error(chan, 'You don\'t have an account!', 'use !register to make an account')
					elif len(args) == 2:
						if cmd == 'bottom':
							option  = args[1]
							options = {'1h':'percent_change_1h','24h':'percent_change_24h','7d':'percent_change_7d','value':'price_usd'}
							try:
								option = options[option.lower()]
							except KeyError:
								Commands.error(chan, 'Invalid option!', 'valid options are 1h, 24h, 7d, & value')
							else:
								data = CMC.get()
								sorted_data = dict()
								for item in data:
									sorted_data[item] = float(data[item][option])
								bottom_data = sorted(sorted_data, key=sorted_data.get, reverse=True)[-10:]
								Commands.sendmsg(chan, color('  Symbol       Value           1H          24H           7D         24H Volume        Market Cap    ', constants.black, constants.light_grey))
								for coin in bottom_data:
									Commands.sendmsg(chan, functions.coin_info(CMC.get()[coin], True))
									time.sleep(config.throttle.msg)
						elif cmd == 'top':
							option  = args[1]
							options = {'1h':'percent_change_1h','24h':'percent_change_24h','7d':'percent_change_7d','value':'price_usd','volume':'24h_volume_usd'}
							try:
								option = options[option.lower()]
							except KeyError:
								Commands.error(chan, 'Invalid option!', 'valid options are 1h, 24h, 7d, value & volume')
							else:
								data = CMC.get()
								sorted_data = dict()
								for item in data:
									sorted_data[item] = float(data[item][option])
								top_data = sorted(sorted_data, key=sorted_data.get, reverse=True)[:10]
								Commands.sendmsg(chan, color('  Symbol       Value           1H          24H           7D         24H Volume        Market Cap    ', constants.black, constants.light_grey))
								for coin in top_data:
									Commands.sendmsg(chan, functions.coin_info(CMC.get()[coin], True))
									time.sleep(config.throttle.msg)
					elif len(args) == 3:
						if cmd == 'trade':
							if not Bot.maintenance:
								if nick in Bot.db['wallet']:
									pair = args[1].upper()
									if len(pair.split('/')) == 2:
										from_symbol, to_symbol = pair.split('/')
										if from_symbol != to_symbol:
											if from_symbol in Bot.db['wallet'][nick]:
												amount = args[2]
												if functions.is_amount(amount):
													if amount.startswith('$'):
														if from_symbol != 'USD':
															usd_value = float(amount[1:])
															value     = float(CMC.get()[from_symbol]['price_usd'])
															amount    = float(amount[1:])/value
														else:
															amount    = float(amount[1:])
															usd_value = amount
													else:
														if amount == '*':
															amount = Bot.db['wallet'][nick][from_symbol]
														else:
															amount = float(amount)
														if from_symbol != 'USD':
															value     = float(CMC.get()[from_symbol]['price_usd'])
															usd_value = amount*value
														else:
															usd_value = amount
													if Bot.db['wallet'][nick][from_symbol] >= amount:
														if usd_value >= config.limits.trade:
															fee_amount = functions.fee(amount, config.fees.trade)
															if from_symbol == 'USD':
																if to_symbol in ('BTC','ETH','LTC'):
																	value = float(CMC.get()[to_symbol]['price_usd'])
																	recv_amount = fee_amount/value
																	if to_symbol in Bot.db['wallet'][nick]:
																		Bot.db['wallet'][nick][from_symbol] -= amount
																		Bot.db['wallet'][nick][to_symbol] += recv_amount
																		Bot.cleanup(nick)
																		Commands.sendmsg(chan, 'Trade successful!')
																	else:
																		if len(Bot.db['wallet'][nick]) < config.limits.assets:
																			Bot.db['wallet'][nick]['USD'] -= amount
																			Bot.db['wallet'][nick][to_symbol] = recv_amount
																			Bot.cleanup(nick)
																			Commands.sendmsg(chan, 'Trade successful!')
																		else:
																			Commands.error(chan, f'You can\'t hold more than {config.limits.assets} assets!')
																else:
																	Commands.error(chan, 'Invalid trade pair!', 'can only trade USD for BTC, ETH, & LTC')
															elif to_symbol == 'USD':
																if from_symbol in ('BTC','ETH','LTC'):
																	value = float(CMC.get()[from_symbol]['price_usd'])
																	recv_amount = fee_amount*value
																	if to_symbol in Bot.db['wallet'][nick]:
																		Bot.db['wallet'][nick][from_symbol] -= amount
																		Bot.db['wallet'][nick][to_symbol] += recv_amount
																		Bot.cleanup(nick)
																		Commands.sendmsg(chan, 'Trade successful!')
																	else:
																		if len(Bot.db['wallet'][nick]) < config.limits.assets:
																			Bot.db['wallet'][nick][from_symbol] -= amount
																			Bot.db['wallet'][nick][to_symbol] = recv_amount
																			Bot.cleanup(nick)
																			Commands.sendmsg(chan, 'Trade successful!')
																		else:
																			Commands.error(chan, f'You can\'t hold more than {config.limits.assets} assets!')
																else:
																	Commands.error(chan, 'Invalid trade pair!', 'only BTC, ETH, & LTC can be traded for USD.')
															elif from_symbol in ('BTC','ETH') or to_symbol in ('BTC','ETH'):
																from_value  = float(CMC.get()[from_symbol]['price_usd'])
																to_value    = float(CMC.get()[to_symbol]['price_usd'])
																recv_amount = (fee_amount*from_value)/to_value
																if to_symbol in Bot.db['wallet'][nick]:
																	Bot.db['wallet'][nick][from_symbol] -= amount
																	Bot.db['wallet'][nick][to_symbol] += recv_amount
																	Bot.cleanup(nick)
																	Commands.sendmsg(chan, 'Trade successful!')
																else:
																	if len(Bot.db['wallet'][nick]) < config.limits.assets:
																		Bot.db['wallet'][nick][from_symbol] -= amount
																		Bot.db['wallet'][nick][to_symbol] = recv_amount
																		Bot.cleanup(nick)
																		Commands.sendmsg(chan, 'Trade successful!')
																	else:
																		Commands.error(chan, f'You can\'t hold more than {config.limits.assets} assets!')
															else:
																Commands.error(chan, 'Invalid trade pair!')
														else:
															Commands.error(chan, 'Invalid amount.', f'${config.limits.trade} minimum')
													else:
														Commands.error(chan, 'Insufficient funds.')
												else:
													Commands.error(chan, 'Invalid amount argument.')
											else:
												Commands.error(chan, 'Insufficient funds.')
										else:
											Commands.error(chan, '...Really?')
									else:
										Commands.error(chan, 'Invalid trade pair.')
								elif nick in Bot.db['verify']:
									Commands.error(chan, 'Your account is not verified yet!', 'try again later')
								else:
									Commands.error(chan, 'You don\'t have an account!')
							else:
								Commands.error(chan, 'Exchange is down for scheduled maintenance.', 'try again later.')
						elif cmd == 'value':
							amount = args[1]
							if functions.is_amount(amount, False):
								symbol = args[2].upper()
								if symbol in CMC.get():
									value = float(CMC.get()[symbol]['price_usd'])*float(amount)
									if value < 0.01:
										Commands.sendmsg(chan, '{0} is worth {1}'.format(color(f'{amount} {symbol}', constants.white), color('${0:,.8f}'.format(value), constants.light_blue)))
									else:
										Commands.sendmsg(chan, '{0} is worth {1}'.format(color(f'{amount} {symbol}', constants.white), color('${0:,.2f}'.format(value), constants.light_blue)))
								else:
									Commands.error(chan, 'Invalid cryptocurrency name!')
							else:
								Commands.error(chan, 'Invalid amount!')
					elif len(args) == 4:
						if cmd == 'send':
							if not Bot.maintenance:
								if nick in Bot.db['wallet']:
									total = 0
									for symbol in Bot.db['wallet'][nick]:
										amount = Bot.db['wallet'][nick][symbol]
										if symbol == 'USD':
											value = float(amount)
										else:
											value = float(CMC.get()[symbol]['price_usd'])*amount
										total += value
									if total >= config.limits.send:
										receiver = args[1].lower()
										if receiver in Bot.db['wallet']:
											if nick != receiver:
												amount = args[2].replace(',','')
												symbol = args[3].upper()
												if symbol in Bot.db['wallet'][nick]:
													if functions.is_amount(amount):
														if amount.startswith('$'):
															if symbol == 'USD':
																amount     = float(amount[1:])
																value      = amount
																usd_amount = amount
															else:
																value      = float(CMC.get()[symbol]['price_usd'])
																amount     = float(amount[1:])/value
																usd_amount = value*amount
														else:
															if amount == '*':
																amount = Bot.db['wallet'][nick][symbol]
															else:
																amount = float(amount)
															if symbol != 'USD':
																value      = float(CMC.get()[symbol]['price_usd'])
																usd_amount = amount/value
															else:
																usd_amount = amount
														if Bot.db['wallet'][nick][symbol] >= amount:
															if usd_amount >= config.limits.trade and usd_amount > 0.0:
																fee_amount = functions.fee(amount, config.fees.send)
																if symbol in Bot.db['wallet'][receiver]:
																	Bot.db['wallet'][receiver][symbol] += fee_amount
																	Bot.db['wallet'][nick][symbol] -= amount
																	Bot.cleanup(nick)
																	Commands.sendmsg(receiver, '{0} just sent you {1} {2}! {3}'.format(color(nick, constants.light_blue), fee_amount, symbol, color('(${0})'.format(functions.clean_value(usd_amount)), constants.grey)))
																	Commands.sendmsg(chan, 'Sent!')
																else:
																	if len(Bot.db['wallet'][nick]) < config.limits.assets:
																		Bot.db['wallet'][receiver][symbol] = fee_amount
																		Bot.db['wallet'][nick][symbol] -= amount
																		Bot.cleanup(nick)
																		Commands.sendmsg(receiver, '{0} just sent you {1} {2}! {3}'.format(color(nick, constants.light_blue), fee_amount, symbol, color('(${0})'.format(functions.clean_value(usd_amount)), constants.grey)))
																		Commands.sendmsg(chan, 'Sent!')
																	else:
																		Commands.error(chan, f'User can\'t hold more than {config.limits.assets} assets!')
															else:
																Commands.error(chan, 'Invalid send amount.', f'${config.limittrade} minimum')
														else:
															Commands.error(chan, 'Insufficient funds.')
													else:
														Commands.error(chan, 'Invalid send amount.')
												else:
													Commands.error(chan, 'Insufficient funds.')
											else:
												Commands.error(chan, '...Really?')
										elif receiver in Bot.db['verify']:
											Commands.error(chan, 'User is not verified yet!')
										else:
											Commands.error(chan, 'User is not in the database.')
									else:
										Commands.error(chan, 'Insufficent funds!', f'${config.limits.send} minium')
								elif nick in Bot.db['verify']:
									Commands.error(chan, 'Your account is not verified yet!', 'try again later')
								else:
									Commands.error(chan, 'You don\'t have an account!')
							else:
								Commands.error(chan, 'Exchange is down for scheduled maintenance. Please try again later.')
					Bot.last = time.time()
		except Exception as ex:
			Commands.error(chan, 'Command threw an exception.', ex)

	def nick_in_use():
		debug.error('The bot is already running or nick is in use.')

	def handle(data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			Commands.raw('PONG ' + args[1][1:])
		elif args[1] == constants.RPL_WELCOME:
			Events.connect()
		elif args[1] == constants.ERR_NICKNAMEINUSE:
			Events.nick_in_use()
		elif args[1] == constants.INVITE:
			chan = args[3][1:]
			Events.invite(chan)
		elif args[1] == constants.KICK:
			chan   = args[2]
			kicked = args[3]
			Events.kick(chan, kicked)
		elif args[1] == constants.PRIVMSG:
			nick = args[0].split('!')[0][1:].lower()
			chan = args[2]
			msg  = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
			if chan == config.connection.channel:
				Events.message(nick, chan, msg)

class Loops:
	def backup():
		while True:
			time.sleep(21600) # 6H
			with open('data/db.pkl', 'wb') as db_file:
				pickle.dump(Bot.db, db_file, pickle.HIGHEST_PROTOCOL)
			debug.irc('Database backed up!')

	def maintenance():
		while True:
			try:
				time.sleep(functions.random_int(864000, 2592000)) # 10D - 30D
				Bot.maintenance = True
				Commands.action(config.connection.channel, color('Exchange is going down for scheduled maintenance!', constants.red))
				time.sleep(functions.random_int(3600, 86400))   # 1H - 1D
				Bot.maintenance = False
				Commands.action(config.connection.channel, color('Maintenance complete! Exchange is back online!', constants.green))
			except Exception as ex:
				Bot.maintenance = False
				debug.error('Error occured in the maintenance loop!', ex)

	def verify():
		while True:
			try:
				verified = [nick for nick in Bot.db['verify'] if time.time() - Bot.db['verify'][nick] >= 86400] # 1D
				for nick in verified:
					Bot.db['wallet'][nick] = {'USD':config.limits.init}
					del Bot.db['verify'][nick]
					Commands.sendmsg(nick, 'Your account is now verified! Here is ${:,} to start trading!'.format(config.limits.init))
			except Exception as ex:
				debug.error('Error occured in the verify loop!', ex)
			finally:
				time.sleep(3600) # 1H

Bot = IRC()
CMC = CoinMarketCap()
