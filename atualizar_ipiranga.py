mport BeautifulSoup


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


# ============================================================
# LIMITES
# ============================================================

# Quantidade máxima de matérias diferentes que serão salvas.
MAX_MATERIAS = 130

# Quantidade máxima de páginas que o robô poderá visitar.
MAX_PAGINAS = 300


# ============================================================
# FUNÇÕES BÁSICAS
# ============================================================

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


# ============================================================
# NORMALIZAÇÃO DAS URLs
# ============================================================

def normalizar_url(url):
    """
    Remove partes desnecessárias das URLs do portal.

    Exemplo:

    URL cheia:
    /materias/noticia/!ut/p/z1/...

    vira:

    /materias/noticia
    """

    if not url:
        return ""

    try:

        partes = urlparse(url)

        if not partes.netloc:
            return url

        caminho = partes.path

        # Remove parâmetros internos do portal.
        if "/!ut/" in caminho:
            caminho = caminho.split("/!ut/")[0]

        caminho = caminho.rstrip("/")

        return (
            partes.scheme
            + "://"
            + partes.netloc
            + caminho
        )

    except Exception:

        return url


def obter_slug_materia(url):
    """
    Obtém o nome final da matéria na URL.

    Isso ajuda a identificar versões diferentes
    da mesma publicação.
    """

    url = normalizar_url(url)

    if not url:
        return ""

    marcador = "/materias/"

    if marcador not in url:
        return ""

    slug = url.split(
        marcador,
        1
    )[1]

    slug = slug.split(
        "/",
        1
    )[0]

    return normalizar(
        slug
    )


# ============================================================
# VERIFICAÇÃO DE MATÉRIAS
# ============================================================

def eh_materia_ipiranga(url):

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


# ============================================================
# LINKS
# ============================================================

def encontrar_links_na_pagina(
    soup,
    url_atual
):

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

        if eh_materia_ipiranga(
            url
        ):

            encontrados.append(
                url
            )

    return encontrados


# ============================================================
# EXTRAÇÃO DO TÍTULO
# ============================================================

def extrair_titulo(soup):

    h1 = soup.find("h1")

    if h1:

        titulo = h1.get_text(
            " ",
            strip=True
        )

        if len(titulo) >= 20:
            return titulo

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


# ============================================================
# EXTRAÇÃO DA DATA
# ============================================================

def extrair_data(texto):

    # Primeiro procura uma data próxima de "Atualizado em".
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


# ============================================================
# EXTRAÇÃO DA DESCRIÇÃO
# ============================================================

def extrair_descricao(soup):

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

    candidatos = []

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

        candidatos.append(
            texto
        )

    if not candidatos:

        return (
            "Confira a publicação oficial da Ipiranga."
        )

    descricao = candidatos[0]

    if len(descricao) > 400:

        descricao = (
            descricao[:397]
            .rsplit(" ", 1)[0]
            + "..."
        )

    return descricao


# ============================================================
# EXTRAÇÃO COMPLETA DA MATÉRIA
# ============================================================

def extrair_dados_da_soup(
    soup,
    url
):

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


# ============================================================
# IDENTIFICAÇÃO DA MATÉRIA
# ============================================================

def chave_materia(item):
    """
    Cria uma chave para evitar duplicações.

    O título é usado como principal identificação.
    O slug da URL também ajuda quando disponível.
    """

    titulo = normalizar(
        item.get(
            "titulo",
            ""
        )
    )

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

    if titulo:
        return "titulo:" + titulo

    slug = obter_slug_materia(
        item.get(
            "link",
            ""
        )
    )

    if slug:
        return "slug:" + slug

    return ""


# ============================================================
# BUSCA AUTOMÁTICA
# ============================================================

