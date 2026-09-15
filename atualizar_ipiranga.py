import json
import re
import unicodedata
from pathlib import Path
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


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

# Quantidade máxima de matérias diferentes que o robô pode guardar.
MAX_MATERIAS = 100

# Quantidade máxima de páginas que o robô pode visitar em uma execução.
MAX_PAGINAS = 150


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


def normalizar_url(url):
    """
    Remove partes desnecessárias da URL,
    como !ut/p/z1/... e mantém somente o endereço
    principal da matéria.
    """

    try:

        partes = urlparse(url)

        caminho = partes.path

        # Remove /!ut/p/... das URLs do portal.
        if "/!ut/" in caminho:
            caminho = caminho.split("/!ut/")[0]

        caminho = caminho.rstrip("/")

        # Mantém somente o domínio oficial.
        return (
            partes.scheme
            + "://"
            + partes.netloc
            + caminho
        )

    except Exception:

        return url


def eh_materia_ipiranga(url):
    """
    Verifica se a URL pertence ao site oficial
    da Ipiranga e aponta para uma matéria.
    """

    if not url:
        return False

    url_normalizada = normalizar(
        url
    )

    return (
        "ipiranga.com.br" in url_normalizada
        and "/sala-de-imprensa/" in url_normalizada
        and "/materias/" in url_normalizada
    )


def encontrar_links_na_pagina(
    soup,
    url_atual
):
    """
    Encontra links para outras matérias oficiais.
    """

    encontrados = []

    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a.get(
            "href",
            ""
        ).strip()

        if not href:
            continue

        url = urljoin(
            url_atual,
            href
        )

        url = normalizar_url(
            url
        )

        if eh_materia_ipiranga(url):

            encontrados.append(
                url
            )

    return encontrados


def extrair_titulo(soup):
    """
    Extrai o título principal.
    """

    h1 = soup.find("h1")

    if h1:

        titulo = h1.get_text(
            " ",
            strip=True
        )

        if len(titulo) >= 20:
            return titulo

    # Segunda tentativa usando o <title>.
    if soup.title:

        titulo = soup.title.get_text(
            " ",
            strip=True
        )

        titulo = re.sub(
            r"\s*\|\s*Ipiranga.*$",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        if len(titulo) >= 20:
            return titulo.strip()

    return ""


def extrair_data(texto):
    """
    Procura uma data no formato DD/MM/AAAA.
    """

    # Primeiro tenta encontrar "Atualizado em".
    encontrado = re.search(
        r"Atualizado\s+em\s+(\d{2}/\d{2}/\d{4})",
        texto,
        re.IGNORECASE
    )

    if encontrado:
        return encontrado.group(1)

    # Depois procura qualquer data.
    encontrado = re.search(
        r"\b(\d{2}/\d{2}/\d{4})\b",
        texto
    )

    if encontrado:
        return encontrado.group(1)

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
        "veja também",
        "veja tambem",
        "acesse"
    ]

    for p in soup.find_all("p"):

        texto = p.get_text(
            " ",
            strip=True
        )

        if len(texto) < 60:
            continue

        texto_normalizado = normalizar(
            texto
        )

        if any(
            palavra in texto_normalizado
            for palavra in ignorar
        ):
            continue

        if len(texto) > 400:

            texto = (
                texto[:397]
                .rsplit(" ", 1)[0]
                + "..."
            )

        return texto

    return (
        "Confira a publicação oficial da Ipiranga."
    )


def extrair_dados_da_soup(
    soup,
    url
):
    """
    Extrai todas as informações de uma matéria.
    """

    titulo = extrair_titulo(
        soup
    )

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
        "link": normalizar_url(url)
    }


