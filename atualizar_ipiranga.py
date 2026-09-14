import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_IPIRANGA = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/"
    "ipiranga/a-ipiranga/institucional/sala-de-imprensa/todas-as-materias"
)

ARQUIVO_DADOS = Path("data.json")
LIMITE_MATERIAS = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

MESES = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}


# ============================================================
# FUNÇÕES
# ============================================================

def limpar_texto(texto):
    if not texto:
        return ""

    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def data_para_timestamp(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y").timestamp()
    except Exception:
        return 0


def encontrar_data(texto):
    if not texto:
        return None

    # Procura DD/MM/YYYY
    resultado = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", texto)

    if resultado:
        dia, mes, ano = resultado.groups()
        return f"{dia}/{mes}/{ano}"

    # Procura datas no formato:
    # 10 set 2026
    # 03/09/2026
    resultado = re.search(
        r"\b(\d{1,2})\s+"
        r"(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)"
        r"(?:\s+de)?\s+(\d{4})\b",
        texto.lower(),
    )

    if resultado:
        dia, mes, ano = resultado.groups()
        numero_mes = MESES[mes]
        return f"{int(dia):02d}/{numero_mes:02d}/{ano}"

    return None


def obter_soup(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    resposta.raise_for_status()

    return BeautifulSoup(resposta.text, "html.parser")


def extrair_links_materias(soup):
    materias = []
    vistos = set()

    for a in soup.find_all("a", href=True):

        href = a.get("href", "").strip()

        if "/materias/" not in href:
            continue

        url = urljoin(URL_IPIRANGA, href)

        if url in vistos:
            continue

        titulo = limpar_texto(a.get_text(" ", strip=True))

        # Ignora links sem título útil
        if len(titulo) < 10:
            continue

        vistos.add(url)

        materias.append(
            {
                "titulo": titulo,
                "url": url,
            }
        )

    return materias


def extrair_materia(url, titulo_lista):
    try:
        soup = obter_soup(url)

    except Exception as erro:
        print(f"Não foi possível abrir: {url}")
        print(erro)
        return None

    titulo = titulo_lista

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    meta_title = soup.find("meta", attrs={"property": "og:title"})

    if meta_title and meta_title.get("content"):
        titulo = limpar_texto(meta_title["content"])

    elif soup.find("h1"):
        titulo = limpar_texto(
            soup.find("h1").get_text(" ", strip=True)
        )

    # --------------------------------------------------------
    # DESCRIÇÃO
    # --------------------------------------------------------

    descricao = ""

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta_description and meta_description.get("content"):
        descricao = limpar_texto(
            meta_description["content"]
        )

    if not descricao:
        meta_og = soup.find(
            "meta",
            attrs={"property": "og:description"}
        )

        if meta_og and meta_og.get("content"):
            descricao = limpar_texto(
                meta_og["content"]
            )

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    data = None

    # Tenta JSON-LD
    for script in soup.find_all(
        "script",
        attrs={"type": "application/ld+json"}
    ):

        try:
            conteudo = script.string

            if not conteudo:
                continue

            dados = json.loads(conteudo)

            if isinstance(dados, dict):
                lista = [dados]

            elif isinstance(dados, list):
                lista = dados

            else:
                lista = []

            for item in lista:

                if not isinstance(item, dict):
                    continue

                data_publicacao = (
                    item.get("datePublished")
                    or item.get("dateCreated")
                )

                if data_publicacao:
                    try:
                        data_obj = datetime.fromisoformat(
                            data_publicacao.replace("Z", "+00:00")
                        )

                        data = data_obj.strftime("%d/%m/%Y")
                        break

                    except Exception:
                        pass

        except Exception:
            pass

    # --------------------------------------------------------
    # Se não encontrou, procura no texto da página
    # --------------------------------------------------------

    if not data:

        texto_pagina = limpar_texto(
            soup.get_text(" ", strip=True)
        )

        data = encontrar_data(texto_pagina)

    # --------------------------------------------------------
    # DESCRIÇÃO DE SEGURANÇA
    # --------------------------------------------------------

    if not descricao:

        paragrafos = []

        for p in soup.find_all("p"):

            texto = limpar_texto(
                p.get_text(" ", strip=True)
            )

            if len(texto) > 80:
                paragrafos.append(texto)

        if paragrafos:
            descricao = paragrafos[0]

    if not descricao:
        descricao = "Confira a publicação completa no site oficial da Ipiranga."

    # --------------------------------------------------------
    # DATA FINAL
    # --------------------------------------------------------

    if not data:
        print(f"Data não encontrada: {titulo}")
        return None

    return {
        "titulo": titulo,
        "descricao": descricao,
        "data": data,
        "fonte": "Ipiranga",
        "link": url,
    }


# ============================================================
# CARREGAR DADOS EXISTENTES
# ============================================================

def carregar_dados_existentes():

    if not ARQUIVO_DADOS.exists():
        return []

    try:

        with open(
            ARQUIVO_DADOS,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

    except Exception as erro:

        print("Erro ao ler data.json:")
        print(erro)

    return []


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("======================================")
    print("IPIRANGA 24H - ATUALIZAÇÃO AUTOMÁTICA")
    print("======================================")

    dados_antigos = carregar_dados_existentes()

    print(
        f"Matérias já salvas: {len(dados_antigos)}"
    )

    # --------------------------------------------------------
    # ABRE A SALA DE IMPRENSA
    # --------------------------------------------------------

    print("Consultando a Sala de Imprensa da Ipiranga...")

    try:

        soup = obter_soup(URL_IPIRANGA)

    except Exception as erro:

        print("ERRO ao acessar o site da Ipiranga:")
        print(erro)

        print(
            "Os dados antigos foram preservados."
        )

        return

    # --------------------------------------------------------
    # ENCONTRA AS MATÉRIAS
    # --------------------------------------------------------

    links = extrair_links_materias(soup)

    print(
        f"Links de matérias encontrados: {len(links)}"
    )

    if not links:

        print(
            "Nenhuma matéria foi encontrada."
        )

        print(
            "Nada será alterado para evitar apagar "
            "as informações existentes."
        )

        return

    # --------------------------------------------------------
    # CRIA MAPA DAS MATÉRIAS ANTIGAS
    # --------------------------------------------------------

    materias_por_link = {}

    for materia in dados_antigos:

        link = materia.get("link")

        if link:
            materias_por_link[link] = materia

    # --------------------------------------------------------
    # CONSULTA CADA MATÉRIA
    # --------------------------------------------------------

    for indice, item in enumerate(links, start=1):

        print(
            f"[{indice}/{len(links)}] "
            f"{item['titulo']}"
        )

        materia = extrair_materia(
            item["url"],
            item["titulo"]
        )

        if not materia:
            continue

        materias_por_link[
            materia["link"]
        ] = materia

    # --------------------------------------------------------
    # TRANSFORMA EM LISTA
    # --------------------------------------------------------

    materias = list(
        materias_por_link.values()
    )

    # --------------------------------------------------------
    # REMOVE DATAS INVÁLIDAS
    # --------------------------------------------------------

    materias_validas = []

    for materia in materias:

        if materia.get("data"):
            materias_validas.append(materia)

    materias = materias_validas

    # --------------------------------------------------------
    # ORDENA DA MAIS NOVA PARA A MAIS ANTIGA
    # --------------------------------------------------------

    materias.sort(
        key=lambda item: data_para_timestamp(
            item.get("data", "")
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # LIMITA A QUANTIDADE
    # --------------------------------------------------------

    materias = materias[:LIMITE_MATERIAS]

    # --------------------------------------------------------
    # ADICIONA IDs
    # --------------------------------------------------------

    for indice, materia in enumerate(
        materias,
        start=1
    ):
        materia["id"] = indice

    # --------------------------------------------------------
    # SALVA
    # --------------------------------------------------------

    with open(
        ARQUIVO_DADOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            materias,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

        arquivo.write("\n")

    print("--------------------------------------")
    print(
        f"Atualização concluída: "
        f"{len(materias)} matérias."
    )
    print("--------------------------------------")


if __name__ == "__main__":
    main()
