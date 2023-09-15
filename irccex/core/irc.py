#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python (https://acid.vegas/irccex)
# irc.py

'''
if using_too_many_if_statements == True:
	use_more = True
else:
	use_alot_more = True
'''

import datetime
import os
import pickle
import random
import socket
import threading
import time

import config
import constants
import functions
from coinmarketcap import CoinMarketCap

if config.connection.ssl:
	import ssl

def color(msg, foreground, background=None):
	if background:
		return f'{constants.color}{foreground},{background}{msg}{constants.reset}'
	else:
		return f'{constants.color}{foreground}{msg}{constants.reset}'

class IRC(object):
	def __init__(self):
		self.db          = {'bank':dict(),'pool':0.0,'round':1,'score':dict(),'start':datetime.date.today(),'verify':dict(),'wallet':dict()}
		self.last        = 0
		self.last_backup = time.strftime('%I:%M')
		self.maintenance = False
		self.reward      = {'reward':0,'rewards':0,'status':False}
		self.slow        = False
		self.sock        = None
		self.start       = time.time()

	def run(self):
		if os.path.isfile('db.pkl'):
			with open('db.pkl', 'rb') as db_file:
				self.db = pickle.load(db_file)
			print('[+] - Restored database!')
		Loops.start_loops()
		self.connect()

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((config.connection.server, config.connection.port))
			self.register()
		except socket.error as ex:
			print('[!] - Failed to connect to IRC server! (' + str(ex) + ')')
			Events.disconnect()
		else:
			self.listen()

	def create_socket(self):
		self.sock = socket.socket(AF_INET6) if config.connection.ipv6 else socket.socket()
		if config.connection.vhost:
			self.sock.bind((config.connection.vhost, 0))
		if config.connection.ssl:
			ctx = ssl.SSLContext()
			if config.cert.file:
				ctx.load_cert_chain(config.cert.file, password=config.cert.password)
			if config.connection.ssl_verify:
				ctx.check_hostname = True
				ctx.load_default_certs()
				self.sock = ctx.wrap_socket(self.sock, server_hostname=config.connection.server)
			else:
				self.sock = ctx.wrap_socket(self.sock)

	def listen(self):
		buffer = str()
		last   = time.time()
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				buffer += data
				if data:
					last = time.time()
				else:
					if time.time() - last > 120:
						break
				while '\r\n' in buffer:
					line    = buffer.split('\r\n')[0]
					buffer  = buffer.split('\r\n', 1)[1]
					print('[~] - ' + line)
					if len(line.split()) >= 2:
						Events.handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				print('[!] - Unexpected error occured. (' + str(ex) + ')')
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

	def check_nick(nick, chan):
		if nick in Bot.db['wallet']:
			return True
		else:
			if nick in Bot.db['verify']:
				Commands.error(chan, 'Your account is not verified!', 'try again later')
			else:
				Commands.error(chan, 'You don\'t have an account!', 'use !register to make an account')
			return False

	def cleanup(nick):
		for symbol in [symbol for symbol in Bot.db['wallet'][nick] if not Bot.db['wallet'][nick][symbol]]:
			del Bot.db['wallet'][nick][symbol]
		if not Bot.db['wallet'][nick]:
			del Bot.db['wallet'][nick]

	def error(target, data, reason=None):
		if reason:
			Commands.sendmsg(target, '[{0}] {1} {2}'.format(color('!', constants.red), data, color('({0})'.format(reason), constants.grey)))
		else:
			Commands.sendmsg(target, '[{0}] {1}'.format(color('!', constants.red), data))

	def identify(nick, password):
		Commands.sendmsg('NickServ', f'identify {nick} {password}')

	def join_channel(chan, key=None):
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
		time.sleep(config.throttle.msg)