def encontrar_materias():

    fila = deque()

    visitados = set()

    materias_encontradas = {}

    # Páginas iniciais.
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

        # Limite de páginas.
        if paginas_visitadas >= MAX_PAGINAS:

            print(
                "\nLimite de páginas atingido."
            )

            break

        url = fila.popleft()

        url = normalizar_url(
            url
        )

        # Evita visitar a mesma URL duas vezes.
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

        # ====================================================
        # SE FOR UMA MATÉRIA
        # ====================================================

        if eh_materia_ipiranga(
            url
        ):

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

        # ====================================================
        # PROCURA OUTRAS MATÉRIAS
        # ====================================================

        novos_links = encontrar_links_na_pagina(
            soup,
            url
        )

        for novo_link in novos_links:

            novo_link = normalizar_url(
                novo_link
            )

            if not novo_link:
                continue

            if novo_link in visitados:
                continue

            if len(
                materias_encontradas
            ) >= MAX_MATERIAS:

                break

            fila.append(
                novo_link
            )

        # ====================================================
        # PARAR AO CHEGAR EM 130
        # ====================================================

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


# ============================================================
# CARREGAR DATA.JSON
# ============================================================

def carregar_antigos():

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


# ============================================================
# LIMPEZA
# ============================================================

def limpar_materia(item):

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

    if normalizar(
        titulo
    ) == normalizar(
        "Não encontramos resultados para sua pesquisa. 🙁"
    ):

        return False

    return True


# ============================================================
# DATA PARA ORDENAÇÃO
# ============================================================

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


# ============================================================
# JUNTAR E ELIMINAR DUPLICADAS
# ============================================================

def juntar_materias(
    antigas,
    novas
):

    materias = {}

    # ========================================================
    # MATÉRIAS ANTIGAS
    # ========================================================

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

    # ========================================================
    # MATÉRIAS NOVAS
    # ========================================================

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

        # A informação mais recente encontrada
        # substitui a versão antiga.
        materias[chave] = item

    # ========================================================
    # CONVERTE PARA LISTA
    # ========================================================

    resultado = list(
        materias.values()
    )

    # ========================================================
    # ORDENA DA MAIS NOVA PARA A MAIS ANTIGA
    # ========================================================

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

    # ========================================================
    # LIMITA A 130
    # ========================================================

    resultado = resultado[
        :MAX_MATERIAS
    ]

    # ========================================================
    # IDs
    # ========================================================

    for numero, item in enumerate(
        resultado,
        start=1
    ):

        item["id"] = numero

    return resultado


# ============================================================
# SALVAR DATA.JSON
# ============================================================

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


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

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

    print("")

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

    print("")


if __name__ == "__main__":

    main()
import json
import re
import unicodedata
from pathlib import Path
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO = Path("data.json")

DOMINIO = "https://www.ipiranga.com.br"

URL_SALA_IMPRENSA = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/"
    "a-ipiranga/institucional/sala-de-imprensa/"
)

URL_TODAS_MATERIAS = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/"
    "a-ipiranga/institucional/sala-de-imprensa/todas-as-materias"
)

URL_SITEMAP = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/ipiranga/sitemap"
)

MAX_MATERIAS = 130

# Aumentado porque agora o robô procura em várias fontes.
MAX_PAGINAS = 500

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

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


def normalizar_url(url):
    """
    Limpa URLs do portal da Ipiranga.

    Remove:
    - parâmetros
    - fragmentos
    - caminhos internos !ut/p/...
    """

    if not url:
        return ""

    try:
        partes = urlparse(url)

        if not partes.netloc:
            return ""

        caminho = partes.path

        if "/!ut/" in caminho:
            caminho = caminho.split("/!ut/")[0]

        caminho = caminho.rstrip("/")

        return (
            "https://"
            + partes.netloc
            + caminho
        )

    except Exception:
        return ""


# ============================================================
# DOWNLOAD
# ============================================================

def baixar(url):
    try:

        resposta = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        resposta.raise_for_status()

        return resposta.text

    except Exception as erro:

        print(
            "Erro ao acessar:",
            url
        )

        print(
            "Motivo:",
            erro
        )

        return ""


def soup_da_url(url):

    html = baixar(url)

    if not html:
        return None

    return BeautifulSoup(
        html,
        "html.parser"
    )


# ============================================================
# VERIFICAR MATÉRIA
# ============================================================

def eh_materia(url):

    url_normalizada = normalizar(
        url
    )

    return (
        "ipiranga.com.br" in url_normalizada
        and "/sala-de-imprensa/" in url_normalizada
        and "/materias/" in url_normalizada
    )


# ============================================================
# CHAVE DA MATÉRIA
# ============================================================

