import sqlite3

conn = sqlite3.connect('noir_database.sqlite')
cursor = conn.cursor()

guild_queue_list = {}