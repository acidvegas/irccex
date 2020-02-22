#!/usr/bin/env python
# IRC Cryptocurrency Exchange (IRCCEX) - Developed by acidvegas in Python (https://acid.vegas/irccex)
# irccex.py

import os
import sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or '.')
sys.path += ('core',)

print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('IRC Cryptocurrency Exchange (IRCCEX)'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://acid.vegas/irccex'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
import irc
irc.Bot.run()