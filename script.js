// =====================================================
// IPIRANGA 24H
// SUPABASE + MATÉRIAS + CONTAS + COMENTÁRIOS
// =====================================================


// =====================================================
// SUPABASE
// =====================================================

const SUPABASE_URL =
  "https://afbbgtijozwdnytjskka.supabase.co";

const SUPABASE_KEY =
  "COLE_AQUI_A_SUA_CHAVE_PUBLICA";


const supabaseClient =
  window.supabase.createClient(
    SUPABASE_URL,
    SUPABASE_KEY
  );


// =====================================================
// CONFIGURAÇÕES
// =====================================================

const postsContainer =
  document.getElementById("posts");

const QUANTIDADE_DE_POSTS = 4;

const CHAVE_ULTIMOS_POSTS =
  "ipiranga24h_ultimos_posts";


// =====================================================
// UTILIDADES
// =====================================================

function escaparHTML(texto) {

  if (
    texto === undefined ||
    texto === null
  ) {
    return "";
  }

  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


function escaparAtributo(texto) {
  return escaparHTML(texto);
}


function formatarData(data) {

  if (!data) {
    return "";
  }

  if (
    /^\d{2}\/\d{2}\/\d{4}$/.test(data)
  ) {
    return data;
  }

  const dataObj =
    new Date(data);

  if (
    isNaN(
      dataObj.getTime()
    )
  ) {
    return data;
  }

  return dataObj.toLocaleDateString(
    "pt-BR"
  );
}


function embaralhar(array) {

  const copia = [
    ...array
  ];

  for (
    let i = copia.length - 1;
    i > 0;
    i--
  ) {

    const j =
      Math.floor(
        Math.random() * (i + 1)
      );

    [
      copia[i],
      copia[j]
    ] = [
      copia[j],
      copia[i]
    ];
  }

  return copia;
}


// =====================================================
// IDENTIFICAÇÃO DAS MATÉRIAS
// =====================================================

function obterId(
  post,
  indice
) {

  if (
    post.id !== undefined &&
    post.id !== null
  ) {
    return String(
      post.id
    );
  }

  if (post.link) {
    return post.link;
  }

  return `post-${indice}`;
}


// =====================================================
// ÚLTIMOS POSTS
// =====================================================

function obterUltimosPosts() {

  try {

    const dados =
      JSON.parse(
        sessionStorage.getItem(
          CHAVE_ULTIMOS_POSTS
        )
      );

    if (
      Array.isArray(dados)
    ) {
      return dados;
    }

  } catch (erro) {

    console.error(
      "Erro ao ler últimos posts:",
      erro
    );
  }

  return [];
}


function salvarUltimosPosts(
  posts
) {

  try {

    const ids =
      posts.map(
        (
          post,
          indice
        ) =>
          obterId(
            post,
            indice
          )
      );

    sessionStorage.setItem(
      CHAVE_ULTIMOS_POSTS,
      JSON.stringify(ids)
    );

  } catch (erro) {

    console.error(
      "Erro ao salvar últimos posts:",
      erro
    );
  }
}


function escolherPosts(
  posts
) {

  if (
    !Array.isArray(posts)
  ) {
    return [];
  }

  if (
    posts.length <=
    QUANTIDADE_DE_POSTS
  ) {

    const escolhidos =
      embaralhar(posts);

    salvarUltimosPosts(
      escolhidos
    );

    return escolhidos;
  }


  const ultimosIds =
    obterUltimosPosts();


  const novosPosts =
    posts.filter(
      (
        post,
        indice
      ) =>
        !ultimosIds.includes(
          obterId(
            post,
            indice
          )
        )
    );


  let escolhidos;


  if (
    novosPosts.length >=
    QUANTIDADE_DE_POSTS
  ) {

    escolhidos =
      embaralhar(
        novosPosts
      ).slice(
        0,
        QUANTIDADE_DE_POSTS
      );

  } else {

    const restantes =
      posts.filter(
        (
          post
        ) =>
          !novosPosts.includes(
            post
          )
      );

    escolhidos = [
      ...embaralhar(
        novosPosts
      ),
      ...embaralhar(
        restantes
      )
    ].slice(
      0,
      QUANTIDADE_DE_POSTS
    );
  }


  salvarUltimosPosts(
    escolhidos
  );

  return escolhidos;
}


// =====================================================
// CONTA ATUAL
// =====================================================

let usuarioAtual = null;


async function atualizarUsuario() {

  const {
    data,
    error
  } =
    await supabaseClient.auth.getUser();


  if (error) {

    console.error(
      "Erro ao verificar usuário:",
      error
    );

    usuarioAtual = null;

    return null;
  }


  usuarioAtual =
    data?.user || null;

  return usuarioAtual;
}


// =====================================================
// CRIAR CONTA
// =====================================================

async function criarConta() {

  const username =
    document
      .getElementById(
        "cadastro-username"
      )
      ?.value
      .trim();


  const email =
    document
      .getElementById(
        "cadastro-email"
      )
      ?.value
      .trim();


  const senha =
    document
      .getElementById(
        "cadastro-senha"
      )
      ?.value;


  if (
    !username ||
    !email ||
    !senha
  ) {

    alert(
      "Preencha nome de usuário, e-mail e senha."
    );

    return;
  }


  if (
    username.length < 3
  ) {

    alert(
      "O nome de usuário precisa ter pelo menos 3 caracteres."
    );

    return;
  }


  if (
    senha.length < 6
  ) {

    alert(
      "A senha precisa ter pelo menos 6 caracteres."
    );

    return;
  }


  const botao =
    document.getElementById(
      "botao-cadastrar"
    );


  if (botao) {
    botao.disabled = true;
    botao.textContent =
      "Criando conta...";
  }


  try {

    // Verifica se o nome já existe.
    const {
      data: nomeExistente,
      error: erroNome
    } =
      await supabaseClient
        .from("profiles")
        .select("id")
        .eq(
          "username",
          username
        )
        .maybeSingle();


    if (erroNome) {
      throw erroNome;
    }


    if (nomeExistente) {

      alert(
        "Esse nome de usuário já está sendo usado."
      );

      return;
    }


    // Cria a conta no sistema de autenticação.
    const {
      data,
      error
    } =
      await supabaseClient.auth.signUp({

        email: email,

        password: senha

      });


    if (error) {
      throw error;
    }


    if (!data.user) {

      throw new Error(
        "Não foi possível criar a conta."
      );
    }


    // Cria o perfil do usuário.
    const {
      error: erroPerfil
    } =
      await supabaseClient
        .from("profiles")
        .insert({

          id: data.user.id,

          username: username

        });


    if (erroPerfil) {

      console.error(
        erroPerfil
      );

      alert(
        "A conta foi criada, mas houve um problema ao salvar o nome de usuário."
      );

      return;
    }


    fecharJanelaConta();


    alert(
      "Conta criada com sucesso!"
    );


    // Se a confirmação por e-mail estiver
    // ativada no Supabase.
    if (
      !data.session
    ) {

      alert(
        "Verifique seu e-mail para confirmar a conta antes de entrar."
      );
    }


    document
      .getElementById(
        "cadastro-username"
      )
      .value = "";


    document
      .getElementById(
        "cadastro-email"
      )
      .value = "";


    document
      .getElementById(
        "cadastro-senha"
      )
      .value = "";


  } catch (erro) {

    console.error(
      "Erro ao criar conta:",
      erro
    );


    alert(
      "Não foi possível criar a conta.\n\n" +
      (
        erro.message ||
        "Verifique os dados e tente novamente."
      )
    );


  } finally {

    if (botao) {

      botao.disabled = false;

      botao.textContent =
        "Criar conta";
    }
  }
}


// =====================================================
// ENTRAR
// =====================================================

async function entrarComConta() {

  const email =
    document
      .getElementById(
        "login-email"
      )
      ?.value
      .trim();


  const senha =
    document
      .getElementById(
        "login-senha"
      )
      ?.value;


  if (
    !email ||
    !senha
  ) {

    alert(
      "Digite seu e-mail e sua senha."
    );

    return;
  }


  const botao =
    document.getElementById(
      "botao-entrar-conta"
    );


  if (botao) {

    botao.disabled = true;

    botao.textContent =
      "Entrando...";
  }


  try {

    const {
      data,
      error
    } =
      await supabaseClient.auth.signInWithPassword({

        email: email,

        password: senha

      });


    if (error) {
      throw error;
    }


    usuarioAtual =
      data.user;


    localStorage.setItem(
      "modoAcesso",
      "conta"
    );


    fecharJanelaConta();


    await mostrarSite();


  } catch (erro) {

    console.error(
      "Erro ao entrar:",
      erro
    );


    alert(
      "Não foi possível entrar.\n\n" +
      (
        erro.message ||
        "Verifique seu e-mail e senha."
      )
    );


  } finally {

    if (botao) {

      botao.disabled = false;

      botao.textContent =
        "Entrar";
    }
  }
}


// =====================================================
// VISITANTE
// =====================================================

function entrarComoVisitante() {

  localStorage.setItem(
    "modoAcesso",
    "visitante"
  );


  mostrarSite();
}


// =====================================================
// SAIR
// =====================================================

async function sair() {

  await supabaseClient.auth.signOut();

  usuarioAtual = null;

  localStorage.removeItem(
    "modoAcesso"
  );


  const site =
    document.getElementById(
      "site"
    );

  const login =
    document.getElementById(
      "login-screen"
    );


  if (site) {
    site.style.display =
      "none";
  }


  if (login) {
    login.style.display =
      "flex";
  }
}


// =====================================================
// MOSTRAR SITE
// =====================================================

async function mostrarSite() {

  await atualizarUsuario();


  const login =
    document.getElementById(
      "login-screen"
    );

  const site =
    document.getElementById(
      "site"
    );


  if (login) {

    login.style.display =
      "none";
  }


  if (site) {

    site.style.display =
      "block";
  }


  atualizarInterfaceUsuario();

  carregarPosts();
}


// =====================================================
// INTERFACE DA CONTA
// =====================================================

function atualizarInterfaceUsuario() {

  const aviso =
    document.querySelector(
      ".aviso-visitante"
    );


  if (!aviso) {
    return;
  }


  if (usuarioAtual) {

    aviso.innerHTML =
      `Você está conectado como <strong>${escaparHTML(
        usuarioAtual.email || "usuário"
      )}</strong>.`;

  } else {

    aviso.innerHTML =
      "Você está navegando como visitante. " +
      "Crie uma conta para comentar.";
  }
}


// =====================================================
// JANELA DE LOGIN/CADASTRO
// =====================================================

function criarJanelaConta() {

  if (
    document.getElementById(
      "janela-conta"
    )
  ) {
    return;
  }


  const janela =
    document.createElement(
      "div"
    );


  janela.id =
    "janela-conta";


  janela.innerHTML = `

    <div class="caixa-conta">

      <button
        class="fechar-conta"
        onclick="fecharJanelaConta()"
      >
        ×
      </button>


      <div class="abas-conta">

        <button
          id="aba-login"
          class="aba-conta ativa"
          onclick="mostrarLogin()"
        >
          Entrar
        </button>

        <button
          id="aba-cadastro"
          class="aba-conta"
          onclick="mostrarCadastro()"
        >
          Criar conta
        </button>

      </div>


      <div
        id="form-login"
        class="form-conta"
      >

        <h2>
          Entrar
        </h2>

        <p>
          Entre na sua conta do Ipiranga 24h.
        </p>


        <input
          id="login-email"
          type="email"
          placeholder="Seu e-mail"
          autocomplete="email"
        >


        <input
          id="login-senha"
          type="password"
          placeholder="Sua senha"
          autocomplete="current-password"
        >


        <button
          id="botao-entrar-conta"
          class="botao-conta-principal"
          onclick="entrarComConta()"
        >
          Entrar
        </button>


        <button
          class="botao-conta-secundario"
          onclick="mostrarCadastro()"
        >
          Ainda não tenho conta
        </button>

      </div>


      <div
        id="form-cadastro"
        class="form-conta"
        style="display:none;"
      >

        <h2>
          Criar conta
        </h2>

        <p>
          Crie sua conta para poder comentar.
        </p>


        <input
          id="cadastro-username"
          type="text"
          placeholder="Nome de usuário"
          maxlength="30"
          autocomplete="username"
        >


        <input
          id="cadastro-email"
          type="email"
          placeholder="Seu e-mail"
          autocomplete="email"
        >


        <input
          id="cadastro-senha"
          type="password"
          placeholder="Crie uma senha"
          minlength="6"
          autocomplete="new-password"
        >


        <button
          id="botao-cadastrar"
          class="botao-conta-principal"
          onclick="criarConta()"
        >
          Criar conta
        </button>


        <button
          class="botao-conta-secundario"
          onclick="mostrarLogin()"
        >
          Já tenho uma conta
        </button>

      </div>

    </div>

  `;


  document.body.appendChild(
    janela
  );
}


function abrirJanelaConta() {

  criarJanelaConta();


  const janela =
    document.getElementById(
      "janela-conta"
    );


  janela.style.display =
    "flex";


  mostrarLogin();
}


function fecharJanelaConta() {

  const janela =
    document.getElementById(
      "janela-conta"
    );


  if (janela) {

    janela.style.display =
      "none";
  }
}


function mostrarLogin() {

  criarJanelaConta();


  document
    .getElementById(
      "form-login"
    )
    .style.display =
    "block";


  document
    .getElementById(
      "form-cadastro"
    )
    .style.display =
    "none";


  document
    .getElementById(
      "aba-login"
    )
    .classList.add(
      "ativa"
    );


  document
    .getElementById(
      "aba-cadastro"
    )
    .classList.remove(
      "ativa"
    );
}


function mostrarCadastro() {

  criarJanelaConta();


  document
    .getElementById(
      "form-login"
    )
    .style.display =
    "none";


  document
    .getElementById(
      "form-cadastro"
    )
    .style.display =
    "block";


  document
    .getElementById(
      "aba-login"
    )
    .classList.remove(
      "ativa"
    );


  document
    .getElementById(
      "aba-cadastro"
    )
    .classList.add(
      "ativa"
    );
}


// =====================================================
// COMENTÁRIOS
// =====================================================

async function abrirComentarios(
  id
) {

  const area =
    document.getElementById(
      `comentarios-${id}`
    );


  if (!area) {
    return;
  }


  const aberto =
    area.style.display ===
    "block";


  if (aberto) {

    area.style.display =
      "none";

    return;
  }


  await atualizarUsuario();


  area.style.display =
    "block";


  const campo =
    document.getElementById(
      `comentario-texto-${id}`
    );


  const aviso =
    area.querySelector(
      ".aviso-login-comentario"
    );


  if (
    !usuarioAtual
  ) {

    if (!aviso) {

      const mensagem =
        document.createElement(
          "p"
        );

      mensagem.className =
        "aviso-login-comentario";


      mensagem.innerHTML =
        `💬 Para comentar, você precisa <button onclick="abrirJanelaConta()">entrar ou criar uma conta</button>.`;


      area.prepend(
        mensagem
      );
    }


    if (campo) {
      campo.disabled =
        true;
    }


    const botao =
      area.querySelector(
        ".botao-publicar-comentario"
      );


    if (botao) {
      botao.disabled =
        true;
    }


    return;
  }


  if (campo) {

    campo.disabled =
      false;

    setTimeout(
      () =>
        campo.focus(),
      100
    );
  }


  const botao =
    area.querySelector(
      ".botao-publicar-comentario"
    );


  if (botao) {
    botao.disabled =
      false;
  }


  carregarComentarios(
    id
  );
}


async function adicionarComentario(
  id
) {

  await atualizarUsuario();


  if (!usuarioAtual) {

    alert(
      "Você precisa criar uma conta ou entrar para comentar."
    );

    abrirJanelaConta();

    return;
  }


  const campo =
    document.getElementById(
      `comentario-texto-${id}`
    );


  if (!campo) {
    return;
  }


  const texto =
    campo.value.trim();


  if (!texto) {

    alert(
      "Digite um comentário antes de publicar."
    );

    return;
  }


  if (
    texto.length > 500
  ) {

    alert(
      "O comentário pode ter no máximo 500 caracteres."
    );

    return;
  }


  const {
    data: perfil,
    error: erroPerfil
  } =
    await supabaseClient
      .from("profiles")
      .select("username")
      .eq(
        "id",
        usuarioAtual.id
      )
      .maybeSingle();


  if (erroPerfil) {

    console.error(
      erroPerfil
    );

    alert(
      "Não foi possível encontrar seu perfil."
    );

    return;
  }


  const username =
    perfil?.username ||
    usuarioAtual.email ||
    "Usuário";


  const {
    error
  } =
    await supabaseClient
      .from("comments")
      .insert({

        post_id: String(id),

        user_id:
          usuarioAtual.id,

        username:
          username,

        content:
          texto

      });


  if (error) {

    console.error(
      "Erro ao publicar comentário:",
      error
    );

    alert(
      "Não foi possível publicar o comentário."
    );

    return;
  }


  campo.value =
    "";


  await carregarComentarios(
    id
  );
}


// =====================================================
// CARREGAR COMENTÁRIOS
// =====================================================

async function carregarComentarios(
  id
) {

  const lista =
    document.getElementById(
      `lista-comentarios-${id}`
    );


  if (!lista) {
    return;
  }


  const {
    data,
    error
  } =
    await supabaseClient
      .from("comments")
      .select(
        "id, username, content, created_at"
      )
      .eq(
        "post_id",
        String(id)
      )
      .order(
        "created_at",
        {
          ascending: true
        }
      );


  if (error) {

    console.error(
      "Erro ao carregar comentários:",
      error
    );


    lista.innerHTML =
      `<p class="sem-comentarios">
        Não foi possível carregar os comentários.
      </p>`;

    return;
  }


  if (
    !data ||
    data.length === 0
  ) {

    lista.innerHTML =
      `<p class="sem-comentarios">
        Nenhum comentário ainda.
      </p>`;

    return;
  }


  lista.innerHTML =
    data
      .map(
        comentario => `

          <div class="comentario">

            <strong>
              ${escaparHTML(
                comentario.username
              )}
            </strong>

            <small>
              ${escaparHTML(
                formatarData(
                  comentario.created_at
                )
              )}
            </small>

            <p>
              
