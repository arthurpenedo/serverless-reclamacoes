"""Regra de negócio pura (sem AWS): agrega o CSV de reclamações por empresa."""

from __future__ import annotations

import csv
import io
from collections import defaultdict

COLUNAS = ("empresa", "assunto", "estado", "nota")


def agregar(texto_csv: str) -> dict[str, dict]:
    """Devolve {empresa: {reclamacoes, nota_media, assunto_mais_comum}}.

    Linhas sem empresa são ignoradas; só notas de 1 a 5 entram na média.
    Falta de coluna obrigatória levanta ValueError.
    """
    leitor = csv.DictReader(io.StringIO(texto_csv))
    faltam = [c for c in COLUNAS if c not in (leitor.fieldnames or [])]
    if faltam:
        raise ValueError(f"colunas ausentes: {', '.join(faltam)}")
    notas: dict[str, list[int]] = defaultdict(list)
    assuntos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total: dict[str, int] = defaultdict(int)
    for linha in leitor:
        empresa = (linha["empresa"] or "").strip()
        if not empresa:
            continue
        total[empresa] += 1
        assuntos[empresa][(linha["assunto"] or "").strip() or "sem assunto"] += 1
        try:
            nota = int(linha["nota"])
        except (TypeError, ValueError):
            continue
        if 1 <= nota <= 5:
            notas[empresa].append(nota)
    resumo = {}
    for empresa, n in total.items():
        lista = notas[empresa]
        resumo[empresa] = {
            "reclamacoes": n,
            "nota_media": round(sum(lista) / len(lista), 2) if lista else None,
            "assunto_mais_comum": max(assuntos[empresa].items(), key=lambda kv: (kv[1], kv[0]))[0],
        }
    return resumo
