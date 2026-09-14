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

    padrao = re.search(
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        data
    )

    if padrao:
        dia, mes, ano = padrao.groups()
        return f"{int(dia):02d}/{int(mes):02d}/{ano}"

    padrao = re.search(
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        data
    )

    if padrao:
        ano, mes, dia = padrao.groups()
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
    vistos = set()

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

        if len(texto) < 15:
            continue

        if "/materias/" not in url.lower():
            continue

        if url in vistos:
            continue

        vistos.add(url)

        materias.append({
            "titulo": texto,
            "url": url
        })

    return materias


def extrair_descricao(soup, titulo):

    # Primeiro tenta a descrição específica da matéria.
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

        if (
            descricao
            and descricao.lower() != titulo.lower()
            and "fique por dentro de todas as novidades" not in descricao.lower()
        ):
            return descricao

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

        if (
            descricao
            and descricao.lower() != titulo.lower()
            and "fique por dentro de todas as novidades" not in descricao.lower()
        ):
            return descricao

    # Procura textos dos parágrafos.
    candidatos = []

    for p in soup.find_all("p"):

        texto = limpar(
            p.get_text(
                " ",
                strip=True
            )
        )

        texto_lower = texto.lower()

        if len(texto) < 50:
            continue

        if "fique por dentro de todas as novidades" in texto_lower:
            continue

        if texto_lower == titulo.lower():
            continue

        candidatos.append(texto)

    if candidatos:
        return candidatos[0]

    return (
        "Confira a publicação completa "
        "no site oficial da Ipiranga."
    )


def extrair_materia(url, titulo_inicial):

    try:
        soup = obter_pagina(url)

    except Exception as erro:

        print(
            "Erro ao abrir:",
            url
        )

        print(erro)

        return None

    titulo = titulo_inicial

    # Título específico
    h1 = soup.find("h1")

    if h1:

        texto = limpar(
            h1.get_text(
                " ",
                strip=True
            )
        )

        if len(texto) > 10:
            titulo = texto

    # Data
    data = None

    # Procura datas no código HTML
    texto_html = str(soup)

    datas = re.findall(
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        texto_html
    )

    if datas:

        for valor in datas:

            data_teste = converter_data(
                valor
            )

            if data_teste:
                data = data_teste
                break

    # Se não achou, procura no texto
    if not data:

        texto = limpar(
            soup.get_text(
                " ",
                strip=True
            )
        )

        data = converter_data(
            texto
        )

    if not data:

        print(
            "Data não encontrada:",
            titulo
        )

        return None

    descricao = extrair_descricao(
        soup,
        titulo
    )

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

        print(
            "Erro lendo data.json:",
            erro
        )

    return []


def data_numero(data):

    try:

        return datetime.strptime(
            data,
            "%d/%m/%Y"
        )

    except Exception:

        return datetime.min


def chave_materia(materia):

    titulo = limpar(
        materia.get("titulo", "")
    ).lower()

    data = materia.get(
        "data",
        ""
    )

    # Usa título + data para reconhecer
    # a mesma matéria mesmo que o link antigo
    # seja diferente.
    return (
        re.sub(
            r"[^a-z0-9]+",
            "",
            titulo
        ),
        data
    )


def main():

    print("")
    print("==============================")
    print("IPIRANGA 24H")
    print("ATUALIZAÇÃO AUTOMÁTICA")
    print("==============================")
    print("")

    antigas = carregar_existentes()

    print(
        "Matérias antigas:",
        len(antigas)
    )

    try:

        soup = obter_pagina(
            URL_SALA_IMPRENSA
        )

    except Exception as erro:

        print("")
        print(
            "Não foi possível acessar "
            "a Sala de Imprensa."
        )

        print(erro)

        print(
            "O data.json não será alterado."
        )

        return

    links = encontrar_materias(
        soup
    )

    print(
        "Matérias encontradas:",
        len(links)
    )

    if not links:

        print(
            "Nenhuma matéria encontrada."
        )

        print(
            "O data.json não será alterado."
        )

        return

    materias = {}

    # Primeiro coloca as antigas.
    for materia in antigas:

        chave = chave_materia(
            materia
        )

        if chave[0]:
            materias[chave] = materia

    novas = 0

    # Depois atualiza com as matérias
    # encontradas diretamente no site.
    for item in links[:50]:

        print(
            "Buscando:",
            item["titulo"]
        )

        materia = extrair_materia(
            item["url"],
            item["titulo"]
        )

        if not materia:
            continue

        chave = chave_materia(
            materia
        )

        if chave not in materias:
            novas += 1

        materias[chave] = materia

    resultado = list(
        materias.values()
    )

    # Ordena por data.
    resultado.sort(
        key=lambda item: data_numero(
            item.get("data", "")
        ),
        reverse=True
    )

    # Mantém no máximo 50.
    resultado = resultado[:LIMITE]

    # Recria os IDs.
    for numero, materia in enumerate(
        resultado,
        start=1
    ):

        materia["id"] = numero

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
    print("ATUALIZAÇÃO CONCLUÍDA")
    print(
        "Total:",
        len(resultado)
    )
    print(
        "Novas:",
        novas
    )
    print("==============================")


if __name__ == "__main__":
    main()
