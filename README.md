# 📈 Análise de Performance de Varejo Sênior (Python & Pandas)

## 🇧🇷 Visão Geral do Projeto

Este projeto demonstra uma solução de **Análise de Dados de Varejo** com foco na performance de vendas e gestão de inventário. [cite_start]O objetivo principal é extrair insights acionáveis (dias/meses de maior venda, produtos destaque e alertas de estoque crítico) utilizando práticas sêniores de programação[cite: 1].

A arquitetura do código prioriza:
* [cite_start]**Eficiência Algorítmica (Big-O):** Uso extensivo da biblioteca Pandas para garantir que as agregações de grandes volumes de dados ocorram em complexidade $O(n)$, evitando iterações lentas e ineficientes[cite: 7].
* [cite_start]**Modularidade e Clean Code:** Funções claras e com responsabilidade única (ex: `_carregar_dados_com_seguranca`, `analisar_vendas`, `gerar_grafico_performance_mensal`)[cite: 6].
* [cite_start]**Tratamento Robusto de Erros:** Implementação de `try...except` para I/O, `pd.to_datetime(errors='coerce')` e `os.makedirs(exist_ok=True)` para garantir tolerância a falhas e estabilidade do fluxo[cite: 3].

---

## 🇺🇸 Project Overview

This project demonstrates a **Retail Data Analysis** solution focusing on sales performance and inventory management. [cite_start]The main goal is to extract actionable insights (peak sales days/months, top products, and critical stock alerts) using senior programming practices[cite: 1].

The code architecture prioritizes:
* [cite_start]**Algorithmic Efficiency (Big-O):** Extensive use of the Pandas library ensures that large data aggregations operate with $O(n)$ complexity, avoiding slow and inefficient iterations[cite: 7].
* [cite_start]**Modularity and Clean Code:** Clear functions with single responsibility (e.g., `_carregar_dados_com_seguranca`, `analisar_vendas`, `gerar_grafico_performance_mensal`)[cite: 6].
* [cite_start]**Robust Error Handling:** Implementation of `try...except` for I/O, `pd.to_datetime(errors='coerce')`, and `os.makedirs(exist_ok=True)` to ensure fault tolerance and stable flow[cite: 3].

---

## 💻 Requisitos Técnicos / Technical Requirements

* [cite_start]**Python:** $\geq 3.11$ [cite: 2]
* **Bibliotecas:** `pandas`, `matplotlib` (instalação via `pip install pandas matplotlib`)

---

## 🚀 Fluxo de Análise / Analysis Flow

O processo é projetado em etapas modulares:

| Etapa | Função Principal | Descrição |
| :--- | :--- | :--- |
| **1. Carregamento Seguro** | `_carregar_dados_com_seguranca()` | Carrega `transacoes.csv` e `estoque.csv`. **Trata** `FileNotFoundError` e `Exception`s genéricas, retornando um DataFrame vazio em caso de falha. |
| **2. Análise de Vendas** | `analisar_vendas()` | Calcula `receita` (`quantidade` * `valor_unitario`). [cite_start]Agrega dados por Mês/Ano e Dia, aproveitando as operações vetorizadas do Pandas para **eficiência $O(n)$**[cite: 7]. |
| **3. Análise de Inventário** | `analisar_inventario()` | Identifica produtos **próximos do vencimento** (alerta configurável) e **parados** (sem giro) utilizando `datetime` do Pandas para manipulação eficiente de datas. |
| **4. Geração de Gráfico** | `gerar_grafico_performance_mensal()` | Utiliza Matplotlib para plotar a série temporal de vendas. [cite_start]Garante que a pasta de destino (`imagens`) exista usando `os.makedirs(exist_ok=True)` para evitar erros de I/O[cite: 3]. |

---

## 📁 Estrutura de Arquivos / File Structure

├── analise_varejo.py # Script principal de análise (Clean Code) 
├── transacoes.csv # Dados de Vendas (entrada) 
├── estoque.csv # Dados de Inventário (entrada) 
├── imagens/ # Diretório de saída (criado dinamicamente) 
│ └── vendas_por_mes.png # Gráfico gerado (Saída Testada) 
└── README.md

## 💡 Como Executar / How to Run

1.  **Instalação:**
    ```bash
    pip install pandas matplotlib
    ```
2.  **Criação dos Dados:** 

Certifique-se de que os arquivos `transacoes.csv` e `estoque.csv` 
estão na raiz do projeto.

3.  **Execução:**
    ```bash
    python analise_varejo.py
    ```

Ao finalizar, o console exibirá os relatórios de texto, e o gráfico de 
performance mensal será salvo em `imagens/vendas_por_mes.png`[cite: 12].

Autor [DevGege](https://github.com/GeovaneParedes)
