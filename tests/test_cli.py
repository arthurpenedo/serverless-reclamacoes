import json
from pathlib import Path

from serverless_reclamacoes.cli import main

EXEMPLO = Path(__file__).parent.parent / "dados" / "exemplo.csv"


def test_cli_imprime_json(capsys):
    assert main([str(EXEMPLO)]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["Telecom Beta"]["reclamacoes"] == 2


def test_cli_arquivo_inexistente(capsys, tmp_path):
    assert main([str(tmp_path / "nao-existe.csv")]) == 2
    assert "erro" in capsys.readouterr().err


def test_cli_arquivo_fora_de_utf8_da_mensagem_clara(capsys, tmp_path):
    latin = tmp_path / "latin.csv"
    latin.write_bytes("empresa,assunto,estado,nota\nAção,cobrança,SP,5\n".encode("latin-1"))
    assert main([str(latin)]) == 2
    assert "não está em UTF-8" in capsys.readouterr().err


def test_cli_coluna_ausente(capsys, tmp_path):
    ruim = tmp_path / "ruim.csv"
    ruim.write_text("empresa,assunto\nX,a\n", encoding="utf-8")
    assert main([str(ruim)]) == 2
    assert "colunas ausentes" in capsys.readouterr().err


def test_cli_csv_vazio_da_colunas_ausentes(capsys, tmp_path):
    vazio = tmp_path / "vazio.csv"
    vazio.write_text("", encoding="utf-8")
    assert main([str(vazio)]) == 2
    assert "colunas ausentes" in capsys.readouterr().err


def test_cli_notas_nan_e_inf_nao_entram_na_media(capsys, tmp_path):
    arq = tmp_path / "estranho.csv"
    arq.write_text("empresa,assunto,estado,nota\nX,a,SP,nan\nX,a,SP,inf\nX,a,SP,4\n", encoding="utf-8")
    assert main([str(arq)]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["X"]["reclamacoes"] == 3 and saida["X"]["nota_media"] == 4
