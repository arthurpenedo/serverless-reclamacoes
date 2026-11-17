from pathlib import Path

import pytest

from serverless_reclamacoes.nucleo import agregar

EXEMPLO = Path(__file__).parent.parent / "dados" / "exemplo.csv"


def test_agrega_exemplo():
    r = agregar(EXEMPLO.read_text(encoding="utf-8"))
    esperado = {"reclamacoes": 3, "nota_media": 2.33, "assunto_mais_comum": "Cobrança indevida"}
    assert r["Banco Alfa"] == esperado
    assert r["Loja Gama"]["reclamacoes"] == 1
    assert len(r) == 3


def test_nota_invalida_conta_mas_nao_entra_na_media():
    r = agregar("empresa,assunto,estado,nota\nX,a,SP,9\nX,a,SP,abc\nX,a,SP,4\n")
    assert r["X"]["reclamacoes"] == 3
    assert r["X"]["nota_media"] == 4.0


def test_nota_de_planilha_com_ponto_zero_ou_virgula_entra_na_media():
    r = agregar('empresa,assunto,estado,nota\nX,a,SP,4.0\nX,a,SP,"2,0"\nX,a,SP,3.5\nX,a,SP,nan\nX,a,SP,\n')
    assert r["X"]["reclamacoes"] == 5
    assert r["X"]["nota_media"] == 3.0  # só 4.0 e 2,0 valem; 3.5, nan e vazio ficam de fora


def test_sem_nota_valida_media_none():
    assert agregar("empresa,assunto,estado,nota\nX,a,SP,\n")["X"]["nota_media"] is None


def test_linha_sem_empresa_ignorada():
    assert agregar("empresa,assunto,estado,nota\n,a,SP,3\n") == {}


def test_coluna_ausente():
    with pytest.raises(ValueError, match="nota"):
        agregar("empresa,assunto,estado\nX,a,SP\n")
