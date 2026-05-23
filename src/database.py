import sqlite3
from datetime import datetime


def criar_banco():
    conexao = sqlite3.connect("precos.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            preco REAL NOT NULL,
            data_hora TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


def salvar_preco(produto, preco):
    conexao = sqlite3.connect("precos.db")
    cursor = conexao.cursor()

    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO historico_precos (produto, preco, data_hora)
        VALUES (?, ?, ?)
    """, (produto, preco, data_hora))

    conexao.commit()
    conexao.close()


def buscar_ultimo_preco(produto):
    conexao = sqlite3.connect("precos.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT preco, data_hora
        FROM historico_precos
        WHERE produto = ?
        ORDER BY id DESC
        LIMIT 1
    """, (produto,))

    resultado = cursor.fetchone()

    conexao.close()

    return resultado