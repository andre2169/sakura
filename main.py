"""
SAKURÁ - Assistente de Voz
===========================
Entry point principal. Apenas inicializa e roda o loop.

Estrutura do projeto:
    main.py              ← você está aqui
    core/
        config.py        ← variáveis de ambiente e configurações globais
        loop.py          ← loop principal e roteamento de comandos
    voice/
        listener.py      ← captura e reconhecimento de voz
        speaker.py       ← síntese e reprodução de áudio (edge-tts)
    ai/
        groq_client.py   ← comunicação com a API da Groq (memória + contexto)
    github/
        client.py        ← autenticação e requisições base do GitHub
        repos.py         ← listar, criar repositórios
        issues.py        ← listar, criar, fechar issues
        commits.py       ← fazer commits de arquivos
        readme.py        ← gerar README com IA baseado no código do repositório
        router.py        ← detecta intenção de voz e roteia para a função certa
"""

import asyncio
import pygame
from core.loop import loop_principal


if __name__ == "__main__":
    try:
        asyncio.run(loop_principal())
    except KeyboardInterrupt:
        print("\n👋 SAKURÁ encerrada pelo usuário.")
    finally:
        pygame.mixer.quit()
