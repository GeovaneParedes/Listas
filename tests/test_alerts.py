import os
import pandas as pd
import pytest
from alerts import (
    verificar_vencimento,
    verificar_parado,
    carregar_estoque,
    gerar_alertas_e_enviar,
)


@pytest.fixture
def estoque_tmp(tmp_path):
    data = """produto,quantidade_estoque,data_vencimento,dias_parado
Leite,10,2099-01-01,5
Pao,5,2000-01-01,200
"""
    p = tmp_path / "estoque.csv"
    p.write_text(data)
    return str(p)


def test_carregar_estoque_ok(estoque_tmp):
    df = carregar_estoque(estoque_tmp)
    assert not df.empty
    assert "produto" in df.columns


def test_verificar_vencimento(estoque_tmp, monkeypatch):
    df = carregar_estoque(estoque_tmp)
    old_now = pd.Timestamp("now")
    # for deterministic: just call function and expect at least one expired (2000-01-01)
    res = verificar_vencimento(df, dias_alerta=36500)
    assert "Pao" in res["produto"].values


def test_verificar_parado(estoque_tmp):
    df = carregar_estoque(estoque_tmp)
    res = verificar_parado(df, dias_parado_threshold=100)
    assert "Pao" in res["produto"].values


def test_gerar_alertas_sem_smtp(estoque_tmp, monkeypatch):
    # ensure SMTP env not set -> should not crash and returned enviado False
    for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS"):
        monkeypatch.delenv(k, raising=False)
    resp = gerar_alertas_e_enviar(estoque_tmp, ["ops@teste.local"])
    assert isinstance(resp, dict)
    assert resp["enviado"] is False
