# Rastreador de Preços

Projeto em Python para monitorar o preço de um produto na web, salvar o histórico em banco SQLite e enviar um alerta por e-mail quando houver queda de preço.

## Objetivo

Este projeto foi desenvolvido para praticar automação com Python, web scraping, persistência de dados, regras de negócio e envio de notificações por e-mail.

## Tecnologias utilizadas

- Python
- Requests
- BeautifulSoup4
- SQLite
- smtplib
- Gmail SMTP
- Variáveis de ambiente

## Funcionalidades

- Acessa uma página de produto
- Extrai o preço atual usando web scraping
- Limpa e converte o preço para número decimal
- Salva o histórico de preços em SQLite
- Compara o preço atual com o último preço salvo
- Envia e-mail quando detecta queda de preço

## Como executar o projeto

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

No Windows PowerShell:

```powershell
setx EMAIL_REMETENTE "seuemail@gmail.com"
setx EMAIL_SENHA_APP "sua_senha_de_app_do_gmail"
setx EMAIL_DESTINATARIO "seuemail@gmail.com"
```

Depois de configurar, feche e abra o terminal novamente.

### 4. Executar o script

No Windows, usando o Python do ambiente virtual:

```powershell
.\venv\Scripts\python.exe app.py
```

## Variáveis de ambiente

O projeto utiliza:

```txt
EMAIL_REMETENTE
EMAIL_SENHA_APP
EMAIL_DESTINATARIO
```

A senha usada deve ser uma senha de aplicativo do Gmail, não a senha normal da conta.

## Banco de dados

O projeto cria automaticamente um arquivo SQLite chamado:

```txt
precos.db
```

A tabela utilizada é:

```txt
historico_precos
```

Com as colunas:

```txt
id
produto
preco
data_hora
```

## Fluxo do sistema

```txt
1. Baixar HTML da página do produto
2. Extrair o preço com BeautifulSoup
3. Limpar o preço e converter para float
4. Buscar o último preço salvo no SQLite
5. Comparar preço atual com preço anterior
6. Enviar e-mail se houver queda
7. Salvar o preço atual no banco
```

## Automação futura

Este projeto pode ser automatizado em um Raspberry Pi usando cron.

Exemplo:

```bash
0 0 * * * /caminho/do/projeto/venv/bin/python /caminho/do/projeto/app.py
```

