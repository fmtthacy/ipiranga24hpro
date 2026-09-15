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
              
// ======================================================
// IPIRANGA 24H — SISTEMA DE CONTAS + COMENTÁRIOS
// ======================================================

// ---------- SUPABASE ----------
const SUPABASE_URL = "https://afbbgtijozwdnytjskka.supabase.co";

const SUPABASE_KEY =
  "sb_publishable_l1xwkAczycJw-vaA9TXPNA_uGV7QS0n";

const supabaseClient = window.supabase.createClient(
  SUPABASE_URL,
  SUPABASE_KEY
);


// ======================================================
// CONFIGURAÇÕES
// ======================================================

const postsContainer = document.getElementById("posts");
const QUANTIDADE_DE_POSTS = 4;

let usuarioAtual = null;


// ======================================================
// ESTILO DA JANELA DE LOGIN / CADASTRO
// ======================================================

const estiloConta = document.createElement("style");

estiloConta.textContent = `
#janela-conta {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.65);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.caixa-conta {
  background: white;
  width: 100%;
  max-width: 420px;
  border-radius: 18px;
  padding: 25px;
  box-sizing: border-box;
  position: relative;
  box-shadow: 0 15px 40px rgba(0,0,0,.3);
}

.caixa-conta h2 {
  color: #003b7a;
  margin-top: 0;
  text-align: center;
}

.caixa-conta p {
  text-align: center;
  color: #666;
}

.fechar-conta {
  position: absolute;
  right: 15px;
  top: 10px;
  border: none;
  background: none;
  font-size: 25px;
  cursor: pointer;
}

.abas-conta {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.aba-conta {
  flex: 1;
  padding: 11px;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  background: #eee;
  font-weight: bold;
}

.aba-conta.ativa {
  background: #ffd600;
  color: #003b7a;
}

.form-conta {
  display: none;
}

.form-conta.ativo {
  display: block;
}

.form-conta label {
  display: block;
  margin-top: 12px;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-conta input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 9px;
  font-size: 16px;
}

.botao-conta-principal {
  width: 100%;
  margin-top: 18px;
  padding: 13px;
  border: none;
  border-radius: 9px;
  background: #0055a5;
  color: white;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
}

.botao-conta-secundario {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  border: 1px solid #0055a5;
  border-radius: 9px;
  background: white;
  color: #0055a5;
  font-weight: bold;
  cursor: pointer;
}

.mensagem-conta {
  margin-top: 12px;
  padding: 10px;
  border-radius: 8px;
  background: #f1f1f1;
  text-align: center;
  display: none;
}

.aviso-login-comentario {
  padding: 12px;
  background: #fff4bf;
  border-radius: 9px;
  color: #604f00;
  margin-bottom: 10px;
}
`;

document.head.appendChild(estiloConta);


// ======================================================
// CRIA JANELA DE LOGIN / CADASTRO
// ======================================================

function criarJanelaConta() {

  if (document.getElementById("janela-conta")) {
    return;
  }

  const janela = document.createElement("div");

  janela.id = "janela-conta";

  janela.innerHTML = `
    <div class="caixa-conta">

      <button class="fechar-conta" onclick="fecharJanelaConta()">
        ×
      </button>

      <h2>Ipiranga 24h</h2>

      <p>Acesse sua conta</p>

      <div class="abas-conta">

        <button
          id="aba-login"
          class="aba-conta ativa"
          onclick="mostrarLogin()">
          Entrar
        </button>

        <button
          id="aba-cadastro"
          class="aba-conta"
          onclick="mostrarCadastro()">
          Criar conta
        </button>

      </div>


      <!-- LOGIN -->

      <div id="form-login" class="form-conta ativo">

        <label>E-mail</label>

        <input
          id="login-email"
          type="email"
          placeholder="seu@email.com"
        >

        <label>Senha</label>

        <input
          id="login-senha"
          type="password"
          placeholder="Sua senha"
        >

        <button
          class="botao-conta-principal"
          onclick="entrarComConta()">
          Entrar
        </button>

      </div>


      <!-- CADASTRO -->

      <div id="form-cadastro" class="form-conta">

        <label>Nome de usuário</label>

        <input
          id="cadastro-usuario"
          type="text"
          placeholder="Como você quer aparecer"
        >

        <label>E-mail</label>

        <input
          id="cadastro-email"
          type="email"
          placeholder="seu@email.com"
        >

        <label>Senha</label>

        <input
          id="cadastro-senha"
          type="password"
          placeholder="Mínimo de 6 caracteres"
        >

        <button
          class="botao-conta-principal"
          onclick="criarConta()">
          Criar conta
        </button>

      </div>


      <div id="mensagem-conta" class="mensagem-conta"></div>

    </div>
  `;

  document.body.appendChild(janela);
}


