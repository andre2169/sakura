"""
core/loop.py
============
Loop principal da SAKURÁ.
Responsabilidade: orquestrar escuta → roteamento → resposta.
Não contém lógica de negócio — delega para os módulos especializados.
"""

import asyncio
import pygame

from core.config import validar_config
from voice.listener import ouvir, warmup_reconhecedor
from voice.speaker import falar
from ai.groq_client import gerar_resposta
from github.router import processar_comando_github
from core.localizacao import buscar_localizacao, formatar_localizacao

# Estado global de fala (compartilhado entre listener e speaker)
esta_falando   = False
dados_localizacao: dict = {}

PALAVRAS_SAIDA = ["tchau", "desligar", "encerrar", "sair"]


async def loop_principal():
    global dados_localizacao

    validar_config()
    pygame.mixer.init()
    print("🌸 Iniciando SAKURÁ...")

    # Inicialização paralela: localização + calibração do microfone
    dados_localizacao, _ = await asyncio.gather(
        buscar_localizacao(),
        asyncio.to_thread(warmup_reconhecedor)
    )

    loc_texto = formatar_localizacao(dados_localizacao)
    await falar("Olá, eu sou a SAKURÁ! Estou pronta para te ajudar.")

    while True:
        texto_usuario = await asyncio.to_thread(ouvir)

        if not texto_usuario:
            continue

        # Encerramento
        if any(p in texto_usuario.lower() for p in PALAVRAS_SAIDA):
            await falar("Foi um prazer ajudar! Até logo.")
            break

        # Tenta rotear para GitHub primeiro
        resposta_github = await processar_comando_github(texto_usuario)
        if resposta_github:
            await falar(resposta_github)
            continue

        # Fallback: IA generativa
        resposta = await asyncio.to_thread(gerar_resposta, texto_usuario, loc_texto)
        await falar(resposta)
