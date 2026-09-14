import json
import re
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ARQUIVO = Path("data.json")

URL_MATERIAS = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/"
    "a-ipiranga/institucional/sala-de-imprensa/todas-as-materias"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


def normalizar(texto):
    texto = texto or ""

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip().lower()


def baixar_pagina(url):
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


def encontrar_links_materias():

    print("Buscando matérias no site oficial...")

    soup = baixar_pagina(URL_MATERIAS)

    links = []
    vistos = set()

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if "/materias/" not in href:
            continue

        if href.startswith("/"):
            href = (
                "https://www.ipiranga.com.br"
                + href
            )

        if href in vistos:
            continue

        vistos.add(href)

        links.append(href)

    print(
        f"Links de matérias encontrados: {len(links)}"
    )

    return links


def extrair_materia(url):

    print("Lendo:", url)

    try:

        soup = baixar_pagina(url)

        # -----------------------------------------
        # TÍTULO
        # -----------------------------------------

        titulo = ""

        h1 = soup.find("h1")

        if h1:
            titulo = h1.get_text(
                " ",
                strip=True
            )

        if not titulo or len(titulo) < 20:
            print("Título não encontrado.")
            return None

        # -----------------------------------------
        # DATA
        # -----------------------------------------

        data = ""

        texto_pagina = soup.get_text(
            " ",
            strip=True
        )

        # Primeiro tenta "Atualizado em DD/MM/AAAA"
        encontrado = re.search(
            r"Atualizado\s+em\s+(\d{2}/\d{2}/\d{4})",
            texto_pagina,
            re.IGNORECASE
        )

        if encontrado:
            data = encontrado.group(1)

        # Se não encontrou, tenta qualquer data.
        if not data:

            encontrado = re.search(
                r"\b(\d{2}/\d{2}/\d{4})\b",
                texto_pagina
            )

            if encontrado:
                data = encontrado.group(1)

        # -----------------------------------------
        # DESCRIÇÃO
        # -----------------------------------------

        descricao = ""

        # Procura os parágrafos reais da matéria.
        for p in soup.find_all("p"):

            texto = p.get_text(
                " ",
                strip=True
            )

            if len(texto) < 60:
                continue

            texto_normalizado = normalizar(texto)

            # Ignora textos genéricos.
            ignorar = [
                "fique por dentro de todas as novidades",
                "sobre a ipiranga",
                "informações para imprensa",
                "compartilhe",
                "tópicos da matéria",
                "topicos da materia"
            ]

            if any(
                palavra in texto_normalizado
                for palavra in ignorar
            ):
                continue

            descricao = texto
            break

        if not descricao:
            descricao = (
                "Confira a publicação oficial da Ipiranga."
            )

        if len(descricao) > 400:
            descricao = (
                descricao[:397]
                .rsplit(" ", 1)[0]
                + "..."
            )

        return {
            "titulo": titulo,
            "descricao": descricao,
            "data": data,
            "fonte": "Ipiranga",
            "link": url
        }

    except Exception as erro:

        print(
            "Erro ao ler matéria:",
            erro
        )

        return None


def carregar_antigos():

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
            "Erro ao ler data.json:",
            erro
        )

    return []


def limpar_materia(item):

    titulo = item.get(
        "titulo",
        ""
    ).strip()

    link = item.get(
        "link",
        ""
    ).strip()

    # Remove os erros criados pelas versões anteriores.
    if re.fullmatch(
        r"\d{1,2}\s+"
        r"(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
        titulo.lower()
    ):
        return False

    if normalizar(titulo) == (
        "não encontramos resultados para sua pesquisa. 🙁"
    ):
        return False

    if len(titulo) < 20:
        return False

    if "/materias/" not in link:
        return False

    return True


def chave_link(item):

    link = item.get(
        "link",
        ""
    ).strip()

    return normalizar(link)


def juntar_materias(antigas, novas):

    materias = {}

    # -----------------------------------------
    # Mantém matérias antigas válidas.
    # -----------------------------------------

    for item in antigas:

        if not limpar_materia(item):
            continue

        chave = chave_link(item)

        if chave:
            materias[chave] = item

    # -----------------------------------------
    # Atualiza com as matérias novas.
    # -----------------------------------------

    for item in novas:

        if not item:
            continue

        if not limpar_materia(item):
            continue

        chave = chave_link(item)

        materias[chave] = item

    resultado = list(
        materias.values()
    )

    # -----------------------------------------
    # Ordenação por data.
    # -----------------------------------------

    def ordenar(item):

        data = item.get(
            "data",
            ""
        )

        try:

            dia, mes, ano = data.split("/")

            return (
                int(ano),
                int(mes),
                int(dia)
            )

        except Exception:

            return (
                0,
                0,
                0
            )

    resultado.sort(
        key=ordenar,
        reverse=True
    )

    # -----------------------------------------
    # IDs
    # -----------------------------------------

    for numero, item in enumerate(
        resultado,
        start=1
    ):

        item["id"] = numero

    return resultado


def salvar(dados):

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


def main():

    print("")
    print("======================================")
    print(" ATUALIZAÇÃO AUTOMÁTICA DA IPIRANGA")
    print("======================================")
    print("")

    antigas = carregar_antigos()

    print(
        f"Matérias antigas: {len(antigas)}"
    )

    # -----------------------------------------
    # Descobre os links.
    # -----------------------------------------

    try:

        links = encontrar_links_materias()

    except Exception as erro:

        print(
            "Não foi possível acessar a página:",
            erro
        )

        return

    # -----------------------------------------
    # Lê cada matéria individualmente.
    # -----------------------------------------

    novas = []

    for link in links:

        materia = extrair_materia(link)

        if materia:

            novas.append(materia)

    print("")
    print(
        f"Matérias processadas: {len(novas)}"
    )

    # -----------------------------------------
    # Junta antigas + novas sem duplicar.
    # -----------------------------------------

    resultado = juntar_materias(
        antigas,
        novas
    )

    # -----------------------------------------
    # Salva data.json.
    # -----------------------------------------

    salvar(resultado)

    print("")
    print(
        f"Total final: {len(resultado)} matérias"
    )

    print(
        "data.json atualizado com sucesso!"
    )


if __name__ == "__main__":
    main()
