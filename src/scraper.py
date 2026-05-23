import re
import requests
from bs4 import BeautifulSoup


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