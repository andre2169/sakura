"""
memory/repository.py
====================
Interface genérica de memória — o resto do projeto importa APENAS daqui.
Para trocar de banco, basta mudar a linha de importação no final do arquivo.
Nunca importe sqlite.py diretamente em outros módulos.
"""

from memory.sqlite import SQLiteMemory

# ── Instância global (singleton) ─────────────────────────────────────────────
# Trocar de banco no futuro = trocar só essa linha
_memory = SQLiteMemory()


def inicializar():
    """Cria as tabelas se ainda não existirem. Chamar uma vez na inicialização."""
    _memory.inicializar()


def salvar_mensagem(role: str, content: str):
    """
    Persiste uma mensagem no banco.
    role: 'system' | 'user' | 'assistant'
    """
    _memory.salvar_mensagem(role, content)


def carregar_historico(limite: int = 20) -> list[dict]:
    """
    Retorna as últimas `limite` mensagens (excluindo system) como lista de dicts
    no formato esperado pela Groq: [{"role": ..., "content": ...}]
    """
    return _memory.carregar_historico(limite)


def carregar_system_prompt() -> dict | None:
    """Retorna o system prompt salvo, ou None se não existir."""
    return _memory.carregar_system_prompt()


def limpar_historico():
    """Apaga todas as mensagens do banco. Útil para resetar a memória."""
    _memory.limpar_historico()