class Events:
	def connect():
		if config.connection.modes:
			Commands.mode(config.ident.nickname, '+' + config.connection.modes)
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
		if chan == config.connection.channel:
			try:
				if msg[:1] in '!@$':
					if time.time() - Bot.last < config.throttle.cmd:
						if not Bot.slow:
							Bot.slow = True
							Commands.sendmsg(chan, color('Slow down nerd!', constants.red))
					else:
						Bot.slow = False
						args = msg.split()
						if Bot.maintenance and args[0] in ('!cashout','!send','!trade'):
							Commands.error(chan, 'Exchange is down for scheduled maintenance!', 'try again later')
						else:
							if args[0] == '!cashout':
								if Commands.check_nick(nick, chan):
									if 'USD' not in Bot.db['wallet'][nick]:
										Commands.error(chan, 'Insufficent funds.', 'you have no USD in your account')
									elif Bot.db['wallet'][nick]['USD'] < config.limits.cashout:
										Commands.error(chan, 'Insufficent funds.', f'${config.limits.cashout:,} minimum')
									else:
										profit = Bot.db['wallet'][nick]['USD']-config.limits.init
										amount = functions.fee(profit, config.fees.cashout)
										cashout_msg = msg[9:][:100] if len(args) > 1 else Bot.db['bank'][nick][1] if nick in Bot.db['bank'] else 'IM RICH BITCH !!!'
										Bot.db['bank'][nick] = (Bot.db['bank'][nick][0]+amount, cashout_msg) if nick in Bot.db['bank'] else (amount, cashout_msg)
										Bot.db['pool'] += profit-amount
										Bot.db['wallet'][nick]['USD'] = config.limits.init
										Commands.sendmsg(chan, 'Cashed out {0} to your bank account! {1}'.format(color('${:,}'.format(int(amount)), constants.green), color('(current balance: ${:,})'.format(int(Bot.db['bank'][nick][0])), constants.grey)))
							elif len(args) == 1:
								if msg == '@irccex':
									Commands.sendmsg(chan, constants.bold + 'IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python - https://github.com/acidvegas/irccex')
								elif msg == '@stats':
									bank_total = 0
									global_data = CMC._global()
									ticker_data = CMC._ticker()
									wallet_total = 0
									for item in Bot.db['bank']:
										bank_total += Bot.db['bank'][item][0]
									for user in Bot.db['wallet']:
										for symbol in Bot.db['wallet'][user]:
											value = Bot.db['wallet'][user][symbol] if symbol == 'USD' else ticker_data[symbol]['price']*Bot.db['wallet'][user][symbol]
											wallet_total += value
									Commands.sendmsg(chan, '[{0}]'.format(color('Bot', constants.cyan)))
									Commands.sendmsg(chan, '  {0} {1}'.format(color('Backup :', constants.white), Bot.last_backup))
									Commands.sendmsg(chan, '  {0} {1}'.format(color('Round  :', constants.white), Bot.db['round']))
									Commands.sendmsg(chan, '  {0} {1}'.format(color('Uptime :', constants.white), functions.uptime(Bot.start)))
									Commands.sendmsg(chan, '[{0}]'.format(color('Market', constants.cyan)))
									Commands.sendmsg(chan, '  {0} {1}%'.format(color('BTC Dominance    :', constants.white), global_data['btc_dominance']))
									Commands.sendmsg(chan, '  {0} {1}%'.format(color('ETH Dominance    :', constants.white), global_data['eth_dominance']))
									Commands.sendmsg(chan, '  {0} {1:,}'.format(color('Cryptocurrencies :', constants.white), global_data['cryptocurrencies']))
									Commands.sendmsg(chan, '  {0} {1:,}'.format(color('Exchanges        :', constants.white), global_data['exchanges']))
									Commands.sendmsg(chan, '  {0} ${1:,}'.format(color('Market Cap       :', constants.white), global_data['market_cap']))
									Commands.sendmsg(chan, '  {0} ${1:,}'.format(color('Volume           :', constants.white), global_data['volume']))
									Commands.sendmsg(chan, '[{0}]'.format(color('Round', constants.cyan)))
									Commands.sendmsg(chan, '  {0} {1} {2}'.format(color('Accounts    :', constants.white), '{:,}'.format(len(Bot.db['wallet'])), color('(${:,})'.format(int(wallet_total)), constants.grey)))
									Commands.sendmsg(chan, '  {0} {1} {2}'.format(color('Bank        :', constants.white), '{:,}'.format(len(Bot.db['bank'])), color('(${:,})'.format(int(bank_total)), constants.grey)))
									Commands.sendmsg(chan, '  {0} ${1:,}'.format(color('Reward Pool :', constants.white), int(Bot.db['pool'])))
									Commands.sendmsg(chan, '  {0} {1:,}'.format(color('Unverified  :', constants.white), len(Bot.db['verify'])))
								elif msg.startswith('$'):
									msg = msg.upper()
									if ',' in msg:
										seen  = set()
										coins = [x for x in list(msg[1:].split(','))[:10] if not (x in seen or seen.add(x))]
										data  = [CMC._ticker()[coin] for coin in coins if coin in CMC._ticker()]
										if data:
											if len(data) == 1:
												Commands.sendmsg(chan, functions.coin_info(data[0]))
											else:
												for line in functions.coin_table(data):
													Commands.sendmsg(chan, line)
										else:
											Commands.error(chan, 'Invalid cryptocurrency names!')
									else:
										coin = msg[1:]
										if not coin.split('.')[0].isdigit():
											if coin in CMC._ticker():
												Commands.sendmsg(chan, functions.coin_info(CMC._ticker()[coin]))
											else:
												Commands.error(chan, 'Invalid cryptocurrency name!')
								elif msg == '!bang' and Bot.reward['status']:
									if Commands.check_nick(nick, chan):
										amount = functions.fee(Bot.reward['reward'], float('0.{0:02}'.format(functions.random_int(5,15)))) if Bot.reward['rewards'] else Bot.db['pool']
										Bot.db['wallet'][nick]['USD'] = Bot.db['wallet'][nick]['USD']+amount if 'USD' in Bot.db['wallet'][nick] else amount
										Bot.db['pool'] -= amount
										if Bot.db['pool']:
											Commands.sendmsg(chan, 'You won {0}!'.format(color('${:,}'.format(amount), constants.green)))
											Bot.reward['rewards'] -= 1
										else:
											Commands.sendmsg(chan, 'You won the big {0}!'.format(color('${:,}'.format(amount), constants.green)))
											Bot.reward = {'reward':0,'rewards':0,'status':False}
								elif msg == '!bank':
									if nick in Bot.db['bank']:
										clean_bank = dict()
										for item in Bot.db['bank']:
											clean_bank[item] = Bot.db['bank'][item][0]
										richest = sorted(clean_bank, key=clean_bank.get, reverse=True)
										Commands.sendmsg(chan, '[{0}] {1} {2} {3}'.format(color('{:02}'.format(richest.index(nick)+1), constants.pink), nick, color('${:,}'.format(int(Bot.db['bank'][nick][0])), constants.green), Bot.db['bank'][nick][1]))
									else:
										Commands.error(chan, 'You don\'t have any money in the bank!', 'use !cashout to put money in the bank')
								elif msg == '!portfolio':
									if Commands.check_nick(nick, chan):
										total = 0
										for symbol in Bot.db['wallet'][nick]:
											value = Bot.db['wallet'][nick][symbol] if symbol == 'USD' else CMC._ticker()[symbol]['price']*Bot.db['wallet'][nick][symbol]
											total += value
										Commands.sendmsg(chan, color('${:,}'.format(int(total)), constants.green))
								elif msg == '!register':
									if nick not in Bot.db['verify'] and nick not in Bot.db['wallet']:
										Bot.db['verify'][nick] = time.time()
										Commands.sendmsg(chan, 'Welcome to the IRC Cryptocurrency Exchange! ' + color('(please wait 24 hours while we verify your documents)', constants.grey))
									else:
										Commands.error(chan, 'Failed to register an account!', 'you already have an account')
								elif msg == '!rich':
									if Bot.db['bank']:
										clean_bank = dict()
										for item in Bot.db['bank']:
											clean_bank[item] = Bot.db['bank'][item][0]
										richest = sorted(clean_bank, key=clean_bank.get, reverse=True)[:10]
										for user in richest:
											_user = f'{user[:1]}{constants.reset}{user[1:]}'
											Commands.sendmsg(chan, '[{0}] {1} {2} {3}'.format(color('{:02}'.format(richest.index(user)+1), constants.pink), _user.ljust(15), color('${:,}'.format(int(Bot.db['bank'][user][0])).ljust(13), constants.green), Bot.db['bank'][user][1]))
										Commands.sendmsg(chan, '^ this could be u but u playin...')
									else:
										Commands.error(chan, 'Yall broke...')
								elif msg == '!score':
									if nick in Bot.db['score']:
										clean_bank = dict()
										for item in Bot.db['score']:
											clean_bank[item] = Bot.db['score'][item][0]
										top = sorted(clean_bank, key=clean_bank.get, reverse=True)
										Commands.sendmsg(chan, '[{0}] {1} {2} {3}'.format(color('{:02}'.format(top.index(nick)+1), constants.pink), nick, color(str(Bot.db['score'][nick][0]), constants.cyan), color('${:,}'.format(int(Bot.db['score'][nick][1])), constants.green)))
									else:
										Commands.error(chan, 'You don\'t have any points!', 'be in the top 10 at the end of the month when the current round ends to get points')
								elif msg == '!scores':
									if Bot.db['score']:
										clean_score = dict()
										for item in Bot.db['score']:
											clean_score[item] = Bot.db['score'][item][0]
										top = sorted(clean_score, key=clean_score.get, reverse=True)[:10]
										for user in top:
											Commands.sendmsg(chan, '[{0}] {1} {2} {3}'.format(color('{:02}'.format(top.index(user)+1), constants.pink), user.ljust(15), color(str(Bot.db['score'][user][0]).ljust(5), constants.cyan), color('${:,}'.format(int(Bot.db['score'][nick][1])), constants.green)))
										Commands.sendmsg(chan, '^ this could be u but u playin...')
									else:
										Commands.error(chan, 'Yall broke...')
								elif msg == '!top':
									data = list(CMC._ticker().values())[:10]
									for line in functions.coin_table(data):
										Commands.sendmsg(chan, line)
								elif msg == '!wallet':
									if Commands.check_nick(nick, chan):
										Commands.sendmsg(chan, color('  Symbol          Amount                  Value                   Change             ', constants.black, constants.light_grey))
										total = 0
										for symbol in Bot.db['wallet'][nick]:
											amount = Bot.db['wallet'][nick][symbol]
											if symbol == 'USD':
												value = amount
											elif symbol in CMC._ticker():
												value = CMC._ticker()[symbol]['price']*amount
											else: # CLEAN THIS UP - TEMP FIX FOR ERRORS ON !wallet reported by sht, ji, and others...
												value = 'JACKED'
											if value == 'JACKED':
												Commands.sendmsg(chan, symbol + ' was JACKED sucka!')
												del Bot.db['wallet'][nick][symbol]
											else:
												try:
													Commands.sendmsg(chan, f' {symbol.ljust(8)} | {str(functions.clean_float(amount)).rjust(20)} | {str(functions.clean_value(value)).rjust(20)} | {str(functions.clean_percent(CMC._ticker()[symbol])).rjust(26)} ')
													total += float(value)
												except:
													Commands.sendmsg(chan, f' {symbol.ljust(8)} | {str(functions.clean_float(amount)).rjust(20)} | {str(functions.clean_value(value)).rjust(20)} | {str("N/A").ljust(26)} ')
													total += float(value)	
										Commands.sendmsg(chan, color(f'                      Total:{str(functions.clean_value(total)).rjust(27)}                              ', constants.black, constants.light_grey))
							elif len(args) == 2:
								if args[0] in ('!bottom','!top'):
									option  = args[1].lower()
									if option not in ('1h','24h','7d','value','volume'):
										Commands.error(chan, 'Invalid option!', 'valid options are 1h, 24h, 7d, value & volume')
									else:
										data = dict()
										for item in CMC._ticker():
											data[item] = float(CMC._ticker()[item]['percent'][option])
										data = sorted(data, key=data.get, reverse=True)
										data = data[-10:] if args[0] == '!bottom' else data[:10]
										data = [CMC._ticker()[coin] for coin in data]
										for line in functions.coin_table(data):
											Commands.sendmsg(chan, line)
							elif len(args) == 3:
								if args[0] == '!trade':
									if Commands.check_nick(nick, chan):
										pair = args[1].upper()
										if len(pair.split('/')) == 2:
											from_symbol, to_symbol = pair.split('/')
											if from_symbol in Bot.db['wallet'][nick]:
												amount = args[2].replace(',','')
												if functions.is_amount(amount):
													if amount == '*':
														amount = Bot.db['wallet'][nick][from_symbol]
													elif amount.startswith('$'):
														amount = float(amount[1:]) if from_symbol == 'USD' else float(amount[1:])/CMC._ticker()[from_symbol]['price']
													else:
														amount = float(amount)
													usd_value = amount if from_symbol == 'USD' else CMC._ticker()[from_symbol]['price']*amount
													if Bot.db['wallet'][nick][from_symbol] >= amount:
														if usd_value >= config.limits.trade:
															recv_amount = functions.fee(amount, config.fees.trade)
															if functions.check_pair(from_symbol, to_symbol):
																from_value  = 1 if from_symbol == 'USD' else CMC._ticker()[from_symbol]['price']
																to_value    = 1 if to_symbol == 'USD' else CMC._ticker()[to_symbol]['price']
																recv_amount = (recv_amount*from_value)/to_value
																if to_symbol in Bot.db['wallet'][nick]:
																	Bot.db['wallet'][nick][from_symbol] -= amount
																	Bot.db['wallet'][nick][to_symbol] += recv_amount
																	Commands.cleanup(nick)
																	Bot.db['pool'] += usd_value-functions.fee(usd_value, config.fees.trade)
																	Commands.sendmsg(chan, 'Trade successful!')
																else:
																	if len(Bot.db['wallet'][nick]) < config.limits.assets:
																		Bot.db['wallet'][nick][from_symbol] -= amount
																		Bot.db['wallet'][nick][to_symbol] = recv_amount
																		Commands.cleanup(nick)
																		Bot.db['pool'] += usd_value-functions.fee(usd_value, config.fees.trade)
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
											Commands.error(chan, 'Invalid trade pair.')
								elif args[0] == '!value':
									amount = args[1]
									if functions.is_amount(amount, False):
										amount = amount.replace(',','')
										symbol = args[2].upper()
										if symbol in CMC._ticker():
											value = CMC._ticker()[symbol]['price']*float(amount)
											if value < 0.01:
												Commands.sendmsg(chan, '{0} is worth {1}'.format(color(f'{amount} {symbol}', constants.white), color('${0:,.8f}'.format(value), constants.light_blue)))
											else:
												Commands.sendmsg(chan, '{0} is worth {1}'.format(color(f'{amount} {symbol}', constants.white), color('${0:,.2f}'.format(value), constants.light_blue)))
										else:
											Commands.error(chan, 'Invalid cryptocurrency name!')
									else:
										Commands.error(chan, 'Invalid amount!')
							elif len(args) == 4:
								if args[0] == '!send':
									if Commands.check_nick(nick, chan):
										total = 0
										for symbol in Bot.db['wallet'][nick]:
											total += Bot.db['wallet'][nick]['USD'] if symbol == 'USD' else CMC._ticker()[symbol]['price']*Bot.db['wallet'][nick][symbol]
										if total >= config.limits.send:
											receiver = args[1].lower()
											if receiver in Bot.db['wallet']:
												if nick != receiver:
													amount = args[2].replace(',','')
													symbol = args[3].upper()
													if symbol in Bot.db['wallet'][nick]:
														if functions.is_amount(amount):
															amount = amount.replace(',','')
															if amount == '*':
																amount = Bot.db['wallet'][nick][symbol]
															elif amount.startswith('$'):
																amount = float(amount[1:]) if symbol == 'USD' else float(amount[1:])/CMC._ticker()[symbol]['price']
															else:
																amount = float(amount)
															usd_value = amount if symbol == 'USD' else CMC._ticker()[symbol]['price']*amount
															if Bot.db['wallet'][nick][symbol] >= amount:
																if usd_value >= config.limits.trade:
																	recv_amount = functions.fee(amount, config.fees.send)
																	if symbol in Bot.db['wallet'][receiver] or len(Bot.db['wallet'][receiver]) < config.limits.assets:
																		Bot.db['wallet'][receiver][symbol] = Bot.db['wallet'][receiver][symbol]+recv_amount if symbol in Bot.db['wallet'][receiver] else recv_amount
																		Bot.db['wallet'][nick][symbol] -= amount
																		Commands.cleanup(nick)
																		Bot.db['pool'] += usd_value-functions.fee(usd_value, config.fees.send)
																		Commands.sendmsg(receiver, '{0} just sent you {1} {2}! {3}'.format(color(nick, constants.light_blue), functions.clean_float(recv_amount), symbol, color('({0})'.format(functions.clean_value(usd_value)), constants.grey)))
																		Commands.sendmsg(chan, 'Sent!')
																	else:
																		Commands.error(chan, f'User can\'t hold more than {config.limits.assets} assets!')
																else:
																	Commands.error(chan, 'Invalid send amount.', f'${config.limits.trade} minimum')
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
					Bot.last = time.time()
			except Exception as ex:
				if time.time() - Bot.last < config.throttle.cmd:
					if not Bot.slow:
						Commands.sendmsg(chan, color('Slow down nerd!', constants.red))
						Bot.slow = True
				else:
					Commands.error(chan, 'Command threw an exception.', ex)
				Bot.last = time.time()

	def nick_in_use():
		config.ident.nickname = 'IRCCEX_' + str(functions.random_int(10,99))
		Commands.nick(config.ident.nickname)

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
		elif args[1] == constants.INVITE and len(args) == 4:
			chan = args[3][1:]
			Events.invite(chan)
		elif args[1] == constants.KICK and len(args) >= 4:
			chan   = args[2]
			kicked = args[3]
			Events.kick(chan, kicked)
		elif args[1] == constants.PRIVMSG and len(args) >= 4:
			chan = args[2]
			nick = args[0].split('!')[0][1:].lower()
			msg  = ' '.join(args[3:])[1:]
			Events.message(nick, chan, msg)

