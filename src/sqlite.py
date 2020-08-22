import os
import sqlite3

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
db_connection = sqlite3.connect(os.path.join(definitions.root_dir, definitions.database))
db_connection.execute("PRAGMA journal_mode = MEMORY")   # TODO WAL instead?
db_connection.execute("PRAGMA synchronous = OFF")
db_connection.execute("PRAGMA temp_store = MEMORY")
db_connection.execute("PRAGMA page_size = -65536")

db_cursor = db_connection.cursor()
