// ========================================
// IPIRANGA 24H — FUNCIONAMENTO DO SITE
// ========================================

const postsContainer = document.getElementById("posts");

// ----------------------------------------
// CARREGAR PUBLICAÇÕES
// ----------------------------------------

async function carregarPosts() {
    postsContainer.innerHTML = `
        <div class="loading">
            Carregando informações...
        </div>
    `;

    try {
        const resposta = await fetch("data.json");

        if (!resposta.ok) {
            throw new Error("Não foi possível carregar as informações.");
        }

        const posts = await resposta.json();

        if (!posts || posts.length === 0) {
            postsContainer.innerHTML = `
                <div class="error">
                    Nenhuma publicação disponível no momento.
                </div>
            `;
            return;
        }

        // Mistura a ordem das publicações para que o feed
        // possa apresentar conteúdos diferentes ao atualizar.
        const postsMisturados = [...posts].sort(() => Math.random() - 0.5);

        postsContainer.innerHTML = "";

        postsMisturados.forEach(post => {
            criarPost(post);
        });

    } catch (erro) {

        console.error(erro);

        postsContainer.innerHTML = `
            <div class="error">
                Não foi possível carregar as informações agora.
                Tente atualizar a página.
            </div>
        `;
    }
}


// ----------------------------------------
// CRIAR UMA PUBLICAÇÃO
// ----------------------------------------

function criarPost(post) {

    const postElement = document.createElement("article");

    postElement.className = "post";

    const id = post.id;

    postElement.innerHTML = `

        ${post.imagem ? `
            <img
                class="post-image"
                src="${post.imagem}"
                alt="${escaparHTML(post.titulo)}"
                loading="lazy"
            >
        ` : ""}

        <div class="post-header">

            <div class="post-source">
                ${escaparHTML(post.fonte || "Ipiranga")}
            </div>

            <h2 class="post-title">
                ${escaparHTML(post.titulo)}
            </h2>

            <div class="post-date">
                ${formatarData(post.data)}
            </div>

        </div>

        <div class="post-content">

            <p class="post-description">
                ${escaparHTML(post.descricao || "")}
            </p>

        </div>

        <div class="post-actions">

            <button
                class="action-button like-button"
                onclick="curtirPost('${id}', this)"
            >
                ❤️ <span>0</span>
            </button>

            <button
                class="action-button"
                onclick="abrirComentarios('${id}')"
            >
                💬 <span>Comentar</span>
            </button>

            <button
                class="action-button"
                onclick="compartilharPost('${id}')"
            >
                🔗 <span>Compartilhar</span>
            </button>

            <button
                class="action-button"
                disabled
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
                >
                    Enviar
                </button>

            </div>

            <div id="comment-list-${id}">
            </div>

        </div>
    `;

    postsContainer.appendChild(postElement);

    carregarInteracoes(id);
}


// ----------------------------------------
// CURTIDA
// ----------------------------------------

function curtirPost(id, botao) {

    const chave = `like-${id}`;

    let curtido = localStorage.getItem(chave);

    const contador = botao.querySelector("span");

    let quantidade =
        parseInt(localStorage.getItem(`likes-${id}`)) || 0;

    if (curtido === "true") {

        curtido = false;

        quantidade = Math.max(0, quantidade - 1);

        localStorage.setItem(chave, "false");

        botao.classList.remove("liked");

    } else {

        curtido = true;

        quantidade++;

        localStorage.setItem(chave, "true");

        botao.classList.add("liked");
    }

    localStorage.setItem(`likes-${id}`, quantidade);

    contador.textContent = quantidade;
}


// ----------------------------------------
// COMENTÁRIOS
// ----------------------------------------

function abrirComentarios(id) {

    const area =
        document.getElementById(`comments-${id}`);

    area.classList.toggle("active");
}


function adicionarComentario(id) {

    const input =
        document.getElementById(`input-${id}`);

    const texto = input.value.trim();

    if (!texto) {
        return;
    }

    const chave = `comments-${id}`;

    let comentarios =
        JSON.parse(localStorage.getItem(chave)) || [];

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


function mostrarComentarios(id) {

    const lista =
        document.getElementById(`comment-list-${id}`);

    const comentarios =
        JSON.parse(
            localStorage.getItem(`comments-${id}`)
        ) || [];

    lista.innerHTML = "";

    comentarios.forEach(comentario => {

        const elemento =
            document.createElement("div");

        elemento.className = "comment";

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


// ----------------------------------------
// COMPARTILHAMENTO
// ----------------------------------------

async function compartilharPost(id) {

    const url =
        `${window.location.origin}${window.location.pathname}#post-${id}`;

    try {

        if (navigator.share) {

            await navigator.share({
                title: "Ipiranga 24h",
                text: "Confira esta informação no Ipiranga 24h.",
                url: url
            });

        } else {

            await navigator.clipboard.writeText(url);

            mostrarMensagem(
                "Link da publicação copiado!"
            );
        }

    } catch (erro) {

        console.log("Compartilhamento cancelado.");
    }
}


// ----------------------------------------
// MENSAGEM TEMPORÁRIA
// ----------------------------------------

function mostrarMensagem(texto) {

    let mensagem =
        document.querySelector(".share-message");

    if (!mensagem) {

        mensagem =
            document.createElement("div");

        mensagem.className =
            "share-message";

        document.body.appendChild(mensagem);
    }

    mensagem.textContent = texto;

    mensagem.classList.add("active");

    setTimeout(() => {
        mensagem.classList.remove("active");
    }, 2500);
}


// ----------------------------------------
// CARREGAR INTERAÇÕES SALVAS
// ----------------------------------------

function carregarInteracoes(id) {

    const botao =
        document.querySelector(
            `.like-button[onclick="curtirPost('${id}', this)"]`
        );

    if (!botao) return;

    const contador =
        botao.querySelector("span");

    const quantidade =
        parseInt(
            localStorage.getItem(`likes-${id}`)
        ) || 0;

    contador.textContent = quantidade;

    if (
        localStorage.getItem(`like-${id}`) === "true"
    ) {
        botao.classList.add("liked");
    }

    mostrarComentarios(id);
}


// ----------------------------------------
// DATA
// ----------------------------------------

function formatarData(data) {

    if (!data) {
        return "Data não informada";
    }

    const dataObj = new Date(data);

    if (isNaN(dataObj.getTime())) {
        return data;
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


// ----------------------------------------
// SEGURANÇA DO TEXTO
// ----------------------------------------

function escaparHTML(texto) {

    const div =
        document.createElement("div");

    div.textContent = texto;

    return div.innerHTML;
}


// ----------------------------------------
// INICIAR SITE
// ----------------------------------------

carregarPosts();
