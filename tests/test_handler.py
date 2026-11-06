import json
from decimal import Decimal
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from serverless_reclamacoes.handler import handler

EXEMPLO = Path(__file__).parent.parent / "dados" / "exemplo.csv"
BUCKET = "reclamacoes-teste"


@pytest.fixture
def nuvem(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "teste")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "teste")
    monkeypatch.setenv("TABELA", "resumo")
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=BUCKET)
        dynamo = boto3.resource("dynamodb")
        dynamo.create_table(
            TableName="resumo",
            KeySchema=[
                {"AttributeName": "empresa", "KeyType": "HASH"},
                {"AttributeName": "arquivo", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "empresa", "AttributeType": "S"},
                {"AttributeName": "arquivo", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield s3, dynamo.Table("resumo")


def evento(chave):
    return {"Records": [{"s3": {"bucket": {"name": BUCKET}, "object": {"key": chave}}}]}


def test_handler_grava_s3_e_dynamo(nuvem):
    s3, tabela = nuvem
    s3.put_object(Bucket=BUCKET, Key="entrada/out-2026.csv", Body=EXEMPLO.read_bytes())
    assert handler(evento("entrada/out-2026.csv")) == {"empresas": 3}
    saida = json.loads(s3.get_object(Bucket=BUCKET, Key="resumo/out-2026.json")["Body"].read())
    assert saida["Telecom Beta"]["nota_media"] == 4.0
    item = tabela.get_item(Key={"empresa": "Banco Alfa", "arquivo": "out-2026"})["Item"]
    assert item["reclamacoes"] == 3
    assert item["nota_media"] == Decimal("2.33")


def test_chave_com_espaco_codificada(nuvem):
    s3, _ = nuvem
    s3.put_object(Bucket=BUCKET, Key="entrada/mes 10.csv", Body=EXEMPLO.read_bytes())
    assert handler(evento("entrada/mes+10.csv")) == {"empresas": 3}


def test_resumo_nao_dispara_de_novo(nuvem):
    s3, _ = nuvem
    s3.put_object(Bucket=BUCKET, Key="resumo/x.json", Body=b"{}")
    assert handler(evento("resumo/x.json")) == {"empresas": 0}


def test_csv_com_bom_do_excel(nuvem):
    s3, _ = nuvem
    s3.put_object(Bucket=BUCKET, Key="entrada/bom.csv", Body=b"\xef\xbb\xbf" + EXEMPLO.read_bytes())
    assert handler(evento("entrada/bom.csv")) == {"empresas": 3}
