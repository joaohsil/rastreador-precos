import os
import smtplib
from email.message import EmailMessage


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