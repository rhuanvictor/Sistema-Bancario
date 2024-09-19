import sqlite3

def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT UNIQUE NOT NULL,
                        senha TEXT NOT NULL,
                        saldo REAL DEFAULT 0.0,
                        saques_diarios INTEGER DEFAULT 0,
                        ultimo_saque TEXT
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT,
                        tipo TEXT,
                        valor REAL,
                        data TEXT
                     )''')

    conn.commit()
    conn.close()
