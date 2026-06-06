"""
github/router.py
================
Responsabilidade: detectar intenção GitHub na fala do usuário e rotear
para a função correta.
"""

import re
from core.config import GITHUB_TOKEN
from github.repos  import listar_repos, criar_repo
from github.issues import listar_issues, criar_issue, fechar_issue
from github.commits import commit_arquivo
from github.readme import gerar_readme


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE EXTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

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


_PALAVRAS_IGNORADAS = {
    "privado", "privada", "público", "publica", "publico", "agora", "por",
    "favor", "github", "git", "criar", "cria", "repositório", "repositorio",
    "repo", "um", "uma", "uns", "umas", "novo", "nova", "please", "quero",
    "preciso", "pode", "fazer", "feito", "meu", "minha", "nosso", "nossa",
    "projeto", "código", "codigo", "arquivo", "pasta", "o", "a", "de", "do",
    "da", "no", "na", "em", "com", "para", "que", "se", "é", "e", "ou",
    "esse", "essa", "este", "esta", "aquele", "aquela", "isso", "isto",
    "ele", "ela", "me", "te", "lhe", "nos", "kit", "hub", "rubi",
    "assistente", "ai", "ia", "head", "readme", "riad", "read",
    "redmi", "leiame", "documentação", "doc", "docs", "aí", "lá", "aqui",
    "público", "publico",
}


def _extrair_nome_repo(texto_usuario: str, t: str) -> str:
    """Extrai o nome do repositório da fala com múltiplas estratégias."""
    for gatilho in [
        "chamado", "chama", "chame", "nome", "intitulado", "intitulada",
        "se chama", "com nome", "de nome", "batizado", "batizada",
        "para o repo", "para o repositório", "para o repositorio",
        "repositório chamado", "repositorio chamado", "repo chamado",
        "criar o", "cria o", "novo repo", "novo repositório",
    ]:
        if gatilho in t:
            trecho = _extrair_apos(texto_usuario, gatilho)
            palavras = [p for p in trecho.split() if p.lower() not in _PALAVRAS_IGNORADAS]
            if palavras:
                return palavras[0].lower()

    palavras = [p for p in texto_usuario.split() if p.lower() not in _PALAVRAS_IGNORADAS]
    return palavras[-1].lower() if palavras else ""


def _extrair_repo_generico(texto_usuario: str) -> str:
    """Extrai nome de repo para comandos de README, issues, etc."""
    gatilhos = [
        "para o repositório", "para o repositorio",
        "do repositório", "do repositorio",
        "no repositório", "no repositorio",
        "o repositório", "o repositorio",
        "repositório chamado", "repositorio chamado",
        "para o repo", "do repo", "no repo", "o repo",
        "projeto chamado", "projeto",
        "para a", "chamado", "chama",
    ]
    for gatilho in gatilhos:
        trecho = _extrair_apos(texto_usuario, gatilho)
        palavras = [p for p in trecho.split()
                    if p.lower() not in {"o", "a", "do", "da", "de", "um",
                                         "uma", "público", "publico", "privado"}]
        if palavras:
            return palavras[0].lower()
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