// ======================================================
// MENSAGEM DA CONTA
// ======================================================

function mostrarMensagemConta(texto) {

  const mensagem = document.getElementById("mensagem-conta");

  if (!mensagem) return;

  mensagem.textContent = texto;
  mensagem.style.display = "block";
}


// ======================================================
// ABRIR JANELA
// ======================================================

function abrirJanelaConta() {

  criarJanelaConta();

  const janela = document.getElementById("janela-conta");

  janela.style.display = "flex";

  mostrarLogin();
}


// ======================================================
// FECHAR JANELA
// ======================================================

function fecharJanelaConta() {

  const janela = document.getElementById("janela-conta");

  if (janela) {
    janela.style.display = "none";
  }
}


// ======================================================
// MOSTRAR LOGIN
// ======================================================

function mostrarLogin() {

  criarJanelaConta();

  document.getElementById("form-login").classList.add("ativo");
  document.getElementById("form-cadastro").classList.remove("ativo");

  document.getElementById("aba-login").classList.add("ativa");
  document.getElementById("aba-cadastro").classList.remove("ativa");

  const mensagem = document.getElementById("mensagem-conta");

  if (mensagem) {
    mensagem.style.display = "none";
  }
}


// ======================================================
// MOSTRAR CADASTRO
// ======================================================

function mostrarCadastro() {

  criarJanelaConta();

  document.getElementById("form-login").classList.remove("ativo");
  document.getElementById("form-cadastro").classList.add("ativo");

  document.getElementById("aba-login").classList.remove("ativa");
  document.getElementById("aba-cadastro").classList.add("ativa");

  const mensagem = document.getElementById("mensagem-conta");

  if (mensagem) {
    mensagem.style.display = "none";
  }
}


// ======================================================
// ENTRAR — BOTÃO DO INDEX
// ======================================================

window.entrar = function () {

  localStorage.removeItem("modoAcesso");

  abrirJanelaConta();
};


// ======================================================
// CONTINUAR COMO VISITANTE
// ======================================================

window.entrarComoVisitante = function () {

  localStorage.setItem("modoAcesso", "visitante");

  fecharJanelaConta();

  mostrarSite();

};


// ======================================================
// CRIAR CONTA
// ======================================================

window.criarConta = async function () {

  const username =
    document.getElementById("cadastro-usuario").value.trim();

  const email =
    document.getElementById("cadastro-email").value.trim();

  const senha =
    document.getElementById("cadastro-senha").value;


  if (!username || !email || !senha) {

    mostrarMensagemConta(
      "Preencha todos os campos."
    );

    return;
  }


  if (username.length < 3) {

    mostrarMensagemConta(
      "O nome de usuário precisa ter pelo menos 3 caracteres."
    );

    return;
  }


  if (senha.length < 6) {

    mostrarMensagemConta(
      "A senha precisa ter pelo menos 6 caracteres."
    );

    return;
  }


  mostrarMensagemConta(
    "Criando sua conta..."
  );


  try {

    // Verifica se o nome já existe

    const { data: nomeExistente, error: erroNome } =
      await supabaseClient
        .from("profiles")
        .select("id")
        .eq("username", username)
        .maybeSingle();


    if (erroNome) {

      console.error(erroNome);

    }


    if (nomeExistente) {

      mostrarMensagemConta(
        "Esse nome de usuário já está sendo usado."
      );

      return;
    }


    // Cria usuário no Supabase Auth

    const { data, error } =
      await supabaseClient.auth.signUp({

        email: email,

        password: senha,

        options: {

          data: {
            username: username
          }

        }

      });


    if (error) {

      mostrarMensagemConta(
        error.message
      );

      return;
    }


    // Guarda temporariamente o nome

    localStorage.setItem(
      "ipiranga24h_username",
      username
    );


    // Se o Supabase já criou uma sessão,
    // cria o perfil imediatamente.

    if (data.session && data.user) {

      await garantirPerfil(data.user);

      usuarioAtual = data.user;

      localStorage.setItem(
        "modoAcesso",
        "conta"
      );

      fecharJanelaConta();

      mostrarSite();

      atualizarInterfaceUsuario();

    } else {

      mostrarMensagemConta(
        "Conta criada! Verifique seu e-mail para confirmar a conta e depois entre."
      );

    }


  } catch (erro) {

    console.error(erro);

    mostrarMensagemConta(
      "Não foi possível criar a conta."
    );

  }

};


