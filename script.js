const postsContainer = document.getElementById("posts");

const QUANTIDADE_DE_POSTS = 4;
const CHAVE_ULTIMOS_POSTS = "ipiranga24h_ultimos_posts";

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


/*
  Embaralha as matérias.
  Assim, a ordem muda sempre que a página é recarregada.
*/
function embaralhar(array) {
  const copia = [...array];

  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));

    [copia[i], copia[j]] = [copia[j], copia[i]];
  }

  return copia;
}


/*
  Cria uma identificação estável para cada matéria.
*/
function obterId(post, indice) {
  if (post.id !== undefined && post.id !== null) {
    return String(post.id);
  }

  if (post.link) {
    return post.link;
  }

  return `post-${indice}`;
}


/*
  Pega os IDs que apareceram no último carregamento.
*/
function obterUltimosPosts() {
  try {
    const dados = JSON.parse(
      sessionStorage.getItem(CHAVE_ULTIMOS_POSTS)
    );

    if (Array.isArray(dados)) {
      return dados;
    }

  } catch (erro) {
    console.error("Erro ao ler últimos posts:", erro);
  }

  return [];
}


/*
  Salva quais matérias foram mostradas.
  
  Usamos sessionStorage porque queremos controlar
  as matérias durante a sessão atual do site.
*/
function salvarUltimosPosts(posts) {
  try {
    const ids = posts.map((post, indice) =>
      obterId(post, indice)
    );

    sessionStorage.setItem(
      CHAVE_ULTIMOS_POSTS,
      JSON.stringify(ids)
    );

  } catch (erro) {
    console.error("Erro ao salvar últimos posts:", erro);
  }
}


/*
  Escolhe as matérias que aparecerão na tela.
  
  A cada recarregamento:
  - embaralha todas as matérias;
  - tenta evitar as que apareceram anteriormente;
  - escolhe a quantidade definida em QUANTIDADE_DE_POSTS.
*/
function escolherPosts(posts) {
  if (!Array.isArray(posts)) {
    return [];
  }

  if (posts.length <= QUANTIDADE_DE_POSTS) {
    const escolhidos = embaralhar(posts);

    salvarUltimosPosts(escolhidos);

    return escolhidos;
  }

  const ultimosIds = obterUltimosPosts();

  const novosPosts = posts.filter(
    (post, indice) =>
      !ultimosIds.includes(
        obterId(post, indice)
      )
  );

  let escolhidos;

  /*
    Se existirem matérias que não apareceram antes,
    damos preferência para elas.
  */
  if (novosPosts.length >= QUANTIDADE_DE_POSTS) {

    escolhidos = embaralhar(novosPosts)
      .slice(0, QUANTIDADE_DE_POSTS);

  } else {

    /*
      Se não houver matérias novas suficientes,
      completa com outras matérias aleatórias.
    */

    const restantes = posts.filter(
      (post, indice) =>
        !novosPosts.includes(post)
    );

    escolhidos = [
      ...embaralhar(novosPosts),
      ...embaralhar(restantes)
    ].slice(
      0,
      QUANTIDADE_DE_POSTS
    );
  }

  salvarUltimosPosts(escolhidos);

  return escolhidos;
}