async def processar_comando_github(texto_usuario: str) -> str | None:
    if not GITHUB_TOKEN:
        return None

    t = texto_usuario.lower()

    # Perguntas conceituais → deixa para a IA responder
    perguntas_conceituais = [
        "o que é", "o que são", "explique", "explica", "me explique",
        "como funciona", "como funcionam", "para que serve", "pra que serve",
        "me ensina", "me ensine", "o que significa", "definição de",
        "diferença entre", "como usar", "como se usa",
    ]
    if any(p in t for p in perguntas_conceituais):
        return None

    # ── FLAGS DE INTENÇÃO ─────────────────────────────────────────────────────

    tem_repo = any(p in t for p in [
        "repositório", "repositorio", "repo", "repositórios", "repositorios",
        "projeto", "projetos", "rep",
    ])

    tem_listar = any(p in t for p in [
        "listar", "lista", "ver", "mostrar", "mostra", "quais", "quantos",
        "tenho", "meus", "meu", "exibir", "exibe", "apresentar", "apresenta",
        "me mostra", "me diz", "me fala", "quero ver", "quero saber",
        "me lista", "me listar", "mostre", "mostre-me", "diz quais",
        "fala quais", "quero saber", "me informa", "informa", "informa quais",
        "existem", "existe", "tenho", "há", "tem", "lixo", "ligo", "ligue",
    ])

    tem_criar = any(p in t for p in [
        "criar", "cria", "novo", "nova", "criar um", "cria um", "iniciar",
        "inicia", "abrir", "abre", "fazer", "faz", "adicionar", "adiciona",
        "quero criar", "preciso criar", "pode criar", "me cria", "me criar",
        "gostaria de criar", "queria criar", "vou criar", "bora criar",
        "start", "inicializar", "inicializa", "montar", "monta",
    ])

    tem_issue = any(p in t for p in [
        "issue", "issues", "tarefa", "tarefas", "bug", "bugs", "problema",
        "problemas", "ticket", "tickets", "atividade", "atividades",
        "pendência", "pendencias", "pendência", "to do", "todo",
    ])

    tem_commit = any(p in t for p in [
        "commit", "commitar", "commita", "subir arquivo", "sobe arquivo",
        "enviar arquivo", "envia arquivo", "push arquivo", "salvar arquivo",
        "salva arquivo", "fazer push", "faz push", "mandar arquivo",
        "manda arquivo", "versionar", "versiona",
    ])

    tem_readme = any(p in t for p in [
        "readme", "read me", "readmi", "readm",
        "redmi", "riad", "riad me", "ride me", "ride",
        "head me", "headme", "hed me", "red me", "réd me",
        "rim", "rime", "reame", "radme", "lida me", "lidame",
        "ridmi", "ridme", "riame", "read mi",
        "leiame", "leia me", "léia me",
        "documentação", "documentacao", "documenta", "documentar",
        "gerar doc", "gera doc", "criar doc", "cria doc",
        "descrição do projeto", "descricao do projeto",
        "apresentação do projeto", "sobre o projeto",
        "explicar o projeto", "explica o projeto",
        "descrever o projeto", "descreve o projeto",
        "apresentar o projeto", "apresenta o projeto",
    ])

    tem_fechar = any(p in t for p in [
        "fechar", "fecha", "encerrar", "encerra", "resolver", "resolve",
        "concluir", "conclui", "finalizar", "finaliza", "completar", "completa",
        "marcar como resolvido", "marcar resolvido", "marcar como feito",
        "fechar a", "fecha a", "done", "concluída", "concluido",
        "resolvida", "resolvido", "terminada", "terminado",
    ])

    tem_github = any(p in t for p in [
        "github", "git hub", "git", "kit hub", "kit rubi", "kit ru",
        "github.com", "meu git", "no git", "gitub", "githb",
    ])

    tem_info_repo = any(p in t for p in [
        "do que se trata", "me fala sobre", "me conta sobre",
        "o que tem", "o que contém", "tem algum", "existe algum",
        "tem arquivo", "tem código", "descreve", "descreva",
    ])

    # Sem contexto GitHub → passa para IA
    if not tem_repo and not tem_issue and not tem_commit and not tem_readme and not tem_github:
        return None

    # ── README ────────────────────────────────────────────────────────────────
    if tem_readme:
        repo = _extrair_repo_generico(texto_usuario)
        if not repo:
            return "Qual é o nome do repositório para eu gerar o README?"
        return await gerar_readme(repo)

    # ── INFORMAÇÕES SOBRE REPO ────────────────────────────────────────────────
    if tem_info_repo and tem_repo:
        repo = _extrair_repo_generico(texto_usuario)
        if repo:
            return await gerar_readme(repo)
        return await listar_repos()

    # ── LISTAR REPOSITÓRIOS ───────────────────────────────────────────────────
    if tem_repo and tem_listar and not tem_criar and not tem_issue:
        return await listar_repos()

    frases_listar_diretas = [
        "quais repos", "quais repositórios", "quais repositorios",
        "meus repos", "meus repositórios", "meus repositorios",
        "ver repos", "ver repositórios", "ver repositorios",
        "mostra repos", "mostra repositórios", "mostra repositorios",
        "lista repos", "lista repositórios", "lista repositorios",
        "repositórios que tenho", "repositorios que tenho",
        "quantos repos", "quantos repositórios", "quantos repositorios",
        "acesse meu github", "acessa meu github", "abre meu github",
        "meus projetos no github", "projetos no github",
        "repositórios no github", "repositorios no github",
        "repos no github", "repos do github",
    ]
    if any(f in t for f in frases_listar_diretas):
        return await listar_repos()

    # ── CRIAR REPOSITÓRIO ─────────────────────────────────────────────────────
    if tem_repo and tem_criar and not tem_listar and not tem_readme and not tem_issue:
        privado = any(p in t for p in [
            "privado", "privada", "secreto", "secreta", "private",
            "só pra mim", "so pra mim", "restrito", "restrita",
        ])
        nome = _extrair_nome_repo(texto_usuario, t)
        if not nome:
            return "Qual nome você quer dar ao repositório?"
        return await criar_repo(nome, privado)

    # ── COMMIT DE ARQUIVO ─────────────────────────────────────────────────────
    if tem_commit:
        arquivo  = _extrair_entre(texto_usuario, "arquivo", "no repo")
        repo     = _extrair_entre(texto_usuario, "no repo", "com mensagem")
        mensagem = _extrair_apos(texto_usuario, "com mensagem")

        if not repo:
            repo = _extrair_entre(texto_usuario, "repositório", "com mensagem") or \
                   _extrair_entre(texto_usuario, "repositorio", "com mensagem") or \
                   _extrair_entre(texto_usuario, "repo", "com mensagem")
        if not mensagem:
            mensagem = _extrair_apos(texto_usuario, "mensagem") or \
                       _extrair_apos(texto_usuario, "commit") or \
                       _extrair_apos(texto_usuario, "com a mensagem")

        if not arquivo or not repo or not mensagem:
            return (
                "Para fazer um commit, diga: "
                "fazer commit do arquivo NOME no repo REPOSITORIO com mensagem MENSAGEM."
            )
        return await commit_arquivo(repo.strip(), arquivo.strip(), "", mensagem.strip())

    # ── CRIAR ISSUE ───────────────────────────────────────────────────────────
    if tem_issue and tem_criar:
        repo = ""
        titulo = ""

        gatilhos_repo = [
            "no repo", "no repositório", "no repositorio",
            "em repo", "para o repo", "do repo",
            "repositório", "repositorio", "repo",
        ]
        gatilhos_titulo = [
            "com título", "com titulo", "título", "titulo",
            "chamada", "chamado", "intitulada", "intitulado",
            "sobre", "descrevendo", "dizendo",
        ]

        for gr in gatilhos_repo:
            for gt in gatilhos_titulo:
                repo   = _extrair_entre(texto_usuario, gr, gt)
                titulo = _extrair_apos(texto_usuario, gt)
                if repo and titulo:
                    break
            if repo and titulo:
                break

        if not repo or not titulo:
            return "Para criar uma issue, diga: criar issue no repo NOME com título TITULO."
        return await criar_issue(repo.strip(), titulo.strip())

    # ── FECHAR ISSUE ──────────────────────────────────────────────────────────
    if tem_issue and tem_fechar:
        numero = _extrair_numero(texto_usuario)
        repo = ""

        for gatilho in [
            "no repo", "no repositório", "no repositorio",
            "do repo", "do repositório", "do repositorio",
            "repo", "repositório", "repositorio",
        ]:
            trecho = _extrair_apos(texto_usuario, gatilho)
            candidato = trecho.split()[0] if trecho.split() else ""
            if candidato and candidato.lower() not in {"o", "a", "do", "da", "de"}:
                repo = candidato.lower()
                break

        if not numero or not repo:
            return "Para fechar uma issue, diga: fechar issue número NUMERO no repo REPOSITORIO."
        return await fechar_issue(repo, numero)

    # ── LISTAR ISSUES ─────────────────────────────────────────────────────────
    if tem_issue and (tem_repo or tem_listar) and not tem_criar and not tem_fechar:
        repo = ""
        for gatilho in [
            "do repo", "no repo", "do repositório", "no repositório",
            "do repositorio", "no repositorio", "de repo",
            "repo", "repositório", "repositorio", "projeto",
        ]:
            trecho = _extrair_apos(texto_usuario, gatilho)
            candidato = trecho.split()[0] if trecho.split() else ""
            if candidato and candidato.lower() not in {"o", "a", "do", "da", "de"}:
                repo = candidato.lower()
                break

        if not repo:
            return "Qual é o nome do repositório que você quer ver as issues?"
        return await listar_issues(repo)

    return None
