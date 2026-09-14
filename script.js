/* ========================================
   IPIRANGA 24H
   ESTILO COMPLETO
======================================== */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #f3f4f6;
    color: #17233c;
    min-height: 100vh;
}


/* ========================================
   TELA DE ACESSO
======================================== */

.tela-acesso {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 25px 18px;

    background:
        linear-gradient(
            180deg,
            #003b7a 0%,
            #00549a 55%,
            #f3f4f6 55%,
            #f3f4f6 100%
        );
}

.caixa-acesso {
    width: 100%;
    max-width: 420px;
    background: white;
    border-radius: 20px;
    padding: 35px 25px;
    text-align: center;

    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.15);
}

.logo-ipiranga {
    display: inline-block;

    background: #ffd900;
    color: #003b7a;

    font-size: 25px;
    font-weight: 900;

    padding: 9px 18px;
    border-radius: 12px;

    margin-bottom: 20px;
}

.caixa-acesso h1 {
    color: #003b7a;
    font-size: 29px;
    margin-bottom: 10px;
}

.caixa-acesso p {
    color: #666;
    font-size: 15px;
    line-height: 1.5;
    margin-bottom: 28px;
}


/* ========================================
   BOTÕES DE ACESSO
======================================== */

.botao-principal,
.botao-visitante {
    width: 100%;
    padding: 14px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;

    transition: 0.2s;
}

.botao-principal {
    border: none;
    background: #003b7a;
    color: white;
    margin-bottom: 10px;
}

.botao-principal:hover {
    background: #002d5d;
}

.botao-visitante {
    background: white;
    color: #003b7a;
    border: 2px solid #003b7a;
}

.botao-visitante:hover {
    background: #eef5fb;
}

.caixa-acesso small {
    display: block;
    margin-top: 18px;

    color: #777;
    font-size: 12px;
    line-height: 1.4;
}


/* ========================================
   SITE PRINCIPAL
======================================== */

.site {
    min-height: 100vh;
}


/* ========================================
   CABEÇALHO
======================================== */

header {
    background: #003b7a;
    color: white;

    border-bottom: 6px solid #ffd900;

    padding: 20px 16px;
}

.topo {
    width: 100%;
    max-width: 850px;
    margin: auto;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
}

.topo h1 {
    font-size: 28px;
    margin-bottom: 5px;
}

.topo p {
    font-size: 14px;
    opacity: 0.9;
}


/* ========================================
   BOTÃO SAIR
======================================== */

.botao-sair {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.7);
    color: white;

    padding: 8px 13px;
    border-radius: 8px;

    cursor: pointer;
}

.botao-sair:hover {
    background: rgba(255,255,255,0.1);
}


/* ========================================
   CONTEÚDO
======================================== */

main {
    width: 100%;
    max-width: 850px;

    margin: 0 auto;

    padding: 20px 15px 50px;
}


/* ========================================
   TIPO DE ACESSO
======================================== */

.tipo-acesso {
    background: white;

    border-left: 5px solid #ffd900;

    padding: 12px 15px;

    border-radius: 8px;

    margin-bottom: 20px;

    color: #555;
    font-size: 13px;

    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}


/* ========================================
   FEED
======================================== */

#posts {
    display: flex;
    flex-direction: column;
    gap: 20px;
}


/* ========================================
   PUBLICAÇÃO
======================================== */

.post {
    background: white;

    border-radius: 14px;
    overflow: hidden;

    border: 1px solid #e2e5e9;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.07);
}

.post-header {
    padding: 17px 18px 10px;
}

.post-source {
    color: #0066b3;

    font-size: 13px;
    font-weight: bold;

    margin-bottom: 7px;
}

.post-title {
    color: #17233c;

    font-size: 21px;
    line-height: 1.3;

    margin-bottom: 8px;
}

.post-date {
    color: #777;
    font-size: 12px;
}


