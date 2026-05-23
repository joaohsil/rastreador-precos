import json

from src.scraper import baixar_html, buscar_preco_amazon
from src.database import criar_banco, salvar_preco, buscar_ultimo_preco
from src.email_alert import enviar_email_alerta


def carregar_configuracao():
    with open("config.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def monitorar_produto(produto_config):
    produto = produto_config["nome"]
    url = produto_config["url"]

    print("-" * 60)
    print(f"Monitorando: {produto}")

    ultimo_registro = buscar_ultimo_preco(produto)

    html = baixar_html(url)
    preco_atual = buscar_preco_amazon(html)

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

            enviar_email_alerta(produto, preco_atual, ultimo_preco, url)

            print("E-mail de alerta enviado com sucesso.")
        elif preco_atual > ultimo_preco:
            diferenca = preco_atual - ultimo_preco
            print("O preço aumentou.")
            print(f"Aumento de R$ {diferenca:.2f}")
        else:
            print("O preço permaneceu igual.")

    salvar_preco(produto, preco_atual)

    print("Preço atual salvo no banco de dados com sucesso.")


def main():
    config = carregar_configuracao()
    produtos = config["produtos"]

    criar_banco()

    for produto_config in produtos:
        try:
            monitorar_produto(produto_config)
        except Exception as erro:
            nome = produto_config.get("nome", "Produto sem nome")
            print("-" * 60)
            print(f"Erro ao monitorar produto: {nome}")
            print(f"Detalhes do erro: {erro}")


if __name__ == "__main__":
    main()      