function criarPost(post, indice) {
  const id = obterId(post, indice);

  const curtidas =
    Number(
      localStorage.getItem(
        `curtidas_${id}`
      )
    ) || 0;

  const visualizacoes =
    Number(
      localStorage.getItem(
        `visualizacoes_${id}`
      )
    ) || 0;

  const curtido =
    localStorage.getItem(
      `curtiu_${id}`
    ) === "true";


  const artigo = document.createElement("article");

  artigo.className = "post";

  artigo.dataset.id = id;


  artigo.innerHTML = `
    <div class="post-topo">

      <div>
        <span class="post-fonte">
          ${escaparHTML(
            post.fonte || "Ipiranga"
          )}
        </span>

        <span class="post-data">
          ${escaparHTML(
            formatarData(post.data)
          )}
        </span>
      </div>

      <span class="post-status">
        INFORMAÇÃO
      </span>

    </div>


    <h2>
      ${escaparHTML(
        post.titulo || "Sem título"
      )}
    </h2>


    ${
      post.imagem
        ? `
          <img
            src="${escaparHTML(post.imagem)}"
            alt="${escaparHTML(post.titulo)}"
            loading="lazy"
          >
        `
        : ""
    }


    <p class="post-descricao">
      ${escaparHTML(
        post.descricao || ""
      )}
    </p>


    <div class="post-acoes">

      <button
        class="acao-btn ${curtido ? "curtido" : ""}"
        onclick="curtirPost('${escaparHTML(id)}')"
      >
        ❤️
        <span class="numero-curtidas">
          ${curtidas}
        </span>

        <span class="texto-acao">
          Curtir
        </span>
      </button>


      <button
        class="acao-btn"
        onclick="abrirComentarios('${escaparHTML(id)}')"
      >
        💬
        <span>
          Comentar
        </span>
      </button>


      <button
        class="acao-btn"
        onclick="compartilharPost('${escaparHTML(id)}')"
      >
        🔗
        <span>
          Compartilhar
        </span>
      </button>


      <span class="visualizacoes">
        👁️ ${visualizacoes}
      </span>

    </div>


    <div
      class="comentarios"
      id="comentarios-${escaparHTML(id)}"
      style="display: none;"
    >

      <h3>
        Comentários
      </h3>


      <textarea
        id="comentario-texto-${escaparHTML(id)}"
        placeholder="Escreva um comentário..."
        maxlength="500"
      ></textarea>


      <button
        onclick="adicionarComentario('${escaparHTML(id)}')"
      >
        Publicar comentário
      </button>


      <div
        class="lista-comentarios"
        id="lista-comentarios-${escaparHTML(id)}"
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


  postsContainer.appendChild(
    artigo
  );


  registrarVisualizacao(id);

  carregarComentarios(id);
}


/*
  Registra uma visualização por sessão.
*/
function registrarVisualizacao(id) {

  const chave =
    `visualizacoes_${id}`;

  let visualizacoes =
    Number(
      localStorage.getItem(chave)
    ) || 0;


  if (
    !sessionStorage.getItem(
      `visualizado_${id}`
    )
  ) {

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


  const post =
    document.querySelector(
      `.post[data-id="${CSS.escape(id)}"] .visualizacoes`
    );


  if (post) {
    post.textContent =
      `👁️ ${visualizacoes}`;
  }
}


/*
  Curtidas.
*/
function curtirPost(id) {

  const chaveCurtidas =
    `curtidas_${id}`;

  const chaveUsuario =
    `curtiu_${id}`;


  let curtidas =
    Number(
      localStorage.getItem(
        chaveCurtidas
      )
    ) || 0;


  const jaCurtiu =
    localStorage.getItem(
      chaveUsuario
    ) === "true";


  if (jaCurtiu) {

    curtidas =
      Math.max(
        0,
        curtidas - 1
      );

    localStorage.setItem(
      chaveUsuario,
      "false"
    );

  } else {

    curtidas++;

    localStorage.setItem(
      chaveUsuario,
      "true"
    );
  }


  localStorage.setItem(
    chaveCurtidas,
    curtidas
  );


  const artigo =
    document.querySelector(
      `.post[data-id="${CSS.escape(id)}"]`
    );


  if (!artigo) return;


  const botao =
    artigo.querySelector(
      ".acao-btn"
    );


  if (botao) {

    botao.classList.toggle(
      "curtido",
      !jaCurtiu
    );


    const numero =
      botao.querySelector(
        ".numero-curtidas"
      );


    if (numero) {
      numero.textContent =
        curtidas;
    }
  }
}


/*
  Abre ou fecha os comentários.
*/
function abrirComentarios(id) {

  const area =
    document.getElementById(
      `comentarios-${id}`
    );


  if (!area) return;


  const aberto =
    area.style.display === "block";


  area.style.display =
    aberto
      ? "none"
      : "block";


  if (!aberto) {

    const campo =
      document.getElementById(
        `comentario-texto-${id}`
      );


    if (campo) {

      setTimeout(
        () => campo.focus(),
        100
      );
    }
  }
}


/*
  Adiciona comentário.
*/
function adicionarComentario(id) {

  const campo =
    document.getElementById(
      `comentario-texto-${id}`
    );


  if (!campo) return;


  const texto =
    campo.value.trim();


  if (!texto) {

    alert(
      "Digite um comentário antes de publicar."
    );

    return;
  }


  const chave =
    `comentarios_${id}`;


  let comentarios;


  try {

    comentarios =
      JSON.parse(
        localStorage.getItem(
          chave
        )
      ) || [];

  } catch (erro) {

    comentarios = [];
  }


  comentarios.push({

    texto: texto,

    data:
      new Date().toLocaleString(
        "pt-BR"
      )

  });


  localStorage.setItem(
    chave,
    JSON.stringify(
      comentarios
    )
  );


  campo.value = "";


  carregarComentarios(id);
}


/*
  Carrega comentários do post.
*/
function carregarComentarios(id) {

  const lista =
    document.getElementById(
      `lista-comentarios-${id}`
    );


  if (!lista) return;


  let comentarios;


  try {

    comentarios =
      JSON.parse(
        localStorage.getItem(
          `comentarios_${id}`
        )
      ) || [];

  } catch (erro) {

    comentarios = [];
  }


  if (
    comentarios.length === 0
  ) {

    lista.innerHTML =
      `<p class="sem-comentarios">
        Nenhum comentário ainda.
      </p>`;

    return;
  }


  lista.innerHTML =
    comentarios
      .map(
        comentario => `
          <div class="comentario">

            <strong>
              Visitante
            </strong>

            <small>
              ${escaparHTML(
                comentario.data
              )}
            </small>

            <p>
              ${escaparHTML(
                comentario.texto
              )}
            </p>

          </div>
        `
      )
      .join("");
}


/*
  Compartilhamento.
*/
async function compartilharPost(id) {

  const artigo =
    document.querySelector(
      `.post[data-id="${CSS.escape(id)}"]`
    );


  if (!artigo) return;


  const titulo =
    artigo.querySelector(
      "h2"
    )?.textContent ||
    "Ipiranga 24h";


  const linkOriginal =
    artigo.querySelector(
      ".post-rodape a"
    );


  const url =
    linkOriginal?.href ||
    window.location.href;


  if (navigator.share) {

    try {

      await navigator.share({

        title: titulo,

        text:
          `Confira esta informação no Ipiranga 24h: ${titulo}`,

        url: url

      });

      return;

    } catch (erro) {

      /*
        O usuário pode ter cancelado
        o compartilhamento.
      */
    }
  }


  try {

    await navigator.clipboard.writeText(
      url
    );

    alert(
      "Link copiado para a área de transferência!"
    );

  } catch (erro) {

    prompt(
      "Copie o link abaixo:",
      url
    );
  }
}


/*
  Carrega as matérias do data.json.
*/
async function carregarPosts() {

  if (!postsContainer) {
    return;
  }


  postsContainer.innerHTML = `
    <div class="carregando">
      Carregando informações...
    </div>
  `;


  try {

    const resposta =
      await fetch(
        `data.json?v=${Date.now()}`
      );


    if (!resposta.ok) {

      throw new Error(
        "Não foi possível carregar o data.json."
      );
    }


    const posts =
      await resposta.json();


    if (
      !Array.isArray(posts) ||
      posts.length === 0
    ) {

      postsContainer.innerHTML = `
        <div class="estado-vazio">

          <h2>
            Nenhuma informação encontrada
          </h2>

          <p>
            Volte mais tarde para conferir
            novas publicações.
          </p>

        </div>
      `;

      return;
    }


    /*
      AQUI está a parte que faz a mudança
      das informações a cada recarregamento.
    */
    const postsSelecionados =
      escolherPosts(posts);


    postsContainer.innerHTML = "";


    postsSelecionados.forEach(
      (post, indice) => {

        criarPost(
          post,
          indice
        );

      }
    );


  } catch (erro) {

    console.error(
      erro
    );


    postsContainer.innerHTML = `
      <div class="erro-posts">

        <h2>
          Não foi possível carregar
          as informações
        </h2>

        <p>
          Tente atualizar a página novamente.
        </p>

        <button
          onclick="carregarPosts()"
        >
          Tentar novamente
        </button>

      </div>
    `;
  }
}


/*
  Inicia o carregamento.
*/
carregarPosts();
