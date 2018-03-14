#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX)
# Developed by acidvegas in Python
# https://git.supernets.org/acidvegas/irccex
# db.py

# GLOBALS
bull = u'\u2022'
db   = None

def load():
	with open('db.pkl', 'rb') as db_file:
		db = pickle.load(db_file)

def save():
	with open('db.pkl', 'wb') as db_file:
		pickle.dump(Bot.db, db_file, pickle.HIGHEST_PROTOCOL)

db = load()
for item in db:
	print(f' {bull} {item}\t' + str(len(db[item])))