def chave_materia(item):

    titulo = normalizar(
        item.get(
            "titulo",
            ""
        )
    )

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

    if titulo:
        return titulo

    return normalizar(
        item.get(
            "link",
            ""
        )
    )


# ============================================================
# TÍTULO
# ============================================================

def extrair_titulo(soup):

    h1 = soup.find("h1")

    if h1:

        titulo = h1.get_text(
            " ",
            strip=True
        )

        if len(titulo) >= 20:
            return titulo

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


# ============================================================
# DATA
# ============================================================

def extrair_data(soup):

    texto = soup.get_text(
        " ",
        strip=True
    )

    encontrado = re.search(
        r"Atualizado\s+em\s+(\d{2}/\d{2}/\d{4})",
        texto,
        re.IGNORECASE
    )

    if encontrado:
        return encontrado.group(1)

    encontrado = re.search(
        r"\b(\d{2}/\d{2}/\d{4})\b",
        texto
    )

    if encontrado:
        return encontrado.group(1)

    return ""


# ============================================================
# DESCRIÇÃO
# ============================================================

def extrair_descricao(soup):

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


# ============================================================
# EXTRAIR MATÉRIA
# ============================================================

def extrair_materia(url):

    print(
        "Lendo matéria:",
        url
    )

    soup = soup_da_url(
        url
    )

    if not soup:
        return None

    titulo = extrair_titulo(
        soup
    )

    if not titulo:
        return None

    return {
        "titulo": titulo,
        "descricao": extrair_descricao(soup),
        "data": extrair_data(soup),
        "fonte": "Ipiranga",
        "link": normalizar_url(url)
    }


# ============================================================
# ENCONTRAR LINKS
# ============================================================

def encontrar_links(soup, url_atual):

    encontrados = set()

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

        if eh_materia(url):

            encontrados.add(
                url
            )

    return encontrados


# ============================================================
# BUSCAR MATÉRIAS ATRAVÉS DO SITEMAP
# ============================================================

def buscar_no_sitemap():

    print("")
    print(
        "=========================================="
    )

    print(
        " PROCURANDO MATÉRIAS NO SITEMAP"
    )

    print(
        "=========================================="
    )

    soup = soup_da_url(
        URL_SITEMAP
    )

    if not soup:
        return set()

    encontrados = set()

    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a.get(
            "href",
            ""
        ).strip()

        url = urljoin(
            URL_SITEMAP,
            href
        )

        url = normalizar_url(
            url
        )

        if eh_materia(url):

            encontrados.add(
                url
            )

    print(
        "Matérias encontradas no sitemap:",
        len(encontrados)
    )

    return encontrados


# ============================================================
# BUSCA POR CRAWLING
# ============================================================

def buscar_por_crawling():

    print("")
    print(
        "=========================================="
    )

    print(
        " PROCURANDO MATÉRIAS PELA SALA DE IMPRENSA"
    )

    print(
        "=========================================="
    )

    fila = deque()

    visitados = set()

    materias = set()

    fila.append(
        URL_SALA_IMPRENSA
    )

    fila.append(
        URL_TODAS_MATERIAS
    )

    paginas = 0

    while fila:

        if paginas >= MAX_PAGINAS:

            print(
                "Limite de páginas atingido."
            )

            break

        url = normalizar_url(
            fila.popleft()
        )

        if not url:
            continue

        if url in visitados:
            continue

        visitados.add(
            url
        )

        paginas += 1

        print(
            f"Página {paginas}/{MAX_PAGINAS}:",
            url
        )

        soup = soup_da_url(
            url
        )

        if not soup:
            continue

        # Se for uma matéria.
        if eh_materia(url):

            materias.add(
                url
            )

            print(
                "  ✓ Matéria encontrada"
            )

            if len(materias) >= MAX_MATERIAS:

                break

        # Procura links para outras matérias.
        links = encontrar_links(
            soup,
            url
        )

        for link in links:

            if link not in visitados:

                fila.append(
                    link
                )

    print("")
    print(
        "Páginas visitadas:",
        paginas
    )

    print(
        "Matérias encontradas pelo crawling:",
        len(materias)
    )

    return materias


# ============================================================
# CARREGAR MATÉRIAS ANTIGAS
# ============================================================

