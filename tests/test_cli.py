import json
from pathlib import Path

from serverless_reclamacoes.cli import main

EXEMPLO = Path(__file__).parent.parent / "dados" / "exemplo.csv"


def test_cli_imprime_json(capsys):
    assert main([str(EXEMPLO)]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["Telecom Beta"]["reclamacoes"] == 2


def test_cli_arquivo_inexistente(capsys, tmp_path):
    assert main([str(tmp_path / "nao-existe.csv")]) == 1
    assert "erro" in capsys.readouterr().err


def test_cli_coluna_ausente(capsys, tmp_path):
    ruim = tmp_path / "ruim.csv"
    ruim.write_text("empresa,assunto\nX,a\n", encoding="utf-8")
    assert main([str(ruim)]) == 1
    assert "colunas ausentes" in capsys.readouterr().err
