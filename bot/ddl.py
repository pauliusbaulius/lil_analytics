from . import sqlite


def build_database():
    """Builds database from a schema. Should only be called when bot starts.

    This functions contains database schema for the bot. This is the only file containing schema and any structural
    changes to the database. If schema is altered, you should delete the old database.
    """
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.executescript("""
                    CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY, 
                    name TEXT NOT NULL,
                    history_parser INTEGER DEFAULT 0,
                    deleted INTEGER DEFAULT 0
                    );
                    
                    CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY, 
                    server_id INTEGER NOT NULL, 
                    name TEXT,
                    deleted INTEGER DEFAULT 0 
                    --FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY, 
                    server_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    author_name TEXT NOT NULL,
                    length INTEGER NOT NULL,
                    date DATE NOT NULL,
                    date_last_edited DATE DEFAULT NULL,
                    is_bot INTEGER NOT NULL,
                    is_pinned INTEGER NOT NULL,
                    no_attachments INTEGER NOT NULL,
                    no_embeds INTEGER NOT NULL,
                    mentions_everyone INTEGER NOT NULL,
                    --date_added timestamp DATE DEFAULT (datetime('now','utc')), for later tests
                    deleted INTEGER DEFAULT 0
                    --FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
                    --FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS user_mentions (
                    id INTEGER,
                    mentioned_user_id INTEGER,
                    PRIMARY KEY (id, mentioned_user_id)
                    --FOREIGN KEY (id) REFERENCES messages(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS channel_mentions (
                    id INTEGER,
                    mentioned_channel_id INTEGER,
                    PRIMARY KEY (id, mentioned_channel_id)
                    --FOREIGN KEY (id) REFERENCES messages(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS role_mentions (
                    id INTEGER,
                    mentioned_role_id INTEGER,
                    PRIMARY KEY (id, mentioned_role_id)
                    --FOREIGN KEY (id) REFERENCES messages(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS message_reactions (
                    id INTEGER,
                    reaction_id TEXT,
                    reacted_id INTEGER,
                    reaction_hash INTEGER NOT NULL,
                    PRIMARY KEY (id, reaction_id, reacted_id)
                    --FOREIGN KEY (id) REFERENCES messages(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS bot_replies (
                    message TEXT NOT NULL,
                    date_added TEXT NOT NULL
                    );
                    
                    """)
    cn.commit()
