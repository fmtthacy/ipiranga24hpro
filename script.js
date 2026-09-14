const postsContainer = document.getElementById("posts");

function escaparHTML(texto) {
  if (texto === undefined || texto === null) return "";

  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatarData(data) {
  if (!data) return "";

  if (/^\d{2}\/\d{2}\/\d{4}$/.test(data)) {
    return data;
  }

  const dataObj = new Date(data);

  if (isNaN(dataObj.getTime())) {
    return data;
  }

  return dataObj.toLocaleDateString("pt-BR");
}

function embaralhar(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

function obterId(post, indice) {
  return post.id || `post-${indice}`;
}

function criarPost(post, indice) {
  const id = obterId(post, indice);

  const curtidas =
    Number(localStorage.getItem(`curtidas_${id}`)) || 0;

  const visualizacoes =
    Number(localStorage.getItem(`visualizacoes_${id}`)) || 0;

  const curtido =
    localStorage.getItem(`curtiu_${id}`) === "true";

  const artigo = document.createElement("article");
  artigo.className = "post";
  artigo.dataset.id = id;

  artigo.innerHTML = `
    <div class="post-topo">
      <div>
        <span class="post-fonte">
          ${escaparHTML(post.fonte || "Ipiranga")}
        </span>

        <span class="post-data">
          ${escaparHTML(formatarData(post.data))}
        </span>
      </div>

      <span class="post-status">INFORMAÇÃO</span>
    </div>

    <h2>${escaparHTML(post.titulo)}</h2>

    ${
      post.imagem
        ? `<img 
             src="${escaparHTML(post.imagem)}" 
             alt="${escaparHTML(post.titulo)}"
             loading="lazy"
           >`
        : ""
    }

    <p class="post-descricao">
      ${escaparHTML(post.descricao)}
    </p>

    <div class="post-acoes">
      <button 
        class="acao-btn ${curtido ? "curtido" : ""}" 
        onclick="curtirPost('${id}')"
      >
        ❤️ <span class="numero-curtidas">${curtidas}</span>
        <span class="texto-acao">Curtir</span>
      </button>

      <button 
        class="acao-btn"
        onclick="abrirComentarios('${id}')"
      >
        💬 <span>Comentar</span>
      </button>

      <button 
        class="acao-btn"
        onclick="compartilharPost('${id}')"
      >
        🔗 <span>Compartilhar</span>
      </button>

      <span class="visualizacoes">
        👁️ ${visualizacoes}
      </span>
    </div>

    <div 
      class="comentarios" 
      id="comentarios-${id}"
      style="display: none;"
    >
      <h3>Comentários</h3>

      <textarea
        id="comentario-texto-${id}"
        placeholder="Escreva um comentário..."
        maxlength="500"
      ></textarea>

      <button onclick="adicionarComentario('${id}')">
        Publicar comentário
      </button>

      <div 
        class="lista-comentarios"
        id="lista-comentarios-${id}"
      ></div>
    </div>

    <div class="post-rodape">
      ${
        post.link
          ? `
            <a 
              href="${escaparHTML(post.link)}"
              target="_blank"
              rel="noopener noreferrer"
            >
              Ver publicação original →
            </a>
          `
          : ""
      }
    </div>
  `;

  postsContainer.appendChild(artigo);

  registrarVisualizacao(id);
  carregarComentarios(id);
}

function registrarVisualizacao(id) {
  const chave = `visualizacoes_${id}`;

  let visualizacoes =
    Number(localStorage.getItem(chave)) || 0;

  if (!sessionStorage.getItem(`visualizado_${id}`)) {
    visualizacoes++;

    localStorage.setItem(
      chave,
      visualizacoes
    );

    sessionStorage.setItem(
      `visualizado_${id}`,
      "true"
    );
  }

  const post = document.querySelector(
    `.post[data-id="${id}"] .visualizacoes`
  );

  if (post) {
    post.textContent = `👁️ ${visualizacoes}`;
  }
}

function curtirPost(id) {
  const chaveCurtidas = `curtidas_${id}`;
  const chaveUsuario = `curtiu_${id}`;

  let curtidas =
    Number(localStorage.getItem(chaveCurtidas)) || 0;

  const jaCurtiu =
    localStorage.getItem(chaveUsuario) === "true";

  if (jaCurtiu) {
    curtidas = Math.max(0, curtidas - 1);
    localStorage.setItem(chaveUsuario, "false");
  } else {
    curtidas++;
    localStorage.setItem(chaveUsuario, "true");
  }

  localStorage.setItem(
    chaveCurtidas,
    curtidas
  );

  const botao = document.querySelector(
    `.post[data-id="${id}"] .acao-btn`
  );

  if (botao) {
    botao.classList.toggle(
      "curtido",
      !jaCurtiu
    );

    const numero =
      botao.querySelector(".numero-curtidas");

    if (numero) {
      numero.textContent = curtidas;
    }
  }
}

function abrirComentarios(id) {
  const area = document.getElementById(
    `comentarios-${id}`
  );

  if (!area) return;

  const aberto = area.style.display === "block";

  area.style.display =
    aberto ? "none" : "block";

  if (!aberto) {
    const campo = document.getElementById(
      `comentario-texto-${id}`
    );

    if (campo) {
      setTimeout(() => campo.focus(), 100);
    }
  }
}

function adicionarComentario(id) {
  const campo = document.getElementById(
    `comentario-texto-${id}`
  );

  if (!campo) return;

  const texto = campo.value.trim();

  if (!texto) {
    alert("Digite um comentário antes de publicar.");
    return;
  }

  const chave = `comentarios_${id}`;

  let comentarios =
    JSON.parse(localStorage.getItem(chave)) || [];

  comentarios.push({
    texto: texto,
    data: new Date().toLocaleString("pt-BR")
  });

  localStorage.setItem(
    chave,
    JSON.stringify(comentarios)
  );

  campo.value = "";

  carregarComentarios(id);
}

function carregarComentarios(id) {
  const lista = document.getElementById(
    `lista-comentarios-${id}`
  );

  if (!lista) return;

  const comentarios =
    JSON.parse(
      localStorage.getItem(`comentarios_${id}`)
    ) || [];

  if (comentarios.length === 0) {
    lista.innerHTML =
      `<p class="sem-comentarios">Nenhum comentário ainda.</p>`;

    return;
  }

  lista.innerHTML = comentarios
    .map(
      comentario => `
        <div class="comentario">
          <strong>Visitante</strong>
          <small>${escaparHTML(comentario.data)}</small>
          <p>${escaparHTML(comentario.texto)}</p>
        </div>
      `
    )
    .join("");
}

async function compartilharPost(id) {
  const artigo = document.querySelector(
    `.post[data-id="${id}"]`
  );

  if (!artigo) return;

  const titulo =
    artigo.querySelector("h2")?.textContent ||
    "Ipiranga 24h";

  const url =
    artigo.querySelector(".post-rodape a")?.href ||
    window.location.href;

  if (navigator.share) {
    try {
      await navigator.share({
        title: titulo,
        text: `Confira esta informação no Ipiranga 24h: ${titulo}`,
        url: url
      });

      return;
    } catch (erro) {
      // Usuário cancelou o compartilhamento.
    }
  }

  try {
    await navigator.clipboard.writeText(url);

    alert("Link copiado para a área de transferência!");
  } catch (erro) {
    prompt("Copie o link abaixo:", url);
  }
}

async function carregarPosts() {
  if (!postsContainer) return;

  postsContainer.innerHTML = `
    <div class="carregando">
      Carregando informações...
    </div>
  `;

  try {
    const resposta = await fetch(
      `data.json?v=${Date.now()}`
    );

    if (!resposta.ok) {
      throw new Error("Não foi possível carregar o data.json.");
    }

    const posts = await resposta.json();

    if (!Array.isArray(posts) || posts.length === 0) {
      postsContainer.innerHTML = `
        <div class="estado-vazio">
          <h2>Nenhuma informação encontrada</h2>
          <p>Volte mais tarde para conferir novas publicações.</p>
        </div>
      `;

      return;
    }

    postsContainer.innerHTML = "";

    const postsOrganizados = embaralhar(posts);

    postsOrganizados.forEach((post, indice) => {
      criarPost(post, indice);
    });

  } catch (erro) {
    console.error(erro);

    postsContainer.innerHTML = `
      <div class="erro-posts">
        <h2>Não foi possível carregar as informações</h2>
        <p>
          Tente atualizar a página novamente.
        </p>

        <button onclick="carregarPosts()">
          Tentar novamente
        </button>
      </div>
    `;
  }
}

carregarPosts();
