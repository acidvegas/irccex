#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python (https://acid.vegas/irccex)
# config.py

class connection:
	server     = 'irc.server.com'
	port       = 6667
	ipv6       = False
	ssl        = False
	ssl_verify = False
	vhost      = None
	channel    = '#exchange'
	key        = None
	modes      = None

class cert:
	key      = None
	password = None

class ident:
	nickname = 'IRCCEX'
	username = 'exchange'
	realname = 'acid.vegas/irccex'

class login:
	network  = None
	nickserv = None
	operator = None

class throttle:
	cmd       = 3
	msg       = 0.5
	reconnect = 10
	rejoin    = 3

class limits:
	assets  = 10   # Maximum number of assets held
	cashout = 5000 # Minimum USD required to !cashout
	init    = 1000 # Initial USD for people who !register
	send    = 2500 # Minimum balance required for !send
	trade   = 5    # Minimum USD amount for !trade

class fees:
	cashout = 0.02  # 2%
	send    = 0.01  # 1%
	trade   = 0.001 # 0.1%

CMC_API_KEY = 'CHANGEME' # https://pro.coinmarketcap.com/signup