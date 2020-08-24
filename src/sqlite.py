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
# TODO Wal mode?
#  https://stackoverflow.com/questions/19574286/how-to-merge-contents-of-sqlite-3-7-wal-file-into-main-database-file
#  then also add checkpoint pragma to close_connection before saving to join them.
db_connection.execute("PRAGMA journal_mode = MEMORY")
db_connection.execute("PRAGMA synchronous = OFF")
db_connection.execute("PRAGMA temp_store = MEMORY")
db_connection.execute("PRAGMA page_size = -65536")
db_cursor = db_connection.cursor()


def close_connection():
    """Saves database state and closes the connection opened at bot startup."""
    # TODO call on CTRL C too!
    db_connection.commit()
    db_connection.close()