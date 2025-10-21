#!/usr/bin/env python3
import os
import logging
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

# --- Variáveis de Configuração ---
ARQUIVO_TRANSACOES = "transacoes.csv"
PASTA_IMAGEM = "imagens"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def _carregar_dados_com_seguranca(caminho_arquivo: str) -> pd.DataFrame:
    """Carrega um arquivo CSV e trata erros de I/O e estrutura"""
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        # Validar colunas necessárias
        colunas_requeridas = ['id_transacao', 'data_hora', 'produto']
        if not all(col in df.columns for col in colunas_requeridas):
            logger.error(
                f"Colunas requeridas ausentes: "
                f"{set(colunas_requeridas) - set(df.columns)}"
            )
            return pd.DataFrame()
        return df
    except (FileNotFoundError, UnicodeDecodeError) as e:
        logger.error(f"Erro ao abrir arquivo: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar dados: {str(e)}")
        return pd.DataFrame()


def analisar_vendas(df_transacoes: pd.DataFrame) -> Dict[str, Any]:
    """Realiza a análise de vendas e retorna dados agregados"""
    if df_transacoes is None or df_transacoes.empty:
        return {"Performance por Mês/Ano": pd.Series(dtype=float)}

    try:
        df = df_transacoes.copy()
        df['data_hora'] = pd.to_datetime(
            df['data_hora'], format='%Y-%m-%d %H:%M:%S', errors='coerce'
        )
        df = df.dropna(subset=['data_hora'])
        if df.empty:
            return {"Performance por Mês/Ano": pd.Series(dtype=float)}

        df.loc[:, 'receita'] = pd.to_numeric(
            df.get('quantidade', 0), errors='coerce'
        ) * pd.to_numeric(df.get('valor_unitario', 0), errors='coerce')
        df = df.dropna(subset=['receita'])
        if df.empty:
            return {"Performance por Mês/Ano": pd.Series(dtype=float)}

        df.loc[:, 'mes_ano'] = df['data_hora'].dt.to_period('M').astype(str)
        vendas_por_mes = df.groupby('mes_ano')['receita'].sum().sort_index()

        return {"Performance por Mês/Ano": vendas_por_mes}
    except Exception as e:
        logger.error(f"Erro na análise de vendas: {e}")
        return {"Performance por Mês/Ano": pd.Series(dtype=float)}


def gerar_grafico_performance_mensal(
    vendas_mensais: pd.Series, pasta_saida: str, nome_arquivo: str
) -> None:
    """Gera gráfico de performance mensal"""
    try:
        if not isinstance(vendas_mensais, pd.Series) or vendas_mensais.empty:
            raise ValueError("vendas_mensais deve ser uma Series não vazia")

        os.makedirs(pasta_saida, exist_ok=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        vendas_mensais.plot(kind='bar', ax=ax)
        ax.set_title('Performance Mensal de Vendas')
        ax.set_ylabel('Receita')
        ax.set_xlabel('Mês/Ano')
        plt.tight_layout()

        caminho = os.path.join(pasta_saida, nome_arquivo)
        plt.savefig(caminho)
        plt.close(fig)
        logger.info(f"Gráfico salvo em: {caminho}")
    except Exception as e:
        logger.error(f"ERRO SÊNIOR: Falha ao salvar o gráfico. Detalhes: {e}")
        raise Exception(f"Erro ao gerar gráfico: {e}")


# --- Exemplo de Uso (Fluxo de Desenvolvimento) ---
if __name__ == "__main__":
    # Simulação de Carregamento
    df_vendas = _carregar_dados_com_seguranca(ARQUIVO_TRANSACOES)

    # Execução da Análise
    relatorio_vendas = analisar_vendas(df_vendas)
    vendas_mensais = relatorio_vendas.get("Performance por Mês/Ano")

    # Geração do Gráfico
    if isinstance(vendas_mensais, pd.Series) and not vendas_mensais.empty:
        gerar_grafico_performance_mensal(
            vendas_mensais, PASTA_IMAGEM, "vendas_mensais.png"
        )

    # Executar verificação de estoque e alertas (opcional)
    try:
        import alerts

        alert_emails = os.getenv("ALERT_EMAILS", "")
        destinatarios = [
            e.strip() for e in alert_emails.split(",") if e.strip()
        ]
        if destinatarios:
            resp_alertas = alerts.gerar_alertas_e_enviar(
                "estoque.csv", destinatarios
            )
            logger.info(f"Resultado dos alertas: {resp_alertas}")
        else:
            logger.info(
                "Nenhum destinatário de alerta configurado (ALERT_EMAILS)."
            )
    except Exception as e:
        logger.error(f"Falha ao executar módulo de alertas: {e}")
