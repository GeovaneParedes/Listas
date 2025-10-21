import pytest
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from analise_varejo import (
    _carregar_dados_com_seguranca,
    analisar_vendas,
    gerar_grafico_performance_mensal,
)


def test_hello_world():
    assert 1 + 1 == 2


@pytest.fixture
def df_transacoes_teste():
    return pd.DataFrame(
        {
            'id_transacao': ['T0001', 'T0002'],
            'data_hora': ['2025-01-10 09:00:00', '2025-01-15 15:30:00'],
            'produto': ['Leite Integral 1L', 'Pão de Forma'],
            'quantidade': [2, 1],
            'valor_unitario': [5.00, 8.00],
        }
    )


@pytest.fixture
def df_estoque_teste():
    return pd.DataFrame(
        {
            'produto': ['Leite Integral 1L', 'Pão de Forma'],
            'quantidade_estoque': [50, 10],
            'data_vencimento': ['2025-04-30', '2025-03-25'],
            'dias_parado': [45, 10],
        }
    )


def test_carregar_dados_com_seguranca():
    # Test com arquivo válido
    df = _carregar_dados_com_seguranca('transacoes.csv')
    assert not df.empty
    assert all(
        col in df.columns for col in ['id_transacao', 'data_hora', 'produto']
    )

    # Test com arquivo inválido
    df_invalido = _carregar_dados_com_seguranca('arquivo_inexistente.csv')
    assert df_invalido.empty


def test_carregar_dados_com_seguranca_error_handling():
    """Test error handling in data loading function"""
    # Test with corrupt file
    with open('corrupt.csv', 'w') as f:
        f.write(
            'invalid,csv,format\n1,2\n'
        )  # Malformed CSV without required columns

    df = _carregar_dados_com_seguranca('corrupt.csv')
    assert df.empty, "Should return empty DataFrame for malformed CSV"

    # Cleanup
    os.remove('corrupt.csv')


def test_carregar_dados_com_seguranca_encoding_error():
    """Test handling of encoding errors in data loading"""
    # Create a file with invalid encoding
    with open('invalid_encoding.csv', 'wb') as f:
        f.write(b'\x80\x81\x82\n\x80\x81\x82')

    df = _carregar_dados_com_seguranca('invalid_encoding.csv')
    assert df.empty

    # Cleanup
    os.remove('invalid_encoding.csv')


def test_analisar_vendas(df_transacoes_teste):
    resultado = analisar_vendas(df_transacoes_teste)
    assert 'Performance por Mês/Ano' in resultado
    assert not resultado['Performance por Mês/Ano'].empty
    assert resultado['Performance por Mês/Ano'].sum() == (2 * 5.00 + 1 * 8.00)


def test_analisar_vendas_empty_df():
    """Test sales analysis with empty DataFrame"""
    empty_df = pd.DataFrame()
    result = analisar_vendas(empty_df)
    assert isinstance(result, dict), "Should return a dictionary"
    assert (
        "Performance por Mês/Ano" in result
    ), "Should contain performance key"
    assert result[
        "Performance por Mês/Ano"
    ].empty, "Should have empty performance series"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            pd.DataFrame(
                {
                    'id_transacao': ['T001'],
                    'data_hora': ['2025-01-01 00:00:00'],
                    'produto': ['Test Product'],
                    'quantidade': [0],
                    'valor_unitario': [0],
                }
            ),
            0.0,
        ),
        (
            pd.DataFrame(
                {
                    'id_transacao': ['T002'],
                    'data_hora': ['2025-01-01 00:00:00'],
                    'produto': ['Test Product'],
                    'quantidade': [1],
                    'valor_unitario': [10.0],
                }
            ),
            10.0,
        ),
    ],
)
def test_analisar_vendas_parametrized(test_input, expected):
    """Test sales analysis with different input scenarios"""
    result = analisar_vendas(test_input)
    assert result["Performance por Mês/Ano"].sum() == expected


def test_analisar_vendas_invalid_dates(df_transacoes_teste):
    """Test handling of invalid dates in sales analysis"""
    df_invalido = df_transacoes_teste.copy()
    df_invalido.loc[0, 'data_hora'] = 'invalid_date'

    resultado = analisar_vendas(df_invalido)
    assert 'Performance por Mês/Ano' in resultado
    assert not resultado['Performance por Mês/Ano'].empty


