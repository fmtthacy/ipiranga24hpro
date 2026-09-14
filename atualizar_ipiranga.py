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
    "User-Agent": "Mozilla/5.0"
}


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto).strip().lower()


def buscar(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    resposta.raise_for_status()
    return BeautifulSoup(resposta.text, "html.parser")


def descricao_materia(url):
    try:
        soup = buscar(url)

        for p in soup.find_all("p"):
            texto = p.get_text(" ", strip=True)

            if len(texto) < 60:
                continue

            normalizado = normalizar(texto)

            if "fique por dentro de todas as novidades" in normalizado:
                continue

            if "sobre a ipiranga" in normalizado:
                continue

            if "topicos da materia" in normalizado:
                continue

            if len(texto) > 350:
                texto = texto[:347].rsplit(" ", 1)[0] + "..."

            return texto

    except Exception as erro:
        print("Erro ao buscar descrição:", erro)

    return "Confira a publicação oficial da Ipiranga."


def encontrar_titulo_real(link):
    """
    Procura o título verdadeiro da matéria.
    Nunca aceita textos como '10 set' ou '03 set'.
    """

    # Procura primeiro nos títulos da página.
    for elemento in link.find_all_previous(
        ["h1", "h2", "h3", "h4"],
        limit=5
    ):
        texto = elemento.get_text(" ", strip=True)

        if len(texto) > 20:
            return texto

    # Procura dentro do bloco do card.
    atual = link.parent

    for _ in range(5):
        if atual is None:
            break

        for elemento in atual.find_all(
            ["h1", "h2", "h3", "h4"]
        ):
            texto = elemento.get_text(
                " ",
                strip=True
            )

            if len(texto) > 20:
                return texto

        atual = atual.parent

    return ""


def encontrar_data(link):
    """
    Procura uma data completa no card da matéria.
    """

    atual = link.parent

    for _ in range(5):
        if atual is None:
            break

        texto = atual.get_text(
            " ",
            strip=True
        )

        encontrado = re.search(
            r"\b(\d{2}/\d{2}/\d{4})\b",
            texto
        )

        if encontrado:
            return encontrado.group(1)

        atual = atual.parent

    return ""


def extrair_materias():
    soup = buscar(URL_MATERIAS)

    materias = []
    links_vistos = set()

    for link in soup.find_all("a", href=True):

        href = link["href"].strip()

        if "/materias/" not in href:
            continue

        if href.startswith("/"):
            href = "https://www.ipiranga.com.br" + href

        if href in links_vistos:
            continue

        links_vistos.add(href)

        titulo = encontrar_titulo_real(link)

        # Ignora links que são apenas a data.
        if not titulo or len(titulo) < 20:
            continue

        if re.fullmatch(
            r"\d{1,2}\s+"
            r"(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
            titulo.lower()
        ):
            continue

        data = encontrar_data(link)

        materias.append({
            "titulo": titulo,
            "descricao": descricao_materia(href),
            "data": data,
            "fonte": "Ipiranga",
            "link": href
        })

    return materias


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
        print("Erro ao ler data.json:", erro)

    return []


def chave_materia(item):
    """
    A mesma matéria será identificada pelo link oficial.
    Isso impede duplicações.
    """

    link = item.get("link", "").strip()

    if "/materias/" in link:
        return "link:" + normalizar(link)

    titulo = normalizar(item.get("titulo", ""))
    data = normalizar(item.get("data", ""))

    return f"{titulo}|{data}"


def limpar_antigos(materias):
    """
    Remove registros errados que já foram criados
    pelas versões anteriores do script.
    """

    resultado = []

    for item in materias:

        titulo = item.get("titulo", "").strip()

        # Remove títulos como:
        # 10 set
        # 03 set
        # 01 set
        # 21 ago
        if re.fullmatch(
            r"\d{1,2}\s+"
            r"(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
            titulo.lower()
        ):
            continue

        if len(titulo) < 20:
            continue

        resultado.append(item)

    return resultado


def unir_materias(antigas, novas):

    antigas = limpar_antigos(antigas)

    materias = {}

    # Primeiro coloca as antigas.
    for item in antigas:

        chave = chave_materia(item)

        if chave not in materias:
            materias[chave] = item

    # Depois coloca as novas.
    # Se já existir, a versão nova substitui a antiga.
    for item in novas:

        chave = chave_materia(item)

        materias[chave] = item

    resultado = list(materias.values())

    # -------------------------------------------------
    # Segunda proteção contra duplicatas:
    # título + data.
    # -------------------------------------------------

    finais = {}

    for item in resultado:

        titulo = normalizar(
            item.get("titulo", "")
        )

        data = normalizar(
            item.get("data", "")
        )

        identificador = f"{titulo}|{data}"

        existente = finais.get(identificador)

        if existente is None:
            finais[identificador] = item
            continue

        # Prefere o link oficial da matéria.
        link_novo = item.get("link", "")
        link_existente = existente.get("link", "")

        if (
            "/materias/" in link_novo
            and "/materias/" not in link_existente
        ):
            finais[identificador] = item

    resultado = list(finais.values())

    # Ordena da mais nova para a mais antiga.
    def data_ordem(item):

        data = item.get("data", "")

        try:
            dia, mes, ano = data.split("/")

            return (
                int(ano),
                int(mes),
                int(dia)
            )

        except Exception:
            return (0, 0, 0)

    resultado.sort(
        key=data_ordem,
        reverse=True
    )

    # IDs organizados.
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

    print("===================================")
    print(" ATUALIZAÇÃO AUTOMÁTICA IPIRANGA")
    print("===================================")

    antigas = carregar_antigos()

    print(
        f"Matérias existentes: {len(antigas)}"
    )

    try:
        novas = extrair_materias()

        print(
            f"Matérias encontradas no site: {len(novas)}"
        )

    except Exception as erro:

        print(
            "Erro ao acessar o site da Ipiranga:",
            erro
        )

        return

    resultado = unir_materias(
        antigas,
        novas
    )

    salvar(resultado)

    print(
        f"Total final: {len(resultado)}"
    )

    print("Atualização concluída!")


if __name__ == "__main__":
    main()
