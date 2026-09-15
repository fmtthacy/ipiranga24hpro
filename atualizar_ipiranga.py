import json
import re
import unicodedata
from pathlib import Path
from collections import deque

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


ARQUIVO = Path("data.json")

URL_MATERIAS = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/"
    "a-ipiranga/institucional/sala-de-imprensa/todas-as-materias"
)

URL_SALA_IMPRENSA = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/"
    "a-ipiranga/institucional/sala-de-imprensa/"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}

# Limite para o robô não ficar percorrendo o site infinitamente.
MAX_MATERIAS = 100

# Limite de páginas que podem ser visitadas durante uma execução.
MAX_PAGINAS = 150


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto)
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


def eh_materia_ipiranga(url):
    """
    Verifica se o endereço parece ser uma matéria
    oficial da sala de imprensa da Ipiranga.
    """

    if not url:
        return False

    url_normalizada = normalizar(url)

    return (
        "ipiranga.com.br" in url_normalizada
        and "/sala-de-imprensa/" in url_normalizada
        and "/materias/" in url_normalizada
    )


def normalizar_url(url):
    """
    Remove fragmentos e pequenos problemas de URL.
    """

    try:
        partes = urlparse(url)

        return (
            partes.scheme
            + "://"
            + partes.netloc
            + partes.path
        ).rstrip("/")

    except Exception:
        return url


def encontrar_links_na_pagina(soup, url_atual):
    """
    Procura links para outras matérias oficiais.
    """

    encontrados = []

    for a in soup.find_all("a", href=True):

        href = a.get("href", "").strip()

        if not href:
            continue

        url = urljoin(url_atual, href)

        url = normalizar_url(url)

        if eh_materia_ipiranga(url):
            encontrados.append(url)

    return encontrados


def extrair_data(texto):
    """
    Tenta encontrar datas no formato brasileiro.
    """

    encontrados = re.findall(
        r"\b(\d{2}/\d{2}/\d{4})\b",
        texto
    )

    if not encontrados:
        return ""

    return encontrados[0]


