"""Lógica da versão Azure Functions, sem depender do SDK: bytes entram, JSON sai."""

from __future__ import annotations

import json

from .nucleo import agregar

CONTAINER_ENTRADA = "entrada"
CONTAINER_SAIDA = "resumo"


def resumir_blob(nome: str, conteudo: bytes) -> tuple[str, str]:
    """Recebe o nome do blob (`entrada/abc.csv`) e seus bytes; devolve (nome_saida, json).

    O nome de saída vai para outro container, então o resumo não dispara a função de novo.
    """
    base = nome.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    resumo = agregar(conteudo.decode("utf-8-sig"))
    return f"{base}.json", json.dumps(resumo, ensure_ascii=False, indent=2)
