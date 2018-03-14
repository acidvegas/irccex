#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# irccex.py

import os
import sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or '.')
sys.path += ('core','modules')

import debug

debug.setup_logger()
debug.info()
if not debug.check_version(3):
	debug.error_exit('Python 3 is required!')
if debug.check_privileges():
	debug.error_exit('Do not run as admin/root!')
import irc
irc.Bot.run()
