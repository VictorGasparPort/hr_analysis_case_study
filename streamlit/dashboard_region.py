# app_region_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

# ---------------------------
# 1. CONFIGURAÇÃO INICIAL DA PÁGINA
# ---------------------------
st.set_page_config(
    page_title="📊 Análise Regional - Funcionários",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado para aprimorar a estética (preto e branco, espaçamento adequado e fontes profissionais)
st.markdown("""
    <style>
        body {
            color: #000;
            background-color: #fff;
            font-family: 'Segoe UI', sans-serif;
        }
        .report-box {
            background-color: #f9f9f9; 
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #333;
            line-height: 1.6;
            font-size: 16px;
        }
        h1, h2, h3 {
            color: #000;
        }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------
# 2. FUNÇÃO DE CARREGAMENTO DOS DADOS COM CACHE
# ---------------------------
@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    """
    Carrega os dados do CSV com a tipagem otimizada e faz cache para performance.
    Parâmetros:
      path (str): Caminho do arquivo CSV.
    Retorna:
      DataFrame com os dados carregados.
    """
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# ---------------------------
# 3. FUNÇÃO DE ANÁLISE REGIONAL
# ---------------------------
def analisar_region(df: pd.DataFrame):
    """
    Realiza análise completa das regiões e suas relações com outras variáveis.
    Utiliza cálculos e agrupamentos para extrair métricas de interesse.
    Parâmetros:
      df (pandas.DataFrame): DataFrame com os dados.
    Retorna:
      dict com os resultados das análises.
    """

    try:
        # Cálculo das métricas agregadas por região
        region_counts = df['region'].value_counts()
        region_promotion = df.groupby('region')['is_promoted'].mean() * 100
        region_scores = df.groupby('region')['avg_training_score'].mean()
        region_kpis = df.groupby('region')['KPIs_met >80%'].mean() * 100

        resultados = {
            'contagem': region_counts.to_dict(),
            'promocao': region_promotion.to_dict(),
            'scores': region_scores.to_dict(),
            'kpis': region_kpis.to_dict()
        }
    except Exception as e:
        st.error(f"Erro durante os cálculos agregados: {e}")
        return {}

    # ---------------------------
    # Criação dos gráficos interativos com Plotly
    # ---------------------------

    # Widget: Slider para definir o número "Top N" de regiões a serem exibidas
    top_n = st.slider("Selecione o número de regiões a exibir (Top N):", min_value=3, max_value=20, value=10, step=1)

    # Gráfico 1: Top N Regiões por Número de Funcionários
    df_counts = region_counts.head(top_n).reset_index()
    df_counts.columns = ['region', 'count']
    fig_counts = px.bar(df_counts, x='region', y='count', 
                        title="Top Regiões por Número de Funcionários",
                        labels={'region': 'Região', 'count': 'Número de Funcionários'},
                        color_discrete_sequence=["black"])
    fig_counts.update_layout(template="simple_white")

    # Gráfico 2: Top N Regiões por Taxa de Promoção
    df_promo = region_promotion.sort_values(ascending=False).head(top_n).reset_index()
    df_promo.columns = ['region', 'promotion_rate']
    fig_promo = px.bar(df_promo, x='region', y='promotion_rate',
                       title="Top Regiões por Taxa de Promoção (%)",
                       labels={'region': 'Região', 'promotion_rate': 'Taxa de Promoção (%)'},
                       color_discrete_sequence=["black"])
    fig_promo.update_layout(template="simple_white")

    # Gráfico 3: Top N Regiões por Score Médio de Treinamento
    df_scores = region_scores.sort_values(ascending=False).head(top_n).reset_index()
    df_scores.columns = ['region', 'avg_training_score']
    fig_scores = px.bar(df_scores, x='region', y='avg_training_score',
                        title="Top Regiões por Score Médio de Treinamento",
                        labels={'region': 'Região', 'avg_training_score': 'Score Médio'},
                        color_discrete_sequence=["black"])
    fig_scores.update_layout(template="simple_white")

    # Gráfico 4: Top N Regiões por Taxa de KPIs Atingidos
    df_kpis = region_kpis.sort_values(ascending=False).head(top_n).reset_index()
    df_kpis.columns = ['region', 'kpi_rate']
    fig_kpis = px.bar(df_kpis, x='region', y='kpi_rate',
                      title="Top Regiões por Taxa de KPIs Atingidos (%)",
                      labels={'region': 'Região', 'kpi_rate': 'KPIs Atingidos (%)'},
                      color_discrete_sequence=["black"])
    fig_kpis.update_layout(template="simple_white")

    # Gráfico 5: Mapa de calor das correlações das métricas por região
    try:
        region_metrics = df.groupby('region').agg({
            'is_promoted': 'mean',
            'avg_training_score': 'mean',
            'KPIs_met >80%': 'mean',
            'age': 'mean',
            'length_of_service': 'mean',
            'awards_won?': 'mean'
        })
        corr_matrix = region_metrics.corr()
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdYlBu',
            zmid=0,
            text=corr_matrix.round(2).values.astype(str),
            hoverinfo="text"
        ))
        fig_heatmap.update_layout(title="Correlação entre Métricas por Região", template="simple_white", height=500)
    except Exception as e:
        st.error(f"Erro ao gerar o mapa de calor: {e}")
        fig_heatmap = go.Figure()

    # Gráfico 6: Distribuição de Departamentos por Região (Gráfico empilhado)
    try:
        dept_region = pd.crosstab(df['region'], df['department'], normalize='index') * 100
        dept_region = dept_region.reset_index().melt(id_vars='region', var_name='department', value_name='percentage')
        fig_dept = px.bar(dept_region, x='region', y='percentage', color='department',
                          title="Distribuição de Departamentos por Região",
                          labels={'percentage': 'Proporção (%)', 'region': 'Região'},
                          text_auto=".1f",
                          barmode='stack')
        fig_dept.update_layout(template="simple_white")
    except Exception as e:
        st.error(f"Erro ao gerar gráfico de departamentos: {e}")
        fig_dept = go.Figure()

    # ---------------------------
    # Exibição dos gráficos na página (layout em grid responsivo)
    # ---------------------------
    st.markdown("## 📈 Visualizações Interativas")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_counts, use_container_width=True)
        st.plotly_chart(fig_promo, use_container_width=True)
    with col2:
        st.plotly_chart(fig_scores, use_container_width=True)
        st.plotly_chart(fig_kpis, use_container_width=True)

    st.markdown("---")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown("---")
    st.plotly_chart(fig_dept, use_container_width=True)

    # ---------------------------
    # Relatório textual com insights (caixa estilizada)
    # ---------------------------
    st.markdown("## 📝 Relatório Executivo")
    total_regioes = len(region_counts)
    media_funcionarios = region_counts.mean()
    mediana_funcionarios = region_counts.median()
    top_region = region_counts.idxmax()
    top_region_percent = (region_counts[top_region] / df.shape[0] * 100)

    relatorio = f"""
    <div class='report-box'>
    <h3>Resumo da Análise Regional</h3>
    <b>Estatísticas Gerais:</b><br>
    - Total de regiões analisadas: <b>{total_regioes}</b><br>
    - Média de funcionários por região: <b>{media_funcionarios:.1f}</b><br>
    - Mediana de funcionários por região: <b>{mediana_funcionarios:.1f}</b><br><br>
    <b>Destaques:</b><br>
    - A região <b>{top_region}</b> concentra aproximadamente <b>{top_region_percent:.1f}%</b> do total de funcionários.<br>
    - As regiões com melhores taxas de promoção, scores e KPIs foram identificadas nos gráficos acima.<br><br>
    <b>Insights Adicionais:</b><br>
    - Recomenda-se aprofundar a análise segmentada por departamento e cargo para ações estratégicas.
    </div>
    """
    st.markdown(relatorio, unsafe_allow_html=True)

    return resultados

# ---------------------------
# 4. EXECUÇÃO DO DASHBOARD
# ---------------------------
def main():
    # Definir o caminho do CSV (certifique-se de que o arquivo está no local correto)
    data_path = '../data/processed/train_atualizado.csv'
    df = load_data(data_path)
    
    # Se o DataFrame estiver vazio, interromper a execução
    if df.empty:
        st.stop()
    
    # Cabeçalho principal
    st.markdown("<h1>📊 Dashboard de Análise de Funcionários - Análise Regional</h1>", unsafe_allow_html=True)
    st.markdown("Explore a distribuição e desempenho regional dos funcionários com visualizações interativas e insights detalhados.")
    st.markdown("---")
    
    # Executar a análise regional e exibir os gráficos e relatório
    resultados_region = analisar_region(df)
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
