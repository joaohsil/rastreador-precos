import json
import logging
import os

from src.scraper import baixar_html, buscar_preco_amazon
from src.database import criar_banco, salvar_preco, buscar_ultimo_preco
from src.email_alert import enviar_email_alerta


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/rastreador.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def carregar_configuracao():
    with open("config.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def monitorar_produto(produto_config, modo_teste=False):
    produto = produto_config["nome"]
    url = produto_config["url"]

    logging.info("-" * 60)
    logging.info(f"Monitorando: {produto}")

    ultimo_registro = buscar_ultimo_preco(produto)

    html = baixar_html(url)
    preco_atual = buscar_preco_amazon(html)

    logging.info(f"Preço atual: R$ {preco_atual:.2f}")

    if ultimo_registro is None:
        logging.info("Nenhum preço anterior encontrado. Salvando primeira consulta.")
    else:
        ultimo_preco, data_hora = ultimo_registro

        logging.info(f"Último preço salvo: R$ {ultimo_preco:.2f}")
        logging.info(f"Data do último registro: {data_hora}")

        if preco_atual < ultimo_preco or modo_teste:
            diferenca = max(ultimo_preco - preco_atual, 0)

            if modo_teste and preco_atual >= ultimo_preco:
                logging.warning("MODO TESTE: simulando alerta de queda de preço.")
            else:
                logging.warning("ALERTA: O preço caiu!")

            logging.warning(f"Queda de R$ {diferenca:.2f}")

            enviar_email_alerta(produto, preco_atual, ultimo_preco, url)

            logging.info("E-mail de alerta enviado com sucesso.")
        elif preco_atual > ultimo_preco:
            diferenca = preco_atual - ultimo_preco
            logging.info("O preço aumentou.")
            logging.info(f"Aumento de R$ {diferenca:.2f}")
        else:
            logging.info("O preço permaneceu igual.")

    salvar_preco(produto, preco_atual)

    logging.info("Preço atual salvo no banco de dados com sucesso.")


def main():
    config = carregar_configuracao()
    produtos = config["produtos"]
    modo_teste = config.get("modo_teste", False)

    criar_banco()

    if modo_teste:
        logging.warning("MODO TESTE ATIVADO: alertas podem ser enviados mesmo sem queda real.")

    for produto_config in produtos:
        try:
            monitorar_produto(produto_config, modo_teste)
        except Exception as erro:
            nome = produto_config.get("nome", "Produto sem nome")
            logging.error("-" * 60)
            logging.error(f"Erro ao monitorar produto: {nome}")
            logging.error(f"Detalhes do erro: {erro}")


if __name__ == "__main__":
    main()