def test_analisar_vendas_exception_handling():
    """Test exception handling in sales analysis"""
    # Create DataFrame with invalid data types
    df_invalid = pd.DataFrame(
        {
            'data_hora': ['2025-01-01'],
            'quantidade': ['invalid'],  # Invalid type for multiplication
            'valor_unitario': [10.0],
        }
    )

    result = analisar_vendas(df_invalid)
    assert isinstance(result, dict)
    assert "Performance por Mês/Ano" in result
    assert result["Performance por Mês/Ano"].empty


def test_gerar_grafico_performance_mensal(df_transacoes_teste):
    # Setup
    pasta_teste = 'testes_output'
    arquivo_teste = 'test_grafico.png'

    # Test
    vendas_mensais = analisar_vendas(df_transacoes_teste)[
        'Performance por Mês/Ano'
    ]
    gerar_grafico_performance_mensal(
        vendas_mensais, pasta_teste, arquivo_teste
    )

    # Verify
    caminho_arquivo = os.path.join(pasta_teste, arquivo_teste)
    assert os.path.exists(caminho_arquivo)

    # Cleanup
    os.remove(caminho_arquivo)
    os.rmdir(pasta_teste)


def test_gerar_grafico_performance_mensal_invalid_path():
    """Test graph generation with invalid path"""
    vendas_mensais = pd.Series([100.0], index=['2025-01'])
    invalid_path = '/invalid/path'

    with pytest.raises(Exception):
        gerar_grafico_performance_mensal(
            vendas_mensais, invalid_path, 'test.png'
        )


@pytest.mark.parametrize(
    "invalid_path",
    ['/nonexistent/path/test.png', '', None],  # Empty path  # None path
)
def test_gerar_grafico_performance_mensal_invalid_paths(invalid_path):
    """Test graph generation with various invalid paths"""
    vendas_mensais = pd.Series([100.0], index=['2025-01'])

    with pytest.raises(Exception) as exc_info:
        gerar_grafico_performance_mensal(
            vendas_mensais, invalid_path, 'test.png'
        )

    assert "Erro ao gerar gráfico" in str(exc_info.value)


@pytest.fixture
def mock_matplotlib(monkeypatch):
    """Mock matplotlib for testing graph generation errors"""

    class MockPlt:
        @staticmethod
        def figure(*args, **kwargs):
            raise ValueError("Mock plot error")

    monkeypatch.setattr("matplotlib.pyplot", MockPlt)


def test_gerar_grafico_performance_mensal_plot_error(
    df_transacoes_teste, mock_matplotlib
):
    """Test error handling in graph generation"""
    vendas_mensais = analisar_vendas(df_transacoes_teste)[
        'Performance por Mês/Ano'
    ]

    with pytest.raises(Exception) as exc_info:
        gerar_grafico_performance_mensal(vendas_mensais, 'output', 'test.png')

    assert "Erro ao gerar gráfico" in str(exc_info.value)


def test_carregar_dados_com_seguranca_corrupt_file():
    """Test loading corrupted CSV file"""
    with open('corrupt.csv', 'w') as f:
        f.write('id_transacao,data_hora\n1,2\n')  # Missing required column

    df = _carregar_dados_com_seguranca('corrupt.csv')
    assert df.empty

    os.remove('corrupt.csv')


def test_analisar_vendas_invalid_calculation():
    """Test sales analysis with invalid calculation data"""
    df = pd.DataFrame(
        {
            'id_transacao': ['T001'],
            'data_hora': ['2025-01-01 00:00:00'],
            'produto': ['Test Product'],
            'quantidade': ['invalid'],  # Invalid quantity
            'valor_unitario': [10.0],
        }
    )

    result = analisar_vendas(df)
    assert isinstance(result, dict)
    assert "Performance por Mês/Ano" in result
    assert result["Performance por Mês/Ano"].empty


def test_gerar_grafico_performance_mensal_save_error(monkeypatch):
    """Test graph generation with save error"""

    def mock_savefig(*args, **kwargs):
        raise IOError("Mock save error")

    monkeypatch.setattr(plt, 'savefig', mock_savefig)

    vendas_mensais = pd.Series([100.0], index=['2025-01'])
    with pytest.raises(Exception) as exc_info:
        gerar_grafico_performance_mensal(
            vendas_mensais, 'test_output', 'test.png'
        )

    assert "Erro ao gerar gráfico" in str(exc_info.value)
