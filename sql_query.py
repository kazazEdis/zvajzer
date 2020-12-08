import sqlite3
from datetime import date


def timestamp():
    return date.today().strftime("%d-%m-%Y")


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

