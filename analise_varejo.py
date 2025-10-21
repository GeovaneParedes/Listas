#!/usr/bin/env python3
import pandas as pd
import os
from typing import Dict, Any
import matplotlib.pyplot as plt

# --- Variáveis de Configuração ---
ARQUIVO_TRANSACOES = "transacoes.csv"
PASTA_IMAGEM = "imagens"


def _carregar_dados_com_seguranca(caminho_arquivo: str) -> pd.DataFrame:
    """
    Carrega um arquivo CSV e trata erros de I/O e estrutura (robustez).
    
    Args:
        caminho_arquivo: Caminho completo para o arquivo CSV.

    Returns:
        Um DataFrame do Pandas, ou um DataFrame vazio em caso de erro.
    """
    try:
        df = pd.read_csv(caminho_arquivo, sep=',')
        return df
    except FileNotFoundError:
        print(f"ERRO SÊNIOR: Arquivo não encontrado em {caminho_arquivo}. Retornando DataFrame vazio.")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRO SÊNIOR: Falha ao carregar {caminho_arquivo}. Detalhes: {e}")
        return pd.DataFrame()


def analisar_vendas(df_transacoes: pd.DataFrame) -> Dict[str, Any]:
    """
    Realiza a análise de vendas e retorna dados agregados (O(n)).
    
    Args:
        df_transacoes: DataFrame carregado com os dados de transação.

    Returns:
        Um dicionário contendo a série de Performance por Mês/Ano.
    """
    if df_transacoes.empty:
        return {}
        
    # Limpeza e Preparação dos Dados (Clean Code)
    df_transacoes['data_hora'] = pd.to_datetime(df_transacoes['data_hora'])
    df_transacoes['receita'] = df_transacoes['quantidade'] * df_transacoes['valor_unitario']
    df_transacoes['mes_ano'] = df_transacoes['data_hora'].dt.to_period('M').astype(str)

    # Análise por Mês (Eficiência Algorítmica)
    vendas_por_mes = df_transacoes.groupby('mes_ano')['receita'].sum().sort_index()

    return {
        "Performance por Mês/Ano": vendas_por_mes
    }


def gerar_grafico_performance_mensal(vendas_mensais: pd.Series, pasta_saida: str, nome_arquivo: str):
    """
    Gera um gráfico de barras da performance de vendas mensal e salva.
    Garante que a pasta de destino exista (Tratamento Robusto).
    
    Args:
        vendas_mensais: Série do Pandas com o índice sendo o mês/ano e os valores a receita.
        pasta_saida: Nome da pasta onde o gráfico será salvo.
        nome_arquivo: Nome do arquivo de imagem (ex: 'vendas_mensais.png').
    """
    if vendas_mensais.empty:
        print("AVISO SÊNIOR: Não há dados de vendas para gerar o gráfico.")
        return

    # Tratamento Robusto: Cria a pasta se não existir (Zero Gambiarra)
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)
    
    plt.figure(figsize=(10, 6))
    
    # Geração do gráfico de barras
    vendas_mensais.plot(kind='bar', color='skyblue', edgecolor='black')
    
    plt.title('Performance de Receita por Mês/Ano', fontsize=16)
    plt.xlabel('Mês/Ano', fontsize=12)
    plt.ylabel('Receita Total (R$)', fontsize=12)
    plt.xticks(rotation=0) 
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adiciona rótulos de valor para clareza
    for i, v in enumerate(vendas_mensais.values):
        plt.text(i, v + 1, f'R$ {v:.2f}', ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    
    try:
        # Salvamento da Imagem
        plt.savefig(caminho_completo)
    except Exception as e:
        print(f"ERRO SÊNIOR: Falha ao salvar o gráfico. Detalhes: {e}")
    finally:
        plt.close()


# --- Exemplo de Uso (Fluxo de Desenvolvimento) ---
if __name__ == "__main__":
    
    # Simulação de Carregamento
    df_vendas = _carregar_dados_com_seguranca(ARQUIVO_TRANSACOES)
    
    # Execução da Análise
    relatorio_vendas = analisar_vendas(df_vendas)
    vendas_mensais = relatorio_vendas.get("Performance por Mês/Ano")

    # Geração do Gráfico
    if isinstance(vendas_mensais, pd.Series):
        gerar_grafico_performance_mensal(
            vendas_mensais, 
            PASTA_IMAGEM, 
            "vendas_por_mes.png"
        )