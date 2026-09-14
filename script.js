// ========================================
// IPIRANGA 24H
// SCRIPT PRINCIPAL
// ========================================

const postsContainer = document.getElementById("posts");


// ========================================
// CARREGAR PUBLICAÇÕES
// ========================================

async function carregarPosts() {

    if (!postsContainer) return;

    postsContainer.innerHTML = `
        <div class="loading">
            Carregando informações...
        </div>
    `;

    try {

        const resposta = await fetch("data.json");

        if (!resposta.ok) {
            throw new Error("Erro ao carregar data.json");
        }

        const posts = await resposta.json();

        if (!Array.isArray(posts) || posts.length === 0) {

            postsContainer.innerHTML = `
                <div class="error">
                    Nenhuma publicação disponível no momento.
                </div>
            `;

            return;
        }

        postsContainer.innerHTML = "";

        // Mantém as publicações em ordem aleatória
        const publicacoes = [...posts];

        publicacoes.sort(() => Math.random() - 0.5);

        publicacoes.forEach((post, index) => {

            // Garante que toda publicação tenha um ID
            if (!post.id) {
                post.id = index + 1;
            }

            criarPost(post);

        });

    } catch (erro) {

        console.error(erro);

        postsContainer.innerHTML = `
            <div class="error">
                Não foi possível carregar as informações.
                Tente atualizar a página.
            </div>
        `;
    }
}


// ========================================
// CRIAR PUBLICAÇÃO
// ========================================

function criarPost(post) {

    const id = String(post.id);

    const artigo = document.createElement("article");

    artigo.className = "post";

    artigo.id = `post-${id}`;


    // ====================================
    // IMAGEM
    // ====================================

    const imagem = post.imagem
        ? `
            <img
                class="post-image"
                src="${escaparHTML(post.imagem)}"
                alt="${escaparHTML(post.titulo || "Publicação Ipiranga")}"
                loading="lazy"
            >
        `
        : "";


    // ====================================
    // LINK DA PUBLICAÇÃO
    // ====================================

    const link = post.link
        ? `
            <a
                class="post-link"
                href="${escaparHTML(post.link)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Ver publicação original
            </a>
        `
        : "";


    // ====================================
    // HTML DO POST
    // ====================================

    artigo.innerHTML = `

        ${imagem}

        <div class="post-header">

            <div class="post-source">
                ${escaparHTML(post.fonte || "Ipiranga")}
            </div>

            <h2 class="post-title">
                ${escaparHTML(post.titulo || "Sem título")}
            </h2>

            <div class="post-date">
                ${formatarData(post.data)}
            </div>

        </div>


        <div class="post-content">

            <p class="post-description">
                ${escaparHTML(post.descricao || "")}
            </p>

            ${link}

        </div>


        <div class="post-actions">

            <button
                class="action-button like-button"
                onclick="curtirPost('${id}', this)"
                type="button"
            >
                ❤️ <span>0</span>
            </button>


            <button
                class="action-button"
                onclick="abrirComentarios('${id}')"
                type="button"
            >
                💬 <span>Comentar</span>
            </button>


            <button
                class="action-button"
                onclick="compartilharPost('${id}')"
                type="button"
            >
                🔗 <span>Compartilhar</span>
            </button>


            <button
                class="action-button view-button"
                disabled
                type="button"
            >
                👁️ <span>0</span>
            </button>

        </div>


        <div
            class="comments"
            id="comments-${id}"
        >

            <div class="comment-form">

                <input
                    class="comment-input"
                    id="input-${id}"
                    type="text"
                    maxlength="300"
                    placeholder="Escreva um comentário..."
                >


                <button
                    class="comment-button"
                    onclick="adicionarComentario('${id}')"
                    type="button"
                >
                    Enviar
                </button>

            </div>


            <div id="comment-list-${id}">
            </div>

        </div>
    `;


    postsContainer.appendChild(artigo);


    // Carrega curtidas e comentários salvos
    carregarInteracoes(id);


    // Registra visualização
    registrarVisualizacao(id);
}


// ========================================
// CURTIR PUBLICAÇÃO
// ========================================

function curtirPost(id, botao) {

    const chaveCurtida =
        `ipiranga-like-${id}`;

    const chaveQuantidade =
        `ipiranga-likes-${id}`;


    let quantidade =
        Number(
            localStorage.getItem(chaveQuantidade)
        ) || 0;


    const jaCurtiu =
        localStorage.getItem(chaveCurtida) === "true";


    if (jaCurtiu) {

        quantidade =
            Math.max(0, quantidade - 1);


        localStorage.setItem(
            chaveCurtida,
            "false"
        );


        botao.classList.remove("liked");

    } else {

        quantidade++;


        localStorage.setItem(
            chaveCurtida,
            "true"
        );


        botao.classList.add("liked");
    }


    localStorage.setItem(
        chaveQuantidade,
        quantidade
    );


    const contador =
        botao.querySelector("span");


    if (contador) {
        contador.textContent = quantidade;
    }
}


// ========================================
// ABRIR COMENTÁRIOS
// ========================================