def carregar_antigas():

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
            "Erro ao carregar data.json:",
            erro
        )

    return []


# ============================================================
# LIMPAR MATÉRIA
# ============================================================

def materia_valida(item):

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

    if not eh_materia(link):
        return False

    if len(titulo) < 20:
        return False

    if normalizar(titulo) == normalizar(
        "Não encontramos resultados para sua pesquisa. 🙁"
    ):
        return False

    return True


# ============================================================
# DATA PARA ORDENAÇÃO
# ============================================================

def data_numero(data):

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


# ============================================================
# JUNTAR MATÉRIAS
# ============================================================

def juntar_materias(
    antigas,
    novas
):

    todas = {}

    # --------------------------------------------------------
    # MATÉRIAS ANTIGAS
    # --------------------------------------------------------

    for item in antigas:

        if not materia_valida(item):
            continue

        chave = chave_materia(
            item
        )

        if chave:

            todas[chave] = item

    # --------------------------------------------------------
    # MATÉRIAS NOVAS
    # --------------------------------------------------------

    for item in novas:

        if not materia_valida(item):
            continue

        chave = chave_materia(
            item
        )

        if chave:

            todas[chave] = item

    resultado = list(
        todas.values()
    )

    # --------------------------------------------------------
    # MAIS RECENTES PRIMEIRO
    # --------------------------------------------------------

    resultado.sort(
        key=lambda item:
            data_numero(
                item.get(
                    "data",
                    ""
                )
            ),
        reverse=True
    )

    # --------------------------------------------------------
    # LIMITE DE 130
    # --------------------------------------------------------

    resultado = resultado[
        :MAX_MATERIAS
    ]

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    for numero, item in enumerate(
        resultado,
        start=1
    ):

        item["id"] = numero

    return resultado


# ============================================================
# SALVAR
# ============================================================

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


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("")
    print(
        "=========================================="
    )

    print(
        " IPIRANGA 24H - ATUALIZAÇÃO AUTOMÁTICA"
    )

    print(
        "=========================================="
    )

    print("")

    # --------------------------------------------------------
    # 1. CARREGA HISTÓRICO
    # --------------------------------------------------------

    antigas = carregar_antigas()

    print(
        "Matérias já salvas:",
        len(antigas)
    )

    # --------------------------------------------------------
    # 2. BUSCA NO SITEMAP
    # --------------------------------------------------------

    links_sitemap = buscar_no_sitemap()

    # --------------------------------------------------------
    # 3. BUSCA PELA SALA DE IMPRENSA
    # --------------------------------------------------------

    links_crawling = buscar_por_crawling()

    # --------------------------------------------------------
    # 4. JUNTA TODAS AS URLs
    # --------------------------------------------------------

    links = (
        links_sitemap
        | links_crawling
    )

    print("")
    print(
        "=========================================="
    )

    print(
        " TOTAL DE LINKS ÚNICOS ENCONTRADOS:",
        len(links)
    )

    print(
        "=========================================="
    )

    # --------------------------------------------------------
    # 5. EXTRAI AS MATÉRIAS
    # --------------------------------------------------------

    novas = []

    for contador, link in enumerate(
        links,
        start=1
    ):

        if len(novas) >= MAX_MATERIAS:
            break

        print("")
        print(
            f"[{contador}/{len(links)}]"
        )

        materia = extrair_materia(
            link
        )

        if materia:

            novas.append(
                materia
            )

    # --------------------------------------------------------
    # 6. JUNTA COM O HISTÓRICO
    # --------------------------------------------------------

    resultado = juntar_materias(
        antigas,
        novas
    )

    # --------------------------------------------------------
    # 7. SALVA
    # --------------------------------------------------------

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

    if len(resultado) < MAX_MATERIAS:

        print(
            "O site oficial não entregou "
            f"{MAX_MATERIAS} matérias acessíveis "
            "nesta execução."
        )

        print(
            "Nenhuma notícia falsa foi criada."
        )

    else:

        print(
            f"As {MAX_MATERIAS} matérias foram encontradas."
        )

    print("")

    print(
        "Duplicadas removidas automaticamente."
    )

    print(
        "data.json atualizado com sucesso!"
    )

    print("")


if __name__ == "__main__":

    main()
