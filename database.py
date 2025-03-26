import sqlite3

def init_db():
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cart (clothing_id TEXT)''')
    conn.commit()
    conn.close()

def add_to_cart(clothing_id):
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()
    c.execute("INSERT INTO cart (clothing_id) VALUES (?)", (clothing_id,))
    conn.commit()
    conn.close()

def get_cart():
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()
    c.execute("SELECT clothing_id FROM cart")
    items = [row[0] for row in c.fetchall()]
    conn.close()
    return items

def clear_cart():
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()
    c.execute("DELETE FROM cart")
    conn.commit()
    conn.close()