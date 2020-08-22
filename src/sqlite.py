import os
import sqlite3
<<<<<<< HEAD

import definitions

# ░░░░░░░░▀▀▀██████▄▄▄░░░░░░░░░░░░
# ░░░░░░▄▄▄▄▄░░█████████▄░░░░░░░░░
# ░░░░░▀▀▀▀█████▌░▀▐▄░▀▐█░░░░░░░░░
# ░░░▀▀█████▄▄░▀██████▄██░░░░░░░░░
# ░░░▀▄▄▄▄▄░░▀▀█▄▀█════█▀░░░░░░░░░
# ░░░░░░░░▀▀▀▄░░▀▀███░▀░░░░░░▄▄░░░
# ░░░░░▄███▀▀██▄████████▄░▄▀▀▀██▌░
# ░░░██▀▄▄▄██▀▄███▀░▀▀████░░░░░▀█▄
# ▄▀▀▀▄██▄▀▀▌████▒▒▒▒▒▒███░░░░▌▄▄▀
# ▌░░░░▐▀████▐███▒▒▒▒▒▐██▌░░░░░░░░
# ▀▄░░▄▀░░░▀▀████▒▒▒▒▄██▀░░░░░░░░░
# ░░▀▀░░░░░░▀▀█████████▀░░░░░░░░░░
# ░░░░░░░░░░░░▀▀██████▀░░░░░░░░░░░
# ░░░░░░░░░░░░░█░░░░░█░░░░░░░░░░░░
# ░░░░░░░░░░░░█░░░░░░█░░░░░░░░░░░░
# ░░░░░░░░░░░█░░░░░░░█░░░░░░░░░░░░
# ░░░░░░░░░░█▒█▄░░░█▀▒▀██▄▄▄▄▄░░░░
# ░░░░░░░░▄▀░░▄▀░░░░▀▀▀▀▀▀▀▀▀▀░░░░
# ░░░░░░▄▀▄▄▄▀░░ I want to go fast, safety? That's for boomers.
db_connection = sqlite3.connect(os.path.join(definitions.root_dir, definitions.database))#, isolation_level=None)
db_connection.execute("PRAGMA journal_mode = MEMORY")   # TODO WAL instead?
db_connection.execute("PRAGMA synchronous = OFF")
db_connection.execute("PRAGMA temp_store = MEMORY")
db_connection.execute("PRAGMA page_size = -65536")

db_cursor = db_connection.cursor()
=======
from contextlib import contextmanager

import definitions

"""
TODO 
    Database should have one connection in WAL mode. Opening a new connection with each function call
    is a really bad idea. 
"""

#db_connection = sqlite3.connect(os.path.join(definitions.root_dir, definitions.database), isolation_level=None)
#db_connection.execute("PRAGMA journal_mode = WAL")
#db_connection.execute('PRAGMA foreign_keys = ON')

#db_cursor = db_connection.cursor()
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