function abrirComentarios(id) {

    const comentarios =
        document.getElementById(
            `comments-${id}`
        );


    if (!comentarios) return;


    comentarios.classList.toggle("active");


    if (comentarios.classList.contains("active")) {

        const input =
            document.getElementById(
                `input-${id}`
            );


        if (input) {
            input.focus();
        }
    }
}


// ========================================
// ADICIONAR COMENTÁRIO
// ========================================

function adicionarComentario(id) {

    const input =
        document.getElementById(
            `input-${id}`
        );


    if (!input) return;


    const texto =
        input.value.trim();


    if (!texto) return;


    const chave =
        `ipiranga-comments-${id}`;


    let comentarios =
        JSON.parse(
            localStorage.getItem(chave)
        ) || [];


    comentarios.push({

        nome: "Visitante",

        texto: texto,

        data: new Date().toISOString()

    });


    localStorage.setItem(
        chave,
        JSON.stringify(comentarios)
    );


    input.value = "";


    mostrarComentarios(id);
}


// ========================================
// MOSTRAR COMENTÁRIOS
// ========================================

function mostrarComentarios(id) {

    const lista =
        document.getElementById(
            `comment-list-${id}`
        );


    if (!lista) return;


    const comentarios =
        JSON.parse(
            localStorage.getItem(
                `ipiranga-comments-${id}`
            )
        ) || [];


    lista.innerHTML = "";


    comentarios.forEach(comentario => {

        const elemento =
            document.createElement("div");


        elemento.className =
            "comment";


        elemento.innerHTML = `

            <strong>
                ${escaparHTML(comentario.nome)}
            </strong>

            <br>

            ${escaparHTML(comentario.texto)}

        `;


        lista.appendChild(elemento);
    });
}


// ========================================
// REGISTRAR VISUALIZAÇÃO
// ========================================

function registrarVisualizacao(id) {

    const chave =
        `ipiranga-views-${id}`;


    let visualizacoes =
        Number(
            localStorage.getItem(chave)
        ) || 0;


    visualizacoes++;


    localStorage.setItem(
        chave,
        visualizacoes
    );


    const botao =
        document.querySelector(
            `#post-${id} .view-button span`
        );


    if (botao) {

        botao.textContent =
            visualizacoes;
    }
}


// ========================================
// COMPARTILHAR
// ========================================

async function compartilharPost(id) {

    const url =
        `${window.location.href.split("#")[0]}#post-${id}`;


    try {

        if (navigator.share) {

            await navigator.share({

                title: "Ipiranga 24h",

                text:
                    "Confira esta publicação no Ipiranga 24h.",

                url: url

            });

        } else {

            await navigator.clipboard.writeText(url);


            mostrarMensagem(
                "Link copiado!"
            );
        }

    } catch (erro) {

        console.log(
            "Compartilhamento cancelado."
        );
    }
}


// ========================================
// MOSTRAR MENSAGEM
// ========================================

function mostrarMensagem(texto) {

    let mensagem =
        document.querySelector(
            ".share-message"
        );


    if (!mensagem) {

        mensagem =
            document.createElement("div");


        mensagem.className =
            "share-message";


        document.body.appendChild(
            mensagem
        );
    }


    mensagem.textContent =
        texto;


    mensagem.classList.add(
        "active"
    );


    setTimeout(() => {

        mensagem.classList.remove(
            "active"
        );

    }, 2500);
}


// ========================================
// CARREGAR INTERAÇÕES
// ========================================

function carregarInteracoes(id) {

    const botao =
        document.querySelector(
            `#post-${id} .like-button`
        );


    if (botao) {

        const quantidade =
            Number(
                localStorage.getItem(
                    `ipiranga-likes-${id}`
                )
            ) || 0;


        const contador =
            botao.querySelector("span");


        if (contador) {

            contador.textContent =
                quantidade;
        }


        if (
            localStorage.getItem(
                `ipiranga-like-${id}`
            ) === "true"
        ) {

            botao.classList.add(
                "liked"
            );
        }
    }


    mostrarComentarios(id);
}


// ========================================
// FORMATAR DATA
// ========================================

function formatarData(data) {

    if (!data) {
        return "Data não informada";
    }


    // Aceita diretamente DD/MM/AAAA
    if (
        /^\d{2}\/\d{2}\/\d{4}$/.test(
            String(data)
        )
    ) {

        return escaparHTML(data);
    }


    // Aceita AAAA-MM-DD
    if (
        /^\d{4}-\d{2}-\d{2}$/.test(
            String(data)
        )
    ) {

        const partes =
            String(data).split("-");


        return `
            ${partes[2]}/${partes[1]}/${partes[0]}
        `;
    }


    // Tenta interpretar outros formatos
    const dataObj =
        new Date(data);


    if (
        isNaN(
            dataObj.getTime()
        )
    ) {

        return escaparHTML(data);
    }


    return dataObj.toLocaleDateString(
        "pt-BR",
        {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        }
    );
}


// ========================================
// PROTEÇÃO CONTRA HTML
// ========================================

function escaparHTML(texto) {

    const div =
        document.createElement("div");


    div.textContent =
        String(texto);


    return div.innerHTML;
}


// ========================================
// INICIAR
// ========================================

carregarPosts();
