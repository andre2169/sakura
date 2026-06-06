"""
memory/sqlite.py
================
Implementação concreta da memória usando SQLite.
NÃO importe este arquivo diretamente — use memory/repository.py.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sakura_memoria.db")


class SQLiteMemory:

    def __init__(self):
        self.db_path = os.path.abspath(DB_PATH)

    def _conectar(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
        return conn

    def inicializar(self):
        """Cria a tabela de mensagens se não existir."""
        with self._conectar() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensagens (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    role      TEXT    NOT NULL,
                    content   TEXT    NOT NULL,
                    criado_em TEXT    NOT NULL
                )
            """)
            conn.commit()
        print(f"🗄️  Banco de dados iniciado em: {self.db_path}")

    def salvar_mensagem(self, role: str, content: str):
        """Persiste uma mensagem no banco com timestamp."""
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            conn.execute(
                "INSERT INTO mensagens (role, content, criado_em) VALUES (?, ?, ?)",
                (role, content, agora)
            )
            conn.commit()

    def carregar_historico(self, limite: int = 20) -> list[dict]:
        """
        Retorna as últimas `limite` mensagens que NÃO sejam system,
        na ordem correta (mais antigas primeiro).
        """
        with self._conectar() as conn:
            rows = conn.execute("""
                SELECT role, content FROM mensagens
                WHERE role != 'system'
                ORDER BY id DESC
                LIMIT ?
            """, (limite,)).fetchall()

        # Inverte para ficar na ordem cronológica correta
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def carregar_system_prompt(self) -> dict | None:
        """Retorna o system prompt mais recente salvo no banco."""
        with self._conectar() as conn:
            row = conn.execute("""
                SELECT role, content FROM mensagens
                WHERE role = 'system'
                ORDER BY id DESC
                LIMIT 1
            """).fetchone()

        if row:
            return {"role": row["role"], "content": row["content"]}
        return None

    def limpar_historico(self):
        """Apaga todas as mensagens do banco."""
        with self._conectar() as conn:
            conn.execute("DELETE FROM mensagens")
            conn.commit()
        print("🗑️  Histórico de memória apagado.")