def extrair_titulo(soup):
    """
    Extrai o título principal da matéria.
    """

    h1 = soup.find("h1")

    if h1:
        titulo = h1.get_text(" ", strip=True)

        if len(titulo) >= 20:
            return titulo

    # Fallback para title da página.
    if soup.title:
        titulo = soup.title.get_text(" ", strip=True)

        titulo = re.sub(
            r"\s*\|\s*Ipiranga.*$",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        if len(titulo) >= 20:
            return titulo.strip()

    return ""


def extrair_descricao(soup):
    """
    Procura o primeiro parágrafo útil da matéria.
    """

    ignorar = [
        "fique por dentro de todas as novidades",
        "sobre a ipiranga",
        "informações para imprensa",
        "informacoes para imprensa",
        "compartilhe",
        "tópicos da matéria",
        "topicos da materia",
        "copiar",
        "baixar material",
        "leia também",
        "leia tambem",
        "acesse",
        "veja também",
        "veja tambem"
    ]

    candidatos = []

    for p in soup.find_all("p"):

        texto = p.get_text(" ", strip=True)

        if len(texto) < 60:
            continue

        texto_normalizado = normalizar(texto)

        if any(
            palavra in texto_normalizado
            for palavra in ignorar
        ):
            continue

        candidatos.append(texto)

    if not candidatos:
        return "Confira a publicação oficial da Ipiranga."

    descricao = candidatos[0]

    if len(descricao) > 400:
        descricao = (
            descricao[:397]
            .rsplit(" ", 1)[0]
            + "..."
        )

    return descricao


def extrair_materia(url):
    """
    Abre uma matéria e extrai seus dados.
    """

    print("Lendo:", url)

    try:

        soup = baixar_pagina(url)

        titulo = extrair_titulo(soup)

        if not titulo:
            print("  Título não encontrado.")
            return None, []

        texto_pagina = soup.get_text(
            " ",
            strip=True
        )

        data = extrair_data(texto_pagina)

        descricao = extrair_descricao(soup)

        links_relacionados = encontrar_links_na_pagina(
            soup,
            url
        )

        materia = {
            "titulo": titulo,
            "descricao": descricao,
            "data": data,
            "fonte": "Ipiranga",
            "link": url
        }

        return materia, links_relacionados

    except Exception as erro:

        print(
            "  Erro ao ler matéria:",
            erro
        )

        return None, []


def encontrar_materias():
    """
    Faz uma busca em profundidade limitada pelo site oficial.

    Começa pela sala de imprensa e vai seguindo
    links que levam para outras matérias.
    """

    fila = deque()

    visitados = set()

    materias_encontradas = {}

    # Pontos iniciais.
    fila.append(
        normalizar_url(URL_MATERIAS)
    )

    fila.append(
        normalizar_url(URL_SALA_IMPRENSA)
    )

    paginas_visitadas = 0

    while fila:

        if paginas_visitadas >= MAX_PAGINAS:
            print(
                "Limite de páginas atingido."
            )
            break

        url = fila.popleft()

        url = normalizar_url(url)

        if url in visitados:
            continue

        visitados.add(url)

        paginas_visitadas += 1

        print(
            f"\nPágina {paginas_visitadas}/{MAX_PAGINAS}"
        )

        try:

            soup = baixar_pagina(url)

        except Exception as erro:

            print(
                "Não foi possível acessar:",
                erro
            )

            continue

        # Se for uma matéria, extrai os dados.
        if eh_materia_ipiranga(url):

            materia = extrair_dados_da_soup(
                soup,
                url
            )

            if materia:

                chave = normalizar_url(
                    materia["link"]
                )

                materias_encontradas[
                    chave
                ] = materia

                print(
                    "  ✓ Matéria encontrada:",
                    materia["titulo"]
                )

        # Procura links para outras matérias.
        novos_links = encontrar_links_na_pagina(
            soup,
            url
        )

        for novo_link in novos_links:

            novo_link = normalizar_url(
                novo_link
            )

            if novo_link in visitados:
                continue

            if novo_link in materias_encontradas:
                continue

            if len(
                materias_encontradas
            ) >= MAX_MATERIAS:
                break

            fila.append(novo_link)

        if len(
            materias_encontradas
        ) >= MAX_MATERIAS:

            print(
                f"\nLimite de {MAX_MATERIAS} matérias atingido."
            )

            break

    print("")
    print(
        "Páginas visitadas:",
        paginas_visitadas
    )

    print(
        "Matérias encontradas:",
        len(materias_encontradas)
    )

    return list(
        materias_encontradas.values()
    )


def extrair_dados_da_soup(soup, url):
    """
    Extrai dados de uma matéria usando uma página
    que já foi baixada.
    """

    titulo = extrair_titulo(soup)

    if not titulo:
        return None

    texto_pagina = soup.get_text(
        " ",
        strip=True
    )

    data = extrair_data(
        texto_pagina
    )

    descricao = extrair_descricao(
        soup
    )

    return {
        "titulo": titulo,
        "descricao": descricao,
        "data": data,
        "fonte": "Ipiranga",
        "link": url
    }


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

    if not isinstance(item, dict):
        return False

    titulo = item.get(
        "titulo",
        ""
    ).strip()

    link = item.get(
        "link",
        ""
    ).strip()

    if not titulo:
        return False

    if not link:
        return False

    if not eh_materia_ipiranga(link):
        return False

    if len(titulo) < 20:
        return False

    if normalizar(titulo) == normalizar(
        "Não encontramos resultados para sua pesquisa. 🙁"
    ):
        return False

    return True


def chave_link(item):

    return normalizar_url(
        item.get("link", "").strip()
    )


def data_para_numero(data):

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


def juntar_materias(antigas, novas):

    materias = {}

    # Mantém o histórico que já estava salvo.
    for item in antigas:

        if not limpar_materia(item):
            continue

        chave = chave_link(item)

        if chave:
            materias[chave] = item

    # Adiciona/atualiza as novas.
    for item in novas:

        if not limpar_materia(item):
            continue

        chave = chave_link(item)

        if chave:
            materias[chave] = item

    resultado = list(
        materias.values()
    )

    # Mais nova primeiro.
    resultado.sort(
        key=lambda item:
            data_para_numero(
                item.get("data", "")
            ),
        reverse=True
    )

    # IDs temporários apenas para compatibilidade
    # com o site atual.
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
    print(
        "======================================"
    )
    print(
        " BUSCA AUTOMÁTICA DE MATÉRIAS IPIRANGA"
    )
    print(
        "======================================"
    )
    print("")

    antigas = carregar_antigos()

    print(
        "Matérias já salvas:",
        len(antigas)
    )

    novas = encontrar_materias()

    resultado = juntar_materias(
        antigas,
        novas
    )

    salvar(resultado)

    print("")
    print(
        "======================================"
    )
    print(
        f" TOTAL FINAL: {len(resultado)} MATÉRIAS"
    )
    print(
        "======================================"
    )
    print("")
    print(
        "data.json atualizado com sucesso!"
    )


if __name__ == "__main__":
    main()
