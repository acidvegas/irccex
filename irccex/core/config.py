#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# config.py

class connection:
	server     = 'irc.server.com'
	port       = 6667
	proxy      = None
	ipv6       = False
	ssl        = False
	ssl_verify = False
	vhost      = None
	channel    = '#exchange'
	key        = None

class cert:
	key      = None
	file     = None
	password = None

class ident:
	nickname = 'IRCCEX'
	username = 'exchange'
	realname = 'git.supernets.org/acidvegas'

class login:
	network  = None
	nickserv = None
	operator = None

class throttle:
	cmd       = 3
	msg       = 0.5
	reconnect = 10
	rejoin    = 3

class settings:
	log      = False
	modes    = None

class limits:
	assets  = 10   # Maximum number of assets held
	cashout = 1500 # Minimum USD required to !cashout
	init    = 1000 # Initial USD for people who !register
	send    = 1200 # Minimum balance required for !send
	trade   = 5    # Minimum USD amount for !trade

class fees:
	cashout = 0.02  # 2%
	send    = 0.01  # 1%
	trade   = 0.005 # 0.5%
