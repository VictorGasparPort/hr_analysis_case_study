import streamlit as st
import pandas as pd
# Removed unused import
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

# Configuração inicial da página
st.set_page_config(
    page_title="Análise Departamental",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .header-text { 
        color: #000000;
        font-family: 'Arial';
        border-bottom: 2px solid #000000;
        padding-bottom: 10px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .report-box {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 25px;
        margin: 15px 0;
        background-color: #FFFFFF;
    }
    .plot-container {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Carregando dados...")
def load_data(file_path: str) -> pd.DataFrame:
    """
    Carrega e otimiza os dados do arquivo CSV
    """
    try:
        df = pd.read_csv(
            file_path,
            usecols=['department', 'is_promoted', 'avg_training_score', 
                    'KPIs_met >80%', 'length_of_service', 'education'],
            dtype={
                'department': 'category',
                'education': 'category',
                'is_promoted': 'int8',
                'avg_training_score': 'int16',
                'KPIs_met >80%': 'int8',
                'length_of_service': 'int8'
            }
        )
        return df.dropna(subset=['department'])
    except Exception:
        st.error("Erro ao carregar dados.")
        return pd.DataFrame()

def create_department_bar_plot(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Cria gráfico de barras interativo para métricas departamentais"""
    metric_data = df.groupby('department')[column].mean()
    if column == 'is_promoted':
        metric_data *= 100
        
    fig = px.bar(
        metric_data.reset_index(),
        x='department',
        y=column,
        title=title,
        labels={'department': 'Departamento', column: 'Valor'},
        color_discrete_sequence=['#333333']
    )
    
    if column == 'is_promoted':
        fig.update_layout(yaxis_title="Taxa de Promoção (%)")
    elif column == 'KPIs_met >80%':
        fig.update_layout(yaxis_title="KPIs Atingidos (%)")
        fig.update_traces(marker_color='#666666')
    
    return fig

def create_education_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras empilhadas da distribuição educacional"""
    educ_dept = pd.crosstab(df['department'], df['education'], normalize='index') * 100
    
    fig = px.bar(
        educ_dept.reset_index(),
        x='department',
        y=educ_dept.columns.tolist(),
        title='Distribuição de Nível Educacional por Departamento',
        labels={'value': 'Proporção (%)', 'variable': 'Nível Educacional'},
        color_discrete_sequence=px.colors.sequential.Greys,
        barmode='stack'
    )
    
    fig.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Proporção (%)",
        legend_title="Educação"
    )
    return fig

def display_key_metrics(resultados: Dict[str, Any]) -> None:
    """Exibe métricas principais em cards estilizados"""
    cols = st.columns(4)
    metrics = [
        ('🏢 Total Departamentos', len(resultados['contagem'])),
        ('📈 Maior Promoção', f"{max(resultados['promocao'].values()):.1f}%"),
        ('🎯 Melhor Score', f"{max(resultados['scores'].values()):.1f}"),
        ('🕒 Maior Tempo Serviço', f"{max(resultados['tempo_servico'].values()):.1f} anos")
    ]
    
    for col, (title, value) in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='metric-card'><h3>{title}</h3><h2>{value}</h2></div>", 
                       unsafe_allow_html=True)

def generate_department_report(resultados: Dict[str, Any]) -> str:
    """Gera relatório textual formatado com insights"""
    top_dept = max(resultados['contagem'], key=resultados['contagem'].get)
    top_promo = max(resultados['promocao'], key=resultados['promocao'].get)
    top_score = max(resultados['scores'], key=resultados['scores'].get)
    
    report = f"""
    📌 **Principais Insights**

    **Distribuição Departamental:**
    - Departamento mais numeroso: {top_dept} ({resultados['contagem'][top_dept]} funcionários)
    - Representa {(resultados['contagem'][top_dept]/resultados['total']*100):.1f}% do total

    **Performance:**
    - 🚀 Melhor taxa de promoção: {top_promo} ({resultados['promocao'][top_promo]:.1f}%)
    - 🎯 Melhor score de treinamento: {top_score} ({resultados['scores'][top_score]:.1f} pontos)

    **Recomendações:**
    - Desenvolver programa de desenvolvimento gerencial para {top_dept}
    - Implementar plano de capacitação técnica para departamentos com baixos scores
    - Criar programa de retenção para departamentos com maior tempo de serviço
    """
    
    return report.strip()
def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="header-text">🏢 Análise de Desempenho Departamental</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    df = load_data('../data/processed/train_atualizado.csv')
    
    if not df.empty:
        # Processar dados
        resultados = {
            'contagem': df['department'].value_counts().to_dict(),
            'promocao': df.groupby('department')['is_promoted'].mean().mul(100).round(1).to_dict(),
            'scores': df.groupby('department')['avg_training_score'].mean().round(1).to_dict(),
            'kpis': df.groupby('department')['KPIs_met >80%'].mean().mul(100).round(1).to_dict(),
            'tempo_servico': df.groupby('department')['length_of_service'].mean().round(1).to_dict(),
            'total': len(df)
        }
        
        # Seção de métricas
        display_key_metrics(resultados)
        
        # Layout principal
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Gráficos principais
            st.plotly_chart(
                create_department_bar_plot(df, 'is_promoted', 'Taxa de Promoção por Departamento'),
                use_container_width=True
            )
            
            st.plotly_chart(
                create_department_bar_plot(df, 'avg_training_score', 'Score Médio de Treinamento por Departamento'),
                use_container_width=True
            )
            
            st.plotly_chart(
                create_education_distribution_plot(df),
                use_container_width=True
            )
        
        with col2:
            # Gráficos secundários
            st.plotly_chart(
                create_department_bar_plot(df, 'KPIs_met >80%', 'KPIs Atingidos por Departamento'),
                use_container_width=True
            )
            
            st.plotly_chart(
                create_department_bar_plot(df, 'length_of_service', 'Tempo Médio de Serviço por Departamento'),
                use_container_width=True
            )
        
        # Seção de relatório
        with st.container():
            with st.expander("📄 Relatório Analítico Detalhado", expanded=True):
                st.markdown(
                    f'<div class="report-box">{generate_department_report(resultados)}</div>',
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()