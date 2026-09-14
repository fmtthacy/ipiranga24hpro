import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


URL_BASE = "https://www.ipiranga.com.br"

URL_SALA_IMPRENSA = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/"
    "ipiranga/a-ipiranga/institucional/sala-de-imprensa/todas-as-materias"
)

ARQUIVO = Path("data.json")
LIMITE = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def limpar(texto):
    if not texto:
        return ""
    return re.sub(r"\s+", " ", texto).strip()


def converter_data(data):
    if not data:
        return None

    data = limpar(data)

    # DD/MM/YYYY
    resultado = re.search(
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        data
    )

    if resultado:
        dia, mes, ano = resultado.groups()
        return f"{int(dia):02d}/{int(mes):02d}/{ano}"

    # YYYY-MM-DD
    resultado = re.search(
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        data
    )

    if resultado:
        ano, mes, dia = resultado.groups()
        return f"{dia}/{mes}/{ano}"

    return None


def obter_pagina(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    resposta.raise_for_status()

    return BeautifulSoup(
        resposta.text,
        "html.parser"
    )


def encontrar_materias(soup):

    materias = []
    links_vistos = set()

    for link in soup.find_all("a", href=True):

        href = link["href"].strip()

        url = urljoin(
            URL_BASE,
            href
        )

        texto = limpar(
            link.get_text(
                " ",
                strip=True
            )
        )

        if not texto:
            continue

        # Aceita diferentes formatos de URL
        # usados dentro da Sala de Imprensa.
        parece_materia = any(
            termo in url.lower()
            for termo in [
                "/materias/",
                "/materia/",
                "materias",
                "imprensa"
            ]
        )

        if not parece_materia:
            continue

        if url in links_vistos:
            continue

        # Evita links genéricos da página
        if url.rstrip("/") == URL_SALA_IMPRENSA.rstrip("/"):
            continue

        links_vistos.add(url)

        materias.append({
            "titulo": texto,
            "url": url
        })

    return materias


def extrair_materia(url, titulo_inicial):

    try:
        soup = obter_pagina(url)

    except Exception as erro:
        print("Erro ao abrir:", url)
        print(erro)
        return None

    titulo = titulo_inicial
    descricao = ""
    data = None

    # -------------------------------
    # TÍTULO
    # -------------------------------

    og_title = soup.find(
        "meta",
        attrs={
            "property": "og:title"
        }
    )

    if og_title and og_title.get("content"):
        titulo = limpar(
            og_title["content"]
        )

    if soup.find("h1"):
        texto_h1 = limpar(
            soup.find("h1").get_text(
                " ",
                strip=True
            )
        )

        if len(texto_h1) > 10:
            titulo = texto_h1

    # -------------------------------
    # DESCRIÇÃO
    # -------------------------------

    meta = soup.find(
        "meta",
        attrs={
            "name": "description"
        }
    )

    if meta and meta.get("content"):
        descricao = limpar(
            meta["content"]
        )

    if not descricao:

        meta = soup.find(
            "meta",
            attrs={
                "property": "og:description"
            }
        )

        if meta and meta.get("content"):
            descricao = limpar(
                meta["content"]
            )

    # -------------------------------
    # DATA
    # -------------------------------

    # Primeiro tenta JSON-LD
    for script in soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        }
    ):

        try:

            if not script.string:
                continue

            dados = json.loads(
                script.string
            )

            if isinstance(dados, dict):
                dados = [dados]

            if not isinstance(dados, list):
                continue

            for item in dados:

                if not isinstance(item, dict):
                    continue

                valor = (
                    item.get("datePublished")
                    or item.get("dateCreated")
                    or item.get("dateModified")
                )

                if valor:

                    data = converter_data(
                        str(valor)
                    )

                    if data:
                        break

            if data:
                break

        except Exception:
            pass

    # -------------------------------
    # Procura a data no texto
    # -------------------------------

    if not data:

        texto = limpar(
            soup.get_text(
                " ",
                strip=True
            )
        )

        data = converter_data(texto)

    # -------------------------------
    # Descrição alternativa
    # -------------------------------

    if not descricao:

        for paragrafo in soup.find_all("p"):

            texto = limpar(
                paragrafo.get_text(
                    " ",
                    strip=True
                )
            )

            if len(texto) >= 80:

                descricao = texto
                break

    if not descricao:

        descricao = (
            "Confira a publicação completa "
            "no site oficial da Ipiranga."
        )

    # -------------------------------
    # Se não encontrou data,
    # não salva a matéria.
    # -------------------------------

    if not data:

        print(
            "Data não encontrada:",
            titulo
        )

        return None

    return {
        "titulo": titulo,
        "descricao": descricao,
        "data": data,
        "fonte": "Ipiranga",
        "link": url
    }


def carregar_existentes():

    if not ARQUIVO.exists():
        return []

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

    except Exception as erro:

        print("Erro lendo data.json:")
        print(erro)

    return []


def data_numero(data):

    try:

        return datetime.strptime(
            data,
            "%d/%m/%Y"
        )

    except Exception:

        return datetime.min


def main():

    print("")
    print("==============================")
    print("IPIRANGA 24H")
    print("Atualização automática")
    print("==============================")
    print("")

    antigas = carregar_existentes()

    print(
        "Matérias já existentes:",
        len(antigas)
    )

    # Mantém tudo que já existe
    por_link = {}

    for materia in antigas:

        link = materia.get("link")

        if link:
            por_link[link] = materia

    print("")
    print(
        "Acessando a Sala de Imprensa..."
    )

    try:

        soup = obter_pagina(
            URL_SALA_IMPRENSA
        )

    except Exception as erro:

        print("")
        print(
            "ERRO: não foi possível acessar "
            "a Ipiranga."
        )
        print(erro)

        print("")
        print(
            "O data.json NÃO será alterado."
        )

        return

    materias = encontrar_materias(
        soup
    )

    print(
        "Links encontrados:",
        len(materias)
    )

    if not materias:

        print("")
        print(
            "Nenhuma matéria encontrada."
        )
        print(
            "O data.json NÃO será alterado."
        )

        return

    print("")

    novas = 0

    # Limita a quantidade consultada
    # para evitar excesso de requisições.
    for item in materias[:30]:

        print(
            "Consultando:",
            item["titulo"]
        )

        materia = extrair_materia(
            item["url"],
            item["titulo"]
        )

        if not materia:
            continue

        link = materia["link"]

        if link not in por_link:
            novas += 1

        por_link[link] = materia

    # -------------------------------
    # Junta antigas + novas
    # -------------------------------

    resultado = list(
        por_link.values()
    )

    # -------------------------------
    # Ordena da mais nova
    # para a mais antiga
    # -------------------------------

    resultado.sort(
        key=lambda item: data_numero(
            item.get("data", "")
        ),
        reverse=True
    )

    # -------------------------------
    # Mantém no máximo 50
    # -------------------------------

    resultado = resultado[:LIMITE]

    # -------------------------------
    # IDs
    # -------------------------------

    for numero, materia in enumerate(
        resultado,
        start=1
    ):
        materia["id"] = numero

    # -------------------------------
    # Salva
    # -------------------------------

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

        arquivo.write("\n")

    print("")
    print("==============================")
    print(
        "ATUALIZAÇÃO CONCLUÍDA!"
    )
    print(
        "Total de matérias:",
        len(resultado)
    )
    print(
        "Novas matérias:",
        novas
    )
    print("==============================")


if __name__ == "__main__":
    main()