def encontrar_materias():
    """
    Começa pela sala de imprensa e percorre os links
    para outras matérias oficiais.

    Existe um limite para evitar que o robô fique
    navegando infinitamente pelo site.
    """

    fila = deque()

    visitados = set()

    materias_encontradas = {}

    # Pontos iniciais.
    fila.append(
        normalizar_url(
            URL_MATERIAS
        )
    )

    fila.append(
        normalizar_url(
            URL_SALA_IMPRENSA
        )
    )

    paginas_visitadas = 0

    while fila:

        if paginas_visitadas >= MAX_PAGINAS:

            print(
                "Limite de páginas atingido."
            )

            break

        url = fila.popleft()

        url = normalizar_url(
            url
        )

        if url in visitados:
            continue

        visitados.add(
            url
        )

        paginas_visitadas += 1

        print(
            f"\nPágina "
            f"{paginas_visitadas}/"
            f"{MAX_PAGINAS}"
        )

        try:

            soup = baixar_pagina(
                url
            )

        except Exception as erro:

            print(
                "Não foi possível acessar:",
                erro
            )

            continue

        # Se for uma matéria, salva.
        if eh_materia_ipiranga(url):

            materia = extrair_dados_da_soup(
                soup,
                url
            )

            if materia:

                chave = chave_materia(
                    materia
                )

                if chave:

                    materias_encontradas[
                        chave
                    ] = materia

                    print(
                        "  ✓ Matéria encontrada:",
                        materia["titulo"]
                    )

        # Procura outras matérias.
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

            if len(
                materias_encontradas
            ) >= MAX_MATERIAS:
                break

            fila.append(
                novo_link
            )

        if len(
            materias_encontradas
        ) >= MAX_MATERIAS:

            print(
                f"\nLimite de "
                f"{MAX_MATERIAS} matérias atingido."
            )

            break

    print("")
    print(
        "Páginas visitadas:",
        paginas_visitadas
    )

    print(
        "Matérias diferentes encontradas:",
        len(materias_encontradas)
    )

    return list(
        materias_encontradas.values()
    )


def carregar_antigos():
    """
    Carrega as matérias que já estavam no data.json.
    """

    if not ARQUIVO.exists():
        return []

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(
                arquivo
            )

        if isinstance(
            dados,
            list
        ):
            return dados

    except Exception as erro:

        print(
            "Erro ao ler data.json:",
            erro
        )

    return []


def limpar_materia(item):
    """
    Verifica se o item realmente parece ser
    uma matéria válida da Ipiranga.
    """

    if not isinstance(
        item,
        dict
    ):
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

    if not eh_materia_ipiranga(
        link
    ):
        return False

    if len(titulo) < 20:
        return False

    if normalizar(titulo) == normalizar(
        "Não encontramos resultados para sua pesquisa. 🙁"
    ):
        return False

    return True


def chave_materia(item):
    """
    Cria uma identificação baseada no título da matéria.

    Isso evita que a mesma publicação seja salva várias
    vezes por causa de versões PT-BR, EN ou URLs diferentes.
    """

    titulo = normalizar(
        item.get(
            "titulo",
            ""
        )
    )

    # Remove caracteres especiais.
    titulo = re.sub(
        r"[^a-z0-9\s]",
        "",
        titulo
    )

    titulo = re.sub(
        r"\s+",
        " ",
        titulo
    ).strip()

    return titulo


def data_para_numero(data):

    try:

        dia, mes, ano = data.split(
            "/"
        )

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


def juntar_materias(
    antigas,
    novas
):
    """
    Junta histórico + novas matérias,
    elimina duplicadas e ordena por data.
    """

    materias = {}

    # Primeiro processa o histórico.
    for item in antigas:

        if not limpar_materia(
            item
        ):
            continue

        chave = chave_materia(
            item
        )

        if not chave:
            continue

        if chave not in materias:

            materias[chave] = item

    # Depois processa as matérias encontradas.
    for item in novas:

        if not limpar_materia(
            item
        ):
            continue

        chave = chave_materia(
            item
        )

        if not chave:
            continue

        # A versão encontrada agora substitui a antiga.
        materias[chave] = item

    resultado = list(
        materias.values()
    )

    # Mais recente primeiro.
    resultado.sort(
        key=lambda item:
            data_para_numero(
                item.get(
                    "data",
                    ""
                )
            ),
        reverse=True
    )

    # IDs.
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
        "=========================================="
    )
    print(
        " BUSCA AUTOMÁTICA DE MATÉRIAS IPIRANGA"
    )
    print(
        "=========================================="
    )
    print("")

    antigas = carregar_antigos()

    print(
        "Matérias salvas anteriormente:",
        len(antigas)
    )

    novas = encontrar_materias()

    resultado = juntar_materias(
        antigas,
        novas
    )

    salvar(
        resultado
    )

    print("")
    print(
        "=========================================="
    )
    print(
        f" TOTAL FINAL: {len(resultado)} MATÉRIAS"
    )
    print(
        "=========================================="
    )
    print("")
    print(
        "Duplicadas removidas automaticamente."
    )
    print(
        "data.json atualizado com sucesso!"
    )


if __name__ == "__main__":
    main()
