"""
github/router.py
================
Responsabilidade: detectar intenção GitHub na fala do usuário e rotear
para a função correta.

Regra: retorna uma string com a resposta, ou None se não for comando GitHub.
O loop principal em core/loop.py decide o que fazer com o retorno.
"""

import re
from core.config import GITHUB_TOKEN
from github.repos  import listar_repos, criar_repo
from github.issues import listar_issues, criar_issue, fechar_issue
from github.commits import commit_arquivo
from github.readme import gerar_readme


def _extrair_apos(texto: str, palavra_chave: str) -> str:
    idx = texto.lower().find(palavra_chave.lower())
    if idx == -1:
        return ""
    return texto[idx + len(palavra_chave):].strip()


def _extrair_entre(texto: str, depois_de: str, antes_de: str | None) -> str:
    texto_lower = texto.lower()
    inicio = texto_lower.find(depois_de.lower())
    if inicio == -1:
        return ""
    trecho = texto[inicio + len(depois_de):].strip()
    if antes_de:
        fim = trecho.lower().find(antes_de.lower())
        if fim != -1:
            trecho = trecho[:fim].strip()
    return trecho.strip()


def _extrair_numero(texto: str) -> int | None:
    numeros = re.findall(r"\d+", texto)
    return int(numeros[0]) if numeros else None


def _extrair_nome_repo(texto_usuario: str, t: str) -> str:
    """
    Tenta extrair o nome do repositório de formas diferentes.
    Prioriza palavras após gatilhos como 'chamado', 'nome', 'para'.
    """
    # Palavras que nunca são nomes de repositório
    PALAVRAS_IGNORADAS = {
        "privado", "público", "publico", "agora", "por", "favor", "github",
        "criar", "cria", "repositório", "repositorio", "repo", "um", "uma",
        "novo", "nova", "please", "quero", "preciso", "pode",
        "fazer", "feito", "meu", "minha", "nosso", "projeto", "código",
        "codigo", "arquivo", "pasta", "o", "a", "de", "do", "da", "no",
        "na", "em", "com", "para", "que", "se", "é", "e", "ou",
    }

    # Tenta extrair após palavras-gatilho
    for gatilho in ["chamado", "chama", "nome", "chame", "intitulado", "para o repo",
                    "para o repositório", "para o repositorio", "repositório chamado",
                    "repositorio chamado", "repo chamado"]:
        if gatilho in t:
            trecho = _extrair_apos(texto_usuario, gatilho)
            palavras = [p for p in trecho.split() if p.lower() not in PALAVRAS_IGNORADAS]
            if palavras:
                return palavras[0].lower()

    # Fallback: última palavra significativa da frase
    palavras = [p for p in texto_usuario.split() if p.lower() not in PALAVRAS_IGNORADAS]
    return palavras[-1].lower() if palavras else ""


