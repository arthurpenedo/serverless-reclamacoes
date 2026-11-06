"""Função Lambda: lê o CSV que chegou no S3, agrega e grava o resumo (S3 + DynamoDB)."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from urllib.parse import unquote_plus

import boto3

from .nucleo import agregar

PREFIXO_ENTRADA = "entrada/"
PREFIXO_SAIDA = "resumo/"


def _para_dynamo(valor):
    """DynamoDB não aceita float: converte para Decimal."""
    if isinstance(valor, float):
        return Decimal(str(valor))
    return valor


def processar(s3, tabela, bucket: str, chave: str) -> int:
    """Processa um objeto; devolve quantas empresas foram gravadas."""
    texto = s3.get_object(Bucket=bucket, Key=chave)["Body"].read().decode("utf-8-sig")
    resumo = agregar(texto)
    nome = chave.removeprefix(PREFIXO_ENTRADA).rsplit(".", 1)[0]
    s3.put_object(
        Bucket=bucket,
        Key=f"{PREFIXO_SAIDA}{nome}.json",
        Body=json.dumps(resumo, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    with tabela.batch_writer() as lote:
        for empresa, dados in resumo.items():
            item = {"empresa": empresa, "arquivo": nome}
            for campo, valor in dados.items():
                if valor is not None:
                    item[campo] = _para_dynamo(valor)
            lote.put_item(Item=item)
    return len(resumo)


def handler(event, context=None):
    s3 = boto3.client("s3")
    tabela = boto3.resource("dynamodb").Table(os.environ["TABELA"])
    gravadas = 0
    for registro in event.get("Records", []):
        bucket = registro["s3"]["bucket"]["name"]
        chave = unquote_plus(registro["s3"]["object"]["key"])
        if not chave.startswith(PREFIXO_ENTRADA):  # evita laço: o resumo não dispara de novo
            continue
        gravadas += processar(s3, tabela, bucket, chave)
    return {"empresas": gravadas}
