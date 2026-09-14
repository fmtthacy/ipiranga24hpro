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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
}


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def chave_materia(item):
    titulo = normalizar(item.get("titulo", ""))
    data = normalizar(item.get("data", ""))
    return f"{titulo}|{data}"


def buscar_pagina(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    resposta.raise_for_status()
    return BeautifulSoup(resposta.text, "html.parser")


def extrair_descricao(url):
    try:
        soup = buscar_pagina(url)

        h1 = soup.find("h1")

        if not h1:
            return ""

        # Procura os parágrafos depois do título da matéria.
        candidatos = []

        for p in soup.find_all("p"):
            texto = p.get_text(" ", strip=True)

            if not texto:
                continue

            texto_normalizado = normalizar(texto)

            # Ignora textos genéricos do site.
            if "fique por dentro de todas as novidades de ipiranga" in texto_normalizado:
                continue

            if "sobre a ipiranga" in texto_normalizado:
                continue

            if "topicos da materia" in texto_normalizado:
                continue

            if len(texto) < 60:
                continue

            candidatos.append(texto)

        if candidatos:
            descricao = candidatos[0]

            # Evita descrições enormes.
            if len(descricao) > 350:
                descricao = descricao[:347].rsplit(" ", 1)[0] + "..."

            return descricao

    except Exception as erro:
        print(f"Não foi possível pegar a descrição de {url}: {erro}")

    return ""


def extrair_materias():
    soup = buscar_pagina(URL_MATERIAS)

    materias = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if "/materias/" not in href:
            continue

        if href.startswith("/"):
            href = "https://www.ipiranga.com.br" + href

        titulo = link.get_text(" ", strip=True)

        if not titulo:
            continue

        # Procura a data próxima ao link.
        bloco = link.parent

        data = ""

        if bloco:
            texto_bloco = bloco.get_text(" ", strip=True)

            datas = re.findall(
                r"\b\d{2}/\d{2}/\d{4}\b",
                texto_bloco
            )

            if datas:
                data = datas[0]

        # Se não encontrou no elemento pai, procura nos elementos próximos.
        if not data:
            anterior = link.find_previous(
                string=re.compile(r"\d{2}/\d{2}/\d{4}")
            )

            if anterior:
                encontrado = re.search(
                    r"\d{2}/\d{2}/\d{4}",
                    anterior
                )

                if encontrado:
                    data = encontrado.group(0)

        materias.append({
            "titulo": titulo,
            "data": data,
            "fonte": "Ipiranga",
            "link": href
        })

    # Remove links repetidos.
    resultado = []
    links_vistos = set()

    for materia in materias:
        if materia["link"] in links_vistos:
            continue

        links_vistos.add(materia["link"])
        resultado.append(materia)

    return resultado


def carregar_antigos():
    if not ARQUIVO.exists():
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return dados

    except Exception as erro:
        print(f"Erro ao ler data.json: {erro}")

    return []


def salvar(materias):
    # Junta antigas + novas.
    todas = []

    for materia in materias:
        todas.append(materia)

    # Remove duplicatas usando título + data.
    unicas = {}

    for item in todas:
        chave = chave_materia(item)

        if not chave or chave == "|":
            continue

        existente = unicas.get(chave)

        if existente is None:
            unicas[chave] = item
            continue

        # Se houver duas versões da mesma matéria,
        # prefere a que possui link /materias/.
        link_novo = item.get("link", "")
        link_antigo = existente.get("link", "")

        if "/materias/" in link_novo and "/materias/" not in link_antigo:
            unicas[chave] = item

    resultado = list(unicas.values())

    # Organiza da mais nova para a mais antiga.
    def data_sort(item):
        data = item.get("data", "")

        try:
            dia, mes, ano = data.split("/")
            return int(ano), int(mes), int(dia)
        except Exception:
            return 0, 0, 0

    resultado.sort(
        key=data_sort,
        reverse=True
    )

    # Garante IDs estáveis.
    for numero, item in enumerate(resultado, start=1):
        item["id"] = numero

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

    print(f"{len(resultado)} matérias salvas em data.json.")


def main():
    print("Iniciando atualização automática da Ipiranga...")

    antigos = carregar_antigos()

    print(f"Matérias antigas encontradas: {len(antigos)}")

    try:
        novas = extrair_materias()

        print(f"Matérias encontradas no site: {len(novas)}")

    except Exception as erro:
        print(f"Erro ao acessar a página da Ipiranga: {erro}")
        return

    materias_processadas = []

    # Primeiro mantém as antigas.
    for antiga in antigos:
        materias_processadas.append(antiga)

    # Depois adiciona/atualiza as encontradas.
    for nova in novas:
        descricao = extrair_descricao(nova["link"])

        nova["descricao"] = descricao or (
            "Confira a publicação oficial da Ipiranga."
        )

        materias_processadas.append(nova)

    salvar(materias_processadas)

    print("Atualização concluída.")


if __name__ == "__main__":
    main()