class Loops:
	def start_loops():
		threading.Thread(target=Loops.backup).start()
		threading.Thread(target=Loops.double_fees).start()
		threading.Thread(target=Loops.maintenance).start()
		threading.Thread(target=Loops.remind).start()
		threading.Thread(target=Loops.reward).start()
		threading.Thread(target=Loops.round).start()
		threading.Thread(target=Loops.verify).start()

	def backup():
		while True:
			time.sleep(1800) # 30M
			with open('db.pkl', 'wb') as db_file:
				pickle.dump(Bot.db, db_file, pickle.HIGHEST_PROTOCOL)
			Bot.last_backup = time.strftime('%I:%M')
			print('[+] - Database backed up!')

	def double_fees():
		original_fees = {'cashout':config.fees.cashout,'send':config.fees.send,'trade':config.fees.trade}
		while True:
			try:
				time.sleep(functions.random_int(604800,864000)) # 7D - 10D
				config.fees.cashout = original_fees['cashout']*2
				config.fees.send    = original_fees['send']*2
				config.fees.trade   = original_fees['trade']*2
				Commands.action(config.connection.channel, color('Double fees have been activated!', constants.red))
				time.sleep(functions.random_int(86400, 259200)) # 1D - 3D
				config.fees.cashout = original_fees['cashout']/2
				config.fees.send    = original_fees['send']/2
				config.fees.trade   = original_fees['trade']/2
				Commands.notice(config.connection.channel, color('Double fees have been deactivated!', constants.red))
			except Exception as ex:
				config.fees.cashout = original_fees['cashout']
				config.fees.send    = original_fees['send']
				config.fees.trade   = original_fees['trade']
				print('[!] - Error occured in the double fees loop! (' + str(ex) + ')')

	def maintenance():
		while True:
			try:
				time.sleep(functions.random_int(604800,1209600)) # 7D - 14D
				Bot.maintenance = True
				Commands.action(config.connection.channel, color('Exchange is going down for scheduled maintenance!', constants.red))
				time.sleep(functions.random_int(3600, 86400)) # 1H - 1D
				Bot.maintenance = False
				Commands.notice(config.connection.channel, color('Maintenance complete! Exchange is back online!', constants.green))
			except Exception as ex:
				Bot.maintenance = False
				print('[!] - Error occured in the maintenance loop! (' + str(ex) + ')')

	def remind():
		time.sleep(10)
		while True:
			try:
				days = functions.month_days()
				now = int(time.strftime('%-d'))
				for dayz in (7,14,21):
					if days-now == dayz:
						Commands.notice(config.connection.channel, 'There is only {0} week(s) left until round {1} ends!'.format(color(str(int(dayz/7)), constants.cyan), color(str(Bot.db['round']), constants.cyan)))
						break
			except Exception as ex:
				print('[!] - Error occured in the reminder loop! (' + str(ex) + ')')
			finally:
				time.sleep(86400) # 24H

	def reward():
		while True:
			try:
				time.sleep(functions.random_int(86400, 259200)) # 1D - 3D
				if not Bot.reward['status'] and not Bot.maintenance:
					option = functions.random_int(25,50)
					Bot.reward = {'reward':Bot.db['pool']/(option*2),'rewards':option,'status':True}
					Commands.notice(config.connection.channel, 'There is {1} in the reward pool. Type {2} to grab some cash stacks!'.format(color('${:,}'.format(int(Bot.db['pool'])), constants.green), color('!bang', constants.light_blue)))
			except Exception as ex:
				print('[!] - Error occured in the reward loop! (' + str(ex) + ')')

	def round():
		time.sleep(10)
		while True:
			try:
				if time.strftime('%d') == '01':
					Bot.maintenance = True
					amount = 10 if len(Bot.db['bank']) >= 10 else len(Bot.db['bank'])
					if amount:
						clean_bank = dict()
						for item in Bot.db['bank']:
							clean_bank[item] = Bot.db['bank'][item][0]
						richest = sorted(clean_bank, key=clean_bank.get, reverse=True)[:amount]
						for nick in richest:
							if nick in Bot.db['score']:
								Bot.db['score'][nick] = (Bot.db['score'][nick][0]+(amount-richest.index(nick)), Bot.db['score'][nick][1]+Bot.db['bank'][nick][0])
							else:
								Bot.db['score'][nick] = (amount-richest.index(nick), Bot.db['bank'][nick][0])
						Commands.notice(config.connection.channel, 'Round {0} is now over! Winners: {1}'.format(color(Bot.db['round'], constants.light_blue), color(', '.join(richest), constants.yellow)))
					else:
						Commands.notice(config.connection.channel, 'Round {0} is now over! Winners: {1}'.format(color(Bot.db['round'], constants.light_blue), color('None', constants.grey)))
					Bot.db = {'bank':dict(),'pool':0.0,'round':Bot.db['round']+1,'score':Bot.db['score'],'verify':dict(),'wallet':dict()}
					Commands.action(config.connection.channel, 'Round {0} starts NOW!'.format(color(Bot.db['round'], constants.light_blue)))
					Bot.maintenance = False
			except Exception as ex:
				print('[!] - Error occured in the round loop! (' + str(ex) + ')')
			finally:
				time.sleep(86400) # 24H

	def verify():
		time.sleep(10)
		while True:
			try:
				if Bot.db['verify']:
					for nick in [nick for nick in Bot.db['verify'] if time.time() - Bot.db['verify'][nick] >= 86400]: # 1D
						Bot.db['wallet'][nick] = {'USD':config.limits.init}
						del Bot.db['verify'][nick]
						Commands.sendmsg(nick, f'Your account is now verified! Here is ${config.limits.init:,} to start trading!')
			except Exception as ex:
				print('[!] - Error occured in the verify loop! (' + str(ex) + ')')
			finally:
				time.sleep(3600) # 1H

Bot = IRC()
CMC = CoinMarketCap(config.CMC_API_KEY)