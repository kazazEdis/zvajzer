import sqlite3
from datetime import date


def timestamp():
    return date.today().isoformat()


def create(contact_number, operator, timestmp):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    op = [(contact_number, operator, timestmp)]
    c.executemany('INSERT INTO operators VALUES (?,?,?)', op)
    conn.commit()
    conn.close()


def read(contact_number):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM operators WHERE contact_number=?", (contact_number,))
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results


def update(timestmp, rowid):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    op = [(timestmp, rowid)]
    c.executemany('UPDATE operators SET timestamp=? WHERE rowid=?', op)
    conn.commit()
    conn.close()


# create(921213592, 'TOMATO', timestamp())
# print(read(921213592))
# update('TELE2', timestamp(), 1)