/* ========================================
   IMAGEM
======================================== */

.post-image {
    width: 100%;
    max-height: 420px;

    object-fit: cover;

    display: block;
}


/* ========================================
   TEXTO DA PUBLICAÇÃO
======================================== */

.post-content {
    padding: 15px 18px;
}

.post-description {
    color: #444;

    font-size: 15px;
    line-height: 1.5;
}


/* ========================================
   AÇÕES
======================================== */

.post-actions {
    display: flex;
    align-items: center;

    border-top: 1px solid #eeeeee;

    padding: 8px 10px;

    gap: 5px;
}

.action-button {
    border: none;
    background: transparent;

    color: #555;

    cursor: pointer;

    padding: 9px 10px;

    border-radius: 8px;

    font-size: 14px;

    transition: 0.2s;
}

.action-button:hover {
    background: #f1f3f5;
}

.action-button:disabled {
    cursor: default;
    opacity: 0.8;
}

.action-button.liked {
    color: #d7263d;
}

.action-button span {
    margin-left: 3px;
}


/* ========================================
   COMENTÁRIOS
======================================== */

.comments {
    display: none;

    padding: 15px 18px;

    border-top: 1px solid #eeeeee;

    background: #fafafa;
}

.comments.active {
    display: block;
}

.comment-form {
    display: flex;
    gap: 8px;

    margin-bottom: 15px;
}

.comment-input {
    flex: 1;

    border: 1px solid #d5d9df;

    border-radius: 8px;

    padding: 10px;

    outline: none;

    font-size: 14px;
}

.comment-input:focus {
    border-color: #0066b3;
}

.comment-button {
    border: none;

    background: #0066b3;
    color: white;

    padding: 10px 14px;

    border-radius: 8px;

    cursor: pointer;

    font-weight: bold;
}

.comment-button:hover {
    background: #004f8c;
}

.comment {
    padding: 10px;

    background: white;

    border-radius: 8px;

    margin-bottom: 8px;

    font-size: 14px;
}

.comment strong {
    color: #003b7a;
}


/* ========================================
   MENSAGEM DE COMPARTILHAMENTO
======================================== */

.share-message {
    position: fixed;

    bottom: 20px;
    left: 50%;

    transform: translateX(-50%);

    background: #003b7a;
    color: white;

    padding: 12px 18px;

    border-radius: 10px;

    font-size: 14px;

    display: none;

    z-index: 1000;
}

.share-message.active {
    display: block;
}


/* ========================================
   CARREGAMENTO
======================================== */

.loading {
    text-align: center;

    padding: 40px 20px;

    color: #666;
}

.loading::before {
    content: "⟳";

    display: block;

    font-size: 30px;

    margin-bottom: 10px;

    animation: girar 1s linear infinite;
}

@keyframes girar {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}


/* ========================================
   ERRO
======================================== */

.error {
    background: white;

    border-left: 5px solid #d7263d;

    padding: 18px;

    border-radius: 10px;

    color: #555;
}


/* ========================================
   CELULAR
======================================== */

@media (max-width: 600px) {

    .tela-acesso {
        padding: 20px 15px;
    }

    .caixa-acesso {
        padding: 30px 20px;
    }

    .caixa-acesso h1 {
        font-size: 25px;
    }

    header {
        padding: 18px 12px;
    }

    .topo h1 {
        font-size: 24px;
    }

    .topo p {
        font-size: 12px;
    }

    .botao-sair {
        padding: 7px 10px;
        font-size: 12px;
    }

    main {
        padding: 15px 10px 40px;
    }

    .post-title {
        font-size: 18px;
    }

    .post-description {
        font-size: 14px;
    }

    .post-actions {
        justify-content: space-between;
    }

    .action-button {
        font-size: 12px;
        padding: 8px 5px;
    }

    .comment-form {
        flex-direction: column;
    }

    .comment-button {
        width: 100%;
    }
        }
