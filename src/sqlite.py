import os
import sqlite3
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