// ======================================================
// ENTRAR COM CONTA
// ======================================================

window.entrarComConta = async function () {

  const email =
    document.getElementById("login-email").value.trim();

  const senha =
    document.getElementById("login-senha").value;


  if (!email || !senha) {

    mostrarMensagemConta(
      "Digite seu e-mail e sua senha."
    );

    return;
  }


  mostrarMensagemConta(
    "Entrando..."
  );


  try {

    const { data, error } =
      await supabaseClient.auth.signInWithPassword({

        email: email,

        password: senha

      });


    if (error) {

      mostrarMensagemConta(
        "E-mail ou senha incorretos."
      );

      return;
    }


    usuarioAtual = data.user;


    await garantirPerfil(usuarioAtual);


    localStorage.setItem(
      "modoAcesso",
      "conta"
    );


    fecharJanelaConta();

    mostrarSite();

    atualizarInterfaceUsuario();

    carregarPosts();


  } catch (erro) {

    console.error(erro);

    mostrarMensagemConta(
      "Não foi possível entrar."
    );

  }

};


// ======================================================
// GARANTIR PERFIL
// ======================================================

async function garantirPerfil(usuario) {

  if (!usuario) return;


  const { data: perfil } =
    await supabaseClient
      .from("profiles")
      .select("*")
      .eq("id", usuario.id)
      .maybeSingle();


  if (perfil) {
    return perfil;
  }


  const usernameSalvo =
    localStorage.getItem("ipiranga24h_username");


  const username =
    usuario.user_metadata?.username ||
    usernameSalvo ||
    usuario.email.split("@")[0];


  const { data, error } =
    await supabaseClient
      .from("profiles")
      .insert({

        id: usuario.id,

        username: username

      })
      .select()
      .single();


  if (error) {

    console.error(
      "Erro ao criar perfil:",
      error
    );

    return null;
  }


  return data;
}


// ======================================================
// MOSTRAR SITE
// ======================================================

function mostrarSite() {

  const loginScreen =
    document.querySelector(".login-screen");

  const conteudo =
    document.querySelector(".conteudo");

  const topbar =
    document.querySelector(".topbar");


  if (loginScreen) {

    loginScreen.style.display = "none";

  }


  if (topbar) {

    topbar.style.display = "flex";

  }


  if (conteudo) {

    conteudo.style.display = "block";

  }

}


// ======================================================
// MOSTRAR LOGIN SCREEN
// ======================================================

function mostrarTelaLogin() {

  const loginScreen =
    document.querySelector(".login-screen");

  const conteudo =
    document.querySelector(".conteudo");

  const topbar =
    document.querySelector(".topbar");


  if (loginScreen) {

    loginScreen.style.display = "flex";

  }


  if (topbar) {

    topbar.style.display = "none";

  }


  if (conteudo) {

    conteudo.style.display = "none";

  }

}


// ======================================================
// SAIR
// ======================================================

window.sair = async function () {

  await supabaseClient.auth.signOut();

  usuarioAtual = null;

  localStorage.removeItem("modoAcesso");

  localStorage.removeItem(
    "ipiranga24h_username"
  );

  mostrarTelaLogin();

};


// ======================================================
// ATUALIZA INTERFACE
// ======================================================

async function atualizarInterfaceUsuario() {

  const aviso =
    document.querySelector(".aviso-visitante");


  if (!aviso) return;


  if (usuarioAtual) {

    let username =
      usuarioAtual.user_metadata?.username;


    const { data: perfil } =
      await supabaseClient
        .from("profiles")
        .select("username")
        .eq("id", usuarioAtual.id)
        .maybeSingle();


    if (perfil) {

      username = perfil.username;

    }


    aviso.textContent =
      `Você está conectado como ${username || "usuário"}.`;

    aviso.style.background =
      "#e8f5e9";

    aviso.style.color =
      "#1b5e20";


  } else {

    aviso.textContent =
      "Você está navegando como visitante. Entre ou crie uma conta para comentar.";

    aviso.style.background =
      "#fff4bf";

    aviso.style.color =
      "#604f00";

  }

}


// ======================================================
// ID ESTÁVEL DO POST
// ======================================================

function obterId(post, indice) {

  // O link é melhor porque não muda
  // quando o data.json é atualizado.

  if (post.link) {

    return post.link;

  }


  if (post.url) {

    return post.url;

  }


  return String(
