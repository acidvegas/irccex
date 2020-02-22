import pickle, coinmarketcap
CMC = coinmarketcap.CoinMarketCap()
DB = pickle.load(open('db.pkl' 'rb'))
wallets = dict()
for nick in DB['wallet']:
	total = 0
	for symbol in DB['wallet'][nick]:
		total += DB['wallet'][nick][symbol] if symbol == 'USD' else CMC.get()[symbol]['price_usd']*DB['wallet'][nick][symbol]
	wallets[nick] = total
data = sorted(wallets, key=wallets.get, reverse=True)
for item in data:
	print('[{0:02}] {1} ${2:,}'.format(data.index(item)+1, item.ljust(9), wallets[item]))
