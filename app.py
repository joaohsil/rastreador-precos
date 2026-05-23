import os
import re
import sqlite3
import smtplib
import requests
from datetime import datetime
from email.message import EmailMessage
from bs4 import BeautifulSoup

URL = "https://www.amazon.com.br/Rei-Amarelo-Edi%C3%A7%C3%A3o-Definitiva/dp/6555982683/ref=pd_sbs_d_sccl_1_1/146-5545016-1048166?psc=1"


def baixar_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    resposta = requests.get(url, headers=headers, timeout=10)

    if resposta.status_code != 200:
        raise Exception(f"Erro ao acessar página. Status code: {resposta.status_code}")

    return resposta.text


def limpar_preco(texto_preco):
    texto_limpo = texto_preco.strip()

    match = re.search(r"R\$\s?[\d\.]+,\d{2}", texto_limpo)

    if not match:
        raise Exception(f"Não foi possível encontrar preço no texto: {texto_preco}")

    preco_texto = match.group()

    preco_numero = (
        preco_texto
        .replace("R$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    return float(preco_numero)


def buscar_preco_amazon(html):
    sopa = BeautifulSoup(html, "html.parser")

    seletores_possiveis = [
        "span.a-price span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div span.a-offscreen",
        "#price span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#newBuyBoxPrice",
    ]

    for seletor in seletores_possiveis:
        elementos = sopa.select(seletor)

        for elemento in elementos:
            texto_preco = elemento.get_text(strip=True)

            if not texto_preco:
                continue

            try:
                preco = limpar_preco(texto_preco)
                return preco
            except Exception:
                continue

    texto_pagina = sopa.get_text(" ", strip=True)
    preco = limpar_preco(texto_pagina)

    return preco

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

def enviar_email_alerta(produto, preco_atual, ultimo_preco, url):
    email_remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    email_destinatario = os.getenv("EMAIL_DESTINATARIO")

    if not email_remetente or not senha_app or not email_destinatario:
        raise Exception("Variáveis de ambiente de e-mail não configuradas.")

    diferenca = ultimo_preco - preco_atual

    mensagem = EmailMessage()
    mensagem["Subject"] = "Alerta de Queda de Preço!"
    mensagem["From"] = email_remetente
    mensagem["To"] = email_destinatario

    corpo = f"""
O preço do produto caiu!

Produto: {produto}
Preço anterior: R$ {ultimo_preco:.2f}
Preço atual: R$ {preco_atual:.2f}
Queda: R$ {diferenca:.2f}

Link do produto:
{url}
"""

    mensagem.set_content(corpo)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_remetente, senha_app)
        smtp.send_message(mensagem)

PRODUTO = "O Rei de Amarelo - Edição Definitiva"

criar_banco()

ultimo_registro = buscar_ultimo_preco(PRODUTO)

html = baixar_html(URL)
preco_atual = buscar_preco_amazon(html)

print(f"Produto: {PRODUTO}")
print(f"Preço atual: R$ {preco_atual:.2f}")

if ultimo_registro is None:
    print("Nenhum preço anterior encontrado. Salvando primeira consulta.")
else:
    ultimo_preco, data_hora = ultimo_registro

    print(f"Último preço salvo: R$ {ultimo_preco:.2f}")
    print(f"Data do último registro: {data_hora}")

    if preco_atual < ultimo_preco:
        diferenca = ultimo_preco - preco_atual
        print("ALERTA: O preço caiu!")
        print(f"Queda de R$ {diferenca:.2f}")
    elif preco_atual > ultimo_preco:
        diferenca = preco_atual - ultimo_preco
        print("O preço aumentou.")
        print(f"Aumento de R$ {diferenca:.2f}")
        enviar_email_alerta(PRODUTO, preco_atual, ultimo_preco, URL)
        print("E-mail de alerta enviado com sucesso.")
    else:
        print("O preço permaneceu igual.")

salvar_preco(PRODUTO, preco_atual)

print("Preço atual salvo no banco de dados com sucesso.")