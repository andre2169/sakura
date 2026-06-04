"""
github/router.py
================
Responsabilidade: detectar intenção GitHub na fala do usuário e rotear
para a função correta.

Regra: retorna uma string com a resposta, ou None se não for comando GitHub.
O loop principal em core/loop.py decide o que fazer com o retorno.
"""

from core.config import GITHUB_TOKEN
from github.repos  import listar_repos, criar_repo
from github.issues import listar_issues, criar_issue, fechar_issue
from github.commits import commit_arquivo
from github.readme import gerar_readme


def _extrair_apos(texto: str, palavra_chave: str) -> str:
    """Extrai tudo que vem depois de uma palavra-chave."""
    idx = texto.lower().find(palavra_chave.lower())
    if idx == -1:
        return ""
    return texto[idx + len(palavra_chave):].strip()


def _extrair_entre(texto: str, depois_de: str, antes_de: str | None) -> str:
    """Extrai trecho entre duas palavras-chave."""
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
    """Extrai o primeiro número inteiro encontrado no texto."""
    import re
    numeros = re.findall(r"\d+", texto)
    return int(numeros[0]) if numeros else None


async def processar_comando_github(texto_usuario: str) -> str | None:
    if not GITHUB_TOKEN:
        return None

    t = texto_usuario.lower()

    # ── Listar repositórios ───────────────────────────────────────────────────
    palavras_repo = ["repositório", "repositorio", "repo", "repositórios", "repositorios"]
    palavras_listar = ["listar", "lista", "ver", "mostrar", "mostra", "quais", "quantos", "tenho", "meus", "meu"]

    tem_repo   = any(p in t for p in palavras_repo)
    tem_listar = any(p in t for p in palavras_listar)
    tem_criar  = any(p in t for p in ["criar", "cria", "novo", "nova"])
    tem_issue  = any(p in t for p in ["issue", "issues"])
    tem_commit = any(p in t for p in ["commit", "commitar", "commita"])
    tem_readme = any(p in t for p in ["readme", "read me"])
    tem_fechar = any(p in t for p in ["fechar", "fecha", "fechar", "encerrar"])

    # Listar repos: qualquer menção a "repo/repositório" + intenção de ver
    if tem_repo and tem_listar and not tem_criar and not tem_issue:
        return await listar_repos()

    # ── Criar repositório ─────────────────────────────────────────────────────
    if tem_repo and tem_criar:
        privado = "privado" in t

        nome = ""
        for gatilho in ["chamado", "nome", "chama"]:
            if gatilho in t:
                trecho = _extrair_apos(texto_usuario, gatilho)
                palavras = [p for p in trecho.split() if p.lower() not in
                           ["privado", "público", "publico", "agora", "por", "favor"]]
                if palavras:
                    nome = palavras[0]
                    break

        if not nome:
            palavras_filtradas = [p for p in texto_usuario.split() if p.lower() not in
                       ["privado", "público", "publico", "agora", "por", "favor",
                        "criar", "cria", "repositório", "repositorio", "repo",
                        "um", "uma", "novo", "nova", "sakura", "github"]]
            nome = palavras_filtradas[-1] if palavras_filtradas else ""

        if not nome:
            return "Qual nome você quer dar ao repositório?"
        return await criar_repo(nome.lower(), privado)

    # ── Gerar README ──────────────────────────────────────────────────────────
    if tem_readme and tem_repo:
        repo = _extrair_apos(texto_usuario, "repo") or _extrair_apos(texto_usuario, "para")
        repo = repo.split()[0] if repo else ""
        if not repo:
            return "Qual é o nome do repositório para gerar o README?"
        return await gerar_readme(repo)

    # ── Fazer commit ──────────────────────────────────────────────────────────
    if tem_commit:
        arquivo  = _extrair_entre(texto_usuario, "arquivo", "no repo")
        repo     = _extrair_entre(texto_usuario, "no repo", "com mensagem")
        mensagem = _extrair_apos(texto_usuario, "com mensagem")
        if not arquivo or not repo or not mensagem:
            return "Para fazer um commit, diga: fazer commit do arquivo NOME no repo REPOSITORIO com mensagem MENSAGEM."
        return await commit_arquivo(repo.strip(), arquivo.strip(), "", mensagem.strip())

    # ── Criar issue ───────────────────────────────────────────────────────────
    if tem_issue and tem_criar:
        repo   = _extrair_entre(texto_usuario, "repo", "com título") or \
                 _extrair_entre(texto_usuario, "repo", "com titulo")
        titulo = _extrair_apos(texto_usuario, "com título") or \
                 _extrair_apos(texto_usuario, "com titulo")
        if not repo or not titulo:
            return "Para criar uma issue, diga: criar issue no repo NOME com título TITULO."
        return await criar_issue(repo.strip(), titulo.strip())

    # ── Fechar issue ──────────────────────────────────────────────────────────
    if tem_issue and tem_fechar:
        numero = _extrair_numero(texto_usuario)
        repo   = _extrair_apos(texto_usuario, "no repo")
        repo   = repo.split()[0] if repo else ""
        if not numero or not repo:
            return "Para fechar uma issue, diga: fechar issue número NUMERO no repo REPOSITORIO."
        return await fechar_issue(repo, numero)

    # ── Listar issues ─────────────────────────────────────────────────────────
    if tem_issue and tem_repo and not tem_criar and not tem_fechar:
        repo = _extrair_apos(texto_usuario, "repo")
        repo = repo.split()[0] if repo else ""
        if not repo:
            return "Qual é o nome do repositório que você quer ver as issues?"
        return await listar_issues(repo)

    return None