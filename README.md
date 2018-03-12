# irccex
A fantasy cryptocurrency trading channel bot for the Internet Relay Chat (IRC) protocol.

*"You can pretend trade currencies, instead of trade pretend currencies!"*

###### Requirments
 - [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*
 - [PySocks](https://pypi.python.org/pypi/PySocks) *(**Optional:** For using the `proxy` setting.)*

###### Information
This bot lets users of an IRC channel "pretend" trade cryptocurrencies. Real time market data from [CoinMarketCap](https://coinmarketcap.com/) is used to obtain the values of cryptocurrencies traded.

Users can make an exchange account with the `!register` command, and after 24 hours, are given `init_funds` to start trading with.

There is no authentication required for interacting with exchange accounts. Everything is regulated based on your current nick. Users can `/nick` to any nick with an account to access it. This means it is possible to steal cryptocurrency using the `!send` command.

A bank account can be made or added to with the `!cashout` command, which deposits all of your USD to your bank account. Money in the bank can only be deposited, you can not withdraw or send money from it, making it an ever growing balance.

Maintaining your nick and doing frequent cashouts to your bank is the only way to protect your money. The goal is to have the largest bank account on IRC, lol.

There is a loop that runs to randomly put the exchange in maintenance mode, which locks the use of all exchange commands.

###### Trading Pair Rules
- USD can only be used for buying or selling BTC, ETH, & LTC.

- BTC & ETH are the only major trading pairs between all other cryptocurrencies.

###### Fees & Minimums
| Command | Fee | Minimum |
| --- | --- | --- |
| !cashout | 2% | $1500 USD Balance |
| !send | 1% | $1200 Balance |
| !trade | 0.5% | $5 |

###### General Commands
| Command | Description |
| --- | --- |
| @irccex | Information about the bot. |
| @irccex help | Information about the commands. |

###### CoinMarketCap Commands
| Command | Description |
| --- | --- |
| $\<name> | Return information for the \<name> cryptocurrency. |
| $\<name,name,name..> | Return information for all the \<name,name,name..> cryptocurrencies. *(Max = 10)* |
| !top | Return information for the top 10 cryptocurrencies based on the market cap. |
| !top \<1h/24h/7d> | Return information for the top 10 cryptocurrencies based on the 1h, 24h, or 7d percent value increase. |
| !top value | Return information for the top 10 cryptocurrencies based on the value. |
| !top volume | Return information for the top 10 cryptocurrencies based on the 24h volume. |
| !bottom \<1h/24h/7d> | Return information for the bottom 10 cryptocurrencies based on the 1h, 24h, or 7d percent value increase. |
| !bottom value | Return information for the bottom 10 cryptocurrencies based on the value. |
| !value \<amount> \<name> | Convert \<amount> of the \<name> cryptocurrency to it's value. |

###### Exchange Commands
| Command | Description |
| --- | --- |
| !bank | Return your total bank account balance. |
| !cashout | Deposit all your USD to your bank account. |
| !register | Register an exchange account. |
| !rich | Return the top 10 richest bank accounts. |
| !send \<nick> \<amount> \<symbol> | Send \<amount> of \<symbol> to \<nick>. |
| !trade \<pair> \<amount> | Trade \<amount> between \<pair>. |
| !wallet | View your exchange wallet. |

- \<amount> can be the symbols amount, USD amount if prefixed with a $, or the total amount you hold if * is used.
	* `!send acidvegas 0.05 BTC` sends 0.05 BTC to acidvegas.
	* `!send chrono $10.00 BTC` sends $10.00 worth of BTC to chrono.
	* `!send mikejonez * BTC` sends all of your BTC to mikejonez.

- \<pair> is the from_symbol/to_symbol you are wanting to make trades with.
	* `!trade ETH/NANO 0.14` trades 0.14 ETH to NANO.
	* `!trade XRP/BTC $100` trades $100 USD worth of XRP to BTC.
	* `!trade ETH/DOGE *` trades all of your ETH to DOGE.
