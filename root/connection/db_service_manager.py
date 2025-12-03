import sqlite3
import os

class DBServiceManager:
    DB_PATH = '/home/caiomaxx/Documentos/projetos/web_chat_with_tkinter/root/connection/servers.db'

    @staticmethod
    def initialize_db():
        """Initializes the database and creates the servers table if it doesn't exist."""
        if not os.path.exists(DBServiceManager.DB_PATH):
            with sqlite3.connect(DBServiceManager.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE servers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        port INTEGER NOT NULL
                    )
                ''')
                conn.commit()

    @staticmethod
    def get_server_port(server_name):
        """Retrieves the port of a server based on its name."""
        DBServiceManager.initialize_db()
        with sqlite3.connect(DBServiceManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT port FROM servers WHERE name = ?', (server_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                raise ValueError(f"Server '{server_name}' not found in the database.")