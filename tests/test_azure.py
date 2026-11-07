import json

import pytest

from serverless_reclamacoes.azure import resumir_blob

CSV = "empresa,assunto,estado,nota\nAcme,cobrança,SP,4\nAcme,cobrança,RJ,2\n"


def test_resumo_tem_nome_e_conteudo():
    nome, texto = resumir_blob("entrada/maio.csv", CSV.encode())
    assert nome == "maio.json"
    assert json.loads(texto)["Acme"]["reclamacoes"] == 2


def test_csv_com_bom_do_excel():
    _, texto = resumir_blob("maio.csv", b"\xef\xbb\xbf" + CSV.encode())
    assert "Acme" in json.loads(texto)


def test_coluna_ausente_levanta():
    with pytest.raises(ValueError, match="colunas ausentes"):
        resumir_blob("x.csv", b"empresa\nAcme\n")


def test_function_app_registra_gatilho():
    pytest.importorskip("azure.functions")
    import function_app

    funcoes = function_app.app.get_functions()
    assert [f.get_function_name() for f in funcoes] == ["resumir"]
