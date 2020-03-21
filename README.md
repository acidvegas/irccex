# irccex
A fantasy cryptocurrency exchange for the Internet Relay Chat (IRC) protocol.

*"You can pretend trade currencies, instead of trade pretend currencies!"* ~ some guy on reddit

*"this bot is begging to be used for not playing"* ~ yuritrue

*"its a game, trade hard & get rich or die tryin`"* ~ contra

###### Requirments
* [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*

###### Information
This bot lets users of an IRC channel "pretend" trade cryptocurrencies in a competitive round-based game manner. Real time market data from [CoinMarketCap](https://coinmarketcap.com/) is used to obtain the values and other information of the cryptocurrencies traded.

Users can make an exchange account with the `!register` command, and after 24 hours, are given `init_funds` to start trading with. There is no authentication required for interacting with exchange accounts. Everything is regulated based on the nick of whoever issues a command. Users can `/nick` to any nick with an account to access it. This means it is possible to steal cryptocurrency using the `!send` command.

Bank accounts can be added to with the `!cashout` command, which deposits all of your USD profits from your wallet. Once money is in the bank, it can not be withdrawn. Maintaining your nick and doing frequent cashouts to your bank is the only way to protect your money. The goal is to have the largest bank account by the end of the round.

Every round starts a new "game mode", which affects how the round will end or how the scoring is done for the winner(s). The main goal of the entire game is to collect points from winning game rounds, which can be seen using the `!scores` command.

###### Strategy
There are many ways to become skilled in this game. Making *legit* trades that you would do in the market with real money is the last fucking on that list.

I know what you're thinking... "Can't I just register 500 accounts & have them all !trade and !send money and get RICH?" Yes, you can do that! But just know you are not going to be the first or the last to ever think of that.

This game can introduce lots of trolling & botting. Get creative & figure out ways to make money, secure money, steal money, and more!

###### Loops
* The database will backup to a pickle file every hour. The last backup time can be seen in the `@stats` reply. Make note of this before restarting the bot for some reason.

* The exchange will random enter "maintenance mode" randomly every 7 to 14 days, which locks the use of all exchange commands. Maintenance can last an hour to a full day.

* All fees are collected & stored in the "reward pool". The bot will make an announcement randomly before the round ends & anyone who types `!bang` after that will get a reward taken from the pool. It takes 25 to 50 `!bang`'s to completely empty the pool. The final person to `!bang` will get the largest reward.

* Double fees mode will be activated randomly every 7 to 10 days, which will double the fees for cashout, trade, and send usage, and can last for 1 to 3 days.

###### Trading Pair Rules
- USD can only be used for buying or selling BTC, ETH, & LTC.

- BTC & ETH are the only major trading pairs between all other cryptocurrencies.

###### Fees & Minimums
| Command | Fee | Minimum |
| --- | --- | --- |
| cashout | 2% | $10000 USD Balance |
| send | 1% | $5000 Balance |
| trade | 0.1% | $5 |

###### Exchange Commands
| Command | Description |
| --- | --- |
| @irccex | Information about the bot. |
| @stats | Statistics on the exchange, market, and more. |
| $\<symbol> | Return information for the \<symbol> cryptocurrency. *(\<symbol> can also be a comma seperated list)* |
| !bang | Grab a reward when the reward pool is triggered. |
| !bank | Return your total bank account balance. |
| !bottom \<1h/24h/7d/value/volume> | Return information for the bottom 10 cryptocurrencies based on the \<1h/24h/7d/value>. |
| !cashout [msg] | Deposit all your USD to your bank account and optionally leave the [msg] message for the !rich list. |
| !portfolio | Total USD value of your wallet. |
| !register | Register an exchange account. |
| !rich | Return the top 10 richest bank accounts. |
| !score | Return your score & rank on the leaderboard. |
| !scores | Return the top 10 players on the leaderboard. |
| !send \<nick> \<amount> \<symbol> | Send \<amount> of \<symbol> to \<nick>. |
| !top [\<1h/24h/7d/value/volume>] | Return information for the top 10 cryptocurrencies, optionally based on \<1h/24h/7d/value/volume>. |
| !trade \<pair> \<amount> | Trade \<amount> between \<pair>. |
| !value \<amount> \<name> | Convert \<amount> of the \<name> cryptocurrency to it's value. |
| !wallet | View your exchange wallet. |

- \<amount> can be the symbols amount, USD amount if prefixed with a $, or the total amount you hold if * is used.
	* `!send acidvegas 0.05 BTC` sends 0.05 BTC to acidvegas.
	* `!send chrono $10.00 BTC` sends $10.00 worth of BTC to chrono.
	* `!send mikejonez * BTC` sends all of your BTC to mikejonez.
	* `!send vap0r 1,000,000 USD` commas can also be used in the amount.

- \<pair> is the from_symbol/to_symbol you are wanting to make trades with.
	* `!trade ETH/NANO 0.14` trades 0.14 ETH to NANO.
	* `!trade XRP/BTC $100` trades $100 USD worth of XRP to BTC.
	* `!trade ETH/DOGE *` trades all of your ETH to DOGE.

###### Patreons
Support the project development if you like it: [Patreon.com/irccex](https://patreon.com/irccex)

The IRCCEX project is completely open source & non-profit, though any support/pledges will help in motivation towards more development and adding new features!

###### Future Concepts & Ideas
* Use multiple API keys to prevent rate limiting.
* IRCCEX BlockChain - Keep an on-going ledger of every single transaction ever made in the channel. *(No idea what use it would have. Maybe a `!trades` command for recent history. The idea makes me laugh)*
* Buying options - Spend a large sum of money on features like locking someone from trading for X amount of time (Charge Y per hour and max it to 24 hours), wallet spying, wallet bombing (sending a bunch of shitcoins), hindsight where you get private message alerts on a coins price changing (can be used whenever only once).
* Post reward pool bangs will make you lose money to fuck with people spamming hard with bots to rack up the pool
* Crate Drops - A "crate" will drop randomly in the channel that requires multiple `!break`'s to open it. Once opened, there will be 4 items you can get by typing the ! command under it. Items will include money, extra privlegges like holding more coins, and other items you can win.
* **Suicide Round** - There is no bank in this mode, and if you lose your nick through a NICK or QUIT, you lose your wallet. Round can last 3-7 days and the top 10 wallets will score.
* **Bank Round** - Round lasts a week and the top 10 players in the bank will score.
* **Flash Match** - Round lasts a day and the top 10 players in the bank will score.

###### Try it out
We are running IRCCEX actively in **#exchange** on **EFNet** & **SuperNETs**, come chat with us, make some money, and share ideas!

###### Mirrors
- [acid.vegas](https://acid.vegas/irccex) *(main)*
- [GitHub](https://github.com/acidvegas/irccex)
- [GitLab](https://gitlab.com/acidvegas/irccex)
