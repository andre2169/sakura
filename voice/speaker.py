"""
voice/speaker.py
================
Responsabilidade: sintetizar texto em fala e reproduzir o áudio.
Usa edge-tts (vozes neurais Microsoft) + pygame para reprodução.
"""

import asyncio
import os
import re
import tempfile
import time

import edge_tts
import pygame

from core.config import VOZ_BRASILEIRA, VOZ_VELOCIDADE

_deve_interromper = False
_esta_falando     = False


def esta_falando() -> bool:
    return _esta_falando


def interromper():
    global _deve_interromper
    _deve_interromper = True


def limpar_texto(texto: str) -> str:
    """Remove markdown e símbolos que atrapalham a leitura em voz alta."""
    texto = re.sub(r"[*#`\"\\]", "", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.strip()


async def _sintetizar(texto: str, caminho: str):
    communicate = edge_tts.Communicate(texto, VOZ_BRASILEIRA, rate=VOZ_VELOCIDADE)
    await communicate.save(caminho)


def _reproduzir(caminho: str):
    global _deve_interromper, _esta_falando
    try:
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if _deve_interromper:
                pygame.mixer.music.stop()
                print("\n🛑 Você interrompeu a SAKURÁ")
                break
            time.sleep(0.05)
    finally:
        pygame.mixer.music.unload()
        _esta_falando = False


async def falar(texto: str):
    """Pipeline completo: limpa texto → sintetiza → reproduz → limpa arquivo."""
    global _deve_interromper, _esta_falando

    texto_limpo = limpar_texto(texto)
    print(f"\n🔊 Sakura: {texto_limpo}")

    _deve_interromper = False
    _esta_falando     = True

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        caminho_tmp = tmp.name

    try:
        await _sintetizar(texto_limpo, caminho_tmp)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _reproduzir, caminho_tmp)
    finally:
        if os.path.exists(caminho_tmp):
            try:
                os.remove(caminho_tmp)
            except PermissionError:
                pass  # pygame ainda segura o arquivo — será limpo pelo SO depois
