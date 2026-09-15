import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE_URL = "https://www.ipiranga.com.br"

TODAS_AS_MATERIAS = (
    "https://www.ipiranga.com.br/wps/portal/pt-br/"
    "ipiranga/a-ipiranga/institucional/sala-de-imprensa/"
    "todas-as-materias/"
)

ARQUIVO_SAIDA = "data.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def baixar(url):
    try:
        req = Request(url, headers=HEADERS)

        with urlopen(req, timeout=30) as resposta:
            return resposta.read().decode(
                "utf-8",
                errors="ignore"
            )

    except Exception as erro:
        print(f"ERRO ao acessar: {url}")
        print(erro)
        return ""


def limpar(texto):
    if not texto:
        return ""

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def eh_materia(url):
    caminho = urlparse(url).path.lower()

    return (
        "/sala-de-imprensa/materias/" in caminho
        and urlparse(url).netloc.endswith(
            "ipiranga.com.br"
        )
    )


def encontrar_materias(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    urls = set()

    for a in soup.find_all(
        "a",
        href=True
    ):
        href = a["href"].strip()

        if not href:
            continue

        url = urljoin(
            BASE_URL,
            href
        )

        if eh_materia(url):
            urls.add(url)

    return urls


def extrair_materia(url):
    html = baixar(url)

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    titulo = ""

    meta_titulo = soup.find(
        "meta",
        attrs={
            "property": "og:title"
        }
    )

    if meta_titulo:
        titulo = limpar(
            meta_titulo.get(
                "content",
                ""
            )
        )

    if not titulo:
        h1 = soup.find("h1")

        if h1:
            titulo = limpar(
                h1.get_text(
                    " ",
                    strip=True
                )
            )

    if not titulo:
        return None

    descricao = ""

    meta_descricao = soup.find(
        "meta",
        attrs={
            "property": "og:description"
        }
    )

    if meta_descricao:
        descricao = limpar(
            meta_descricao.get(
                "content",
                ""
            )
        )

    if not descricao:
        meta_descricao = soup.find(
            "meta",
            attrs={
                "name": "description"
            }
        )

        if meta_descricao:
            descricao = limpar(
                meta_descricao.get(
                    "content",
                    ""
                )
            )

    if not descricao:
        paragrafos = []

        for p in soup.find_all("p"):
            texto = limpar(
                p.get_text(
                    " ",
                    strip=True
                )
            )

            if len(texto) >= 50:
                paragrafos.append(texto)

        if paragrafos:
            descricao = " ".join(
                paragrafos[:2]
            )

    data = ""

    # Procura a data nos metadados.
    possiveis_datas = [
        soup.find(
            "meta",
            attrs={
                "property":
                "article:published_time"
            }
        ),
        soup.find(
            "meta",
            attrs={
                "property":
                "article:modified_time"
            }
        ),
        soup.find(
            "meta",
            attrs={
                "name": "date"
            }
        ),
    ]

    for elemento in possiveis_datas:
        if elemento:
            valor = elemento.get(
                "content",
                ""
            ).strip()

            if valor:
                data = valor
                break

    # Procura elemento <time>.
    if not data:
        time = soup.find(
            "time",
            attrs={
                "datetime": True
            }
        )

        if time:
            data = time.get(
                "datetime",
                ""
            ).strip()

    # Procura datas no texto da página.
    if not data:
        texto = soup.get_text(
            " ",
            strip=True
        )

        padrao = re.search(
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",
            texto
        )

        if padrao:
            data = padrao.group(0)

    if not data:
        data = datetime.now().strftime(
            "%d/%m/%Y"
        )

    imagem = ""

    meta_imagem = soup.find(
        "meta",
        attrs={
            "property": "og:image"
        }
    )

    if meta_imagem:
        imagem = urljoin(
            url,
            meta_imagem.get(
                "content",
                ""
            )
        )

    return {
        "titulo": titulo,
        "descricao": descricao,
        "data": data,
        "fonte": "Ipiranga",
        "link": url,
    }


def carregar_existentes():
    try:
        with open(
            ARQUIVO_SAIDA,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

    except Exception as erro:
        print(
            "Não foi possível carregar "
            "o data.json:",
            erro
        )

    return []


def salvar(posts):
    with open(
        ARQUIVO_SAIDA,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            posts,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


def chave_post(post):
    return (
        post.get("link")
        or post.get("url")
        or post.get("titulo", "").lower()
    )


def main():

    print("=" * 50)
    print("IPIRANGA 24H")
    print("COLETOR DE MATÉRIAS")
    print("=" * 50)

    print()
    print(
        "Acessando a página oficial "
        "'Todas as matérias'..."
    )

    html = baixar(
        TODAS_AS_MATERIAS
    )

    if not html:
        print(
            "Não foi possível acessar "
            "a página de matérias."
        )

        return

    urls = encontrar_materias(
        html
    )

    print(
        f"Matérias encontradas "
        f"diretamente: {len(urls)}"
    )

    # Também procura links na página
    # principal da Sala de Imprensa.
    sala_url = (
        "https://www.ipiranga.com.br/"
        "wps/portal/pt-br/ipiranga/"
        "a-ipiranga/institucional/"
        "sala-de-imprensa/"
    )

    print()
    print(
        "Verificando também a Sala "
        "de Imprensa..."
    )

    sala_html = baixar(
        sala_url
    )

    if sala_html:
        urls.update(
            encontrar_materias(
                sala_html
            )
        )

    print(
        f"Total de URLs de matérias: "
        f"{len(urls)}"
    )

    posts_novos = []

    print()
    print(
        "Baixando conteúdo das matérias..."
    )

    # Tenta até 150 matérias.
    urls = list(urls)[:150]

    for numero, url in enumerate(
        urls,
        start=1
    ):

        print(
            f"[{numero}/{len(urls)}] "
            f"{url}"
        )

        post = extrair_materia(
            url
        )

        if post:
            posts_novos.append(
                post
            )

    print()
    print(
        f"Matérias lidas com sucesso: "
        f"{len(posts_novos)}"
    )

    # Mantém as antigas que já estavam
    # no arquivo.
    antigas = carregar_existentes()

    todas = []

    for post in antigas:
        if isinstance(post, dict):
            todas.append(post)

    todas.extend(
        posts_novos
    )

    # Remove duplicadas.
    unicas = {}

    for post in todas:
        chave = chave_post(
            post
        )

        if chave:
            unicas[chave] = post

    resultado = list(
        unicas.values()
    )

    # Ordenação simples pela data.
    def data_ordem(post):
        valor = str(
            post.get(
                "data",
                ""
            )
        )

        numeros = re.sub(
            r"\D",
            "",
            valor
        )

        return numeros

    resultado.sort(
        key=data_ordem,
        reverse=True
    )

    # Limite do projeto.
    resultado = resultado[:130]

    # Recria IDs sequenciais.
    for numero, post in enumerate(
        resultado,
        start=1
    ):
        post["id"] = numero

        # Garante o campo link.
        if not post.get("link"):
            post["link"] = post.get(
                "url",
                ""
            )

        # Remove url antiga caso exista.
        post.pop(
            "url",
            None
        )

    salvar(
        resultado
    )

    print()
    print("=" * 50)
    print("ATUALIZAÇÃO CONCLUÍDA")
    print("=" * 50)
    print(
        f"Total no data.json: "
        f"{len(resultado)}"
    )


if __name__ == "__main__":
    main()