async def processar_comando_github(texto_usuario: str) -> str | None:
    if not GITHUB_TOKEN:
        return None

    t = texto_usuario.lower()

    # ─────────────────────────────────────────────────────────────────────────
    # FLAGS DE INTENÇÃO
    # ─────────────────────────────────────────────────────────────────────────

    tem_repo = any(p in t for p in [
        "repositório", "repositorio", "repo", "repositórios", "repositorios",
        "projeto", "projetos",
    ])

    tem_listar = any(p in t for p in [
        "listar", "lista", "ver", "mostrar", "mostra", "quais", "quantos",
        "tenho", "meus", "meu", "exibir", "exibe", "apresentar", "apresenta",
        "me mostra", "me diz", "me fala", "quero ver", "quero saber",
        "me lista", "me listar",
    ])

    tem_criar = any(p in t for p in [
        "criar", "cria", "novo", "nova", "criar um", "cria um", "iniciar",
        "inicia", "abrir", "abre", "fazer", "faz", "adicionar", "adiciona",
        "quero criar", "preciso criar", "pode criar", "me cria", "me criar",
    ])

    tem_issue = any(p in t for p in [
        "issue", "issues", "tarefa", "tarefas", "bug", "bugs", "problema",
        "problemas", "ticket", "tickets",
    ])

    tem_commit = any(p in t for p in [
        "commit", "commitar", "commita", "subir arquivo", "sobe arquivo",
        "enviar arquivo", "envia arquivo", "push arquivo", "salvar arquivo",
        "salva arquivo",
    ])

    tem_readme = any(p in t for p in [
    "readme", "read me", "redmi", "leiame", "leia me", "documentação",
    "documentacao", "documenta", "documentar", "gerar doc", "gera doc",
    "criar doc", "cria doc", "descrição do projeto", "descricao do projeto",
    "riad", "riad me", "read", "rime", "reame", "radme", "rim",
])

    tem_fechar = any(p in t for p in [
        "fechar", "fecha", "encerrar", "encerra", "resolver", "resolve",
        "concluir", "conclui", "finalizar", "finaliza", "completar", "completa",
        "marcar como resolvido", "marcar resolvido",
    ])

    tem_github = any(p in t for p in [
        "github", "git hub", "git", "kit hub", "kit rubi", "kit ru",
        "github.com",
    ])

    # Se não tem nenhuma palavra de contexto GitHub, passa para IA
    if not tem_repo and not tem_issue and not tem_commit and not tem_readme and not tem_github:
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # README — vem ANTES de criar repo para evitar conflito
    # ─────────────────────────────────────────────────────────────────────────
    if tem_readme:
        # Tenta extrair o nome do repo de várias formas
        repo = ""
        for gatilho in ["para o repo", "para o repositório", "para o repositorio",
                        "do repo", "do repositório", "do repositorio",
                        "no repo", "no repositório", "no repositorio",
                        "repo", "repositório", "repositorio", "para"]:
            trecho = _extrair_apos(texto_usuario, gatilho)
            candidato = trecho.split()[0] if trecho.split() else ""
            if candidato and candidato.lower() not in ["o", "a", "do", "da", "de"]:
                repo = candidato.lower()
                break

        if not repo:
            return "Qual é o nome do repositório para eu gerar o README?"
        return await gerar_readme(repo)

    # ─────────────────────────────────────────────────────────────────────────
    # LISTAR REPOSITÓRIOS
    # ─────────────────────────────────────────────────────────────────────────
    if tem_repo and tem_listar and not tem_criar and not tem_issue:
        return await listar_repos()

    # Frases diretas de listagem mesmo sem "listar"
    frases_listar_diretas = [
        "quais repos", "quais repositórios", "quais repositorios",
        "meus repos", "meus repositórios", "meus repositorios",
        "ver repos", "ver repositórios", "ver repositorios",
        "mostra repos", "mostra repositórios", "mostra repositorios",
        "lista repos", "lista repositórios", "lista repositorios",
        "repositórios que tenho", "repositorios que tenho",
        "quantos repos", "quantos repositórios", "quantos repositorios",
    ]
    if any(f in t for f in frases_listar_diretas):
        return await listar_repos()

    # ─────────────────────────────────────────────────────────────────────────
    # CRIAR REPOSITÓRIO
    # ─────────────────────────────────────────────────────────────────────────
    if tem_repo and tem_criar and not tem_listar and not tem_readme and not tem_issue:
        privado = any(p in t for p in ["privado", "privada", "secreto", "secreta", "private"])
        nome = _extrair_nome_repo(texto_usuario, t)

        if not nome:
            return "Qual nome você quer dar ao repositório?"
        return await criar_repo(nome, privado)

    # ─────────────────────────────────────────────────────────────────────────
    # COMMIT DE ARQUIVO
    # ─────────────────────────────────────────────────────────────────────────
    if tem_commit:
        arquivo  = _extrair_entre(texto_usuario, "arquivo", "no repo")
        repo     = _extrair_entre(texto_usuario, "no repo", "com mensagem")
        mensagem = _extrair_apos(texto_usuario, "com mensagem")

        # Tenta variações de "no repo"
        if not repo:
            repo = _extrair_entre(texto_usuario, "repositório", "com mensagem") or \
                   _extrair_entre(texto_usuario, "repositorio", "com mensagem")
        if not mensagem:
            mensagem = _extrair_apos(texto_usuario, "mensagem") or \
                       _extrair_apos(texto_usuario, "commit")

        if not arquivo or not repo or not mensagem:
            return (
                "Para fazer um commit, diga: "
                "fazer commit do arquivo NOME no repo REPOSITORIO com mensagem MENSAGEM."
            )
        return await commit_arquivo(repo.strip(), arquivo.strip(), "", mensagem.strip())

    # ─────────────────────────────────────────────────────────────────────────
    # CRIAR ISSUE
    # ─────────────────────────────────────────────────────────────────────────
    if tem_issue and tem_criar:
        repo = ""
        titulo = ""

        for gatilho_repo in ["no repo", "no repositório", "no repositorio",
                              "em repo", "para o repo", "repositório", "repo"]:
            for gatilho_titulo in ["com título", "com titulo", "título", "titulo",
                                   "chamada", "chamado", "intitulada", "intitulado"]:
                repo   = _extrair_entre(texto_usuario, gatilho_repo, gatilho_titulo)
                titulo = _extrair_apos(texto_usuario, gatilho_titulo)
                if repo and titulo:
                    break
            if repo and titulo:
                break

        if not repo or not titulo:
            return "Para criar uma issue, diga: criar issue no repo NOME com título TITULO."
        return await criar_issue(repo.strip(), titulo.strip())

    # ─────────────────────────────────────────────────────────────────────────
    # FECHAR ISSUE
    # ─────────────────────────────────────────────────────────────────────────
    if tem_issue and tem_fechar:
        numero = _extrair_numero(texto_usuario)

        repo = ""
        for gatilho in ["no repo", "no repositório", "no repositorio",
                        "do repo", "do repositório", "repo", "repositório"]:
            trecho = _extrair_apos(texto_usuario, gatilho)
            candidato = trecho.split()[0] if trecho.split() else ""
            if candidato:
                repo = candidato.lower()
                break

        if not numero or not repo:
            return "Para fechar uma issue, diga: fechar issue número NUMERO no repo REPOSITORIO."
        return await fechar_issue(repo, numero)

    # ─────────────────────────────────────────────────────────────────────────
    # LISTAR ISSUES
    # ─────────────────────────────────────────────────────────────────────────
    if tem_issue and (tem_repo or tem_listar) and not tem_criar and not tem_fechar:
        repo = ""
        for gatilho in ["do repo", "no repo", "do repositório", "no repositório",
                        "do repositorio", "no repositorio", "repo", "repositório",
                        "repositorio", "projeto"]:
            trecho = _extrair_apos(texto_usuario, gatilho)
            candidato = trecho.split()[0] if trecho.split() else ""
            if candidato and candidato.lower() not in ["o", "a", "do", "da", "de"]:
                repo = candidato.lower()
                break

        if not repo:
            return "Qual é o nome do repositório que você quer ver as issues?"
        return await listar_issues(repo)

    return None