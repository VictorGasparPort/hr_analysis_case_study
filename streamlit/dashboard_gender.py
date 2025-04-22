import streamlit as st
import pandas as pd
# Removed unused numpy import
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

# Configuração inicial da página
st.set_page_config(
    page_title="Análise de Gênero Corporativa",
    page_icon="👥",
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
    
    Parâmetros:
        file_path (str): Caminho do arquivo CSV
        
    Retorna:
        pd.DataFrame: DataFrame otimizado
    """
    try:
        df = pd.read_csv(
            file_path,
            usecols=['gender', 'is_promoted', 'department', 'age', 'avg_training_score', 'KPIs_met >80%'],
            dtype={
                'gender': 'category',
                'department': 'category',
                'is_promoted': 'int8',
                'age': 'int8',
                'avg_training_score': 'int16',
                'KPIs_met >80%': 'int8'
            }
        )
        return df.dropna(subset=['gender'])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def create_gender_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de pizza interativo da distribuição de gênero"""
    gender_dist = df['gender'].value_counts().reset_index()
    fig = px.pie(
        gender_dist,
        names='gender',
        values='count',
        title='Distribuição de Gênero',
        color_discrete_sequence=px.colors.sequential.Greys_r
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_promotion_analysis_plot(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras interativo da taxa de promoção"""
    promotion = df.groupby('gender')['is_promoted'].mean() * 100
    fig = px.bar(
        promotion,
        x=promotion.index,
        y=promotion.values,
        title='Taxa de Promoção por Gênero',
        labels={'y': 'Taxa (%)', 'x': 'Gênero'},
        color_discrete_sequence=['#333333']
    )
    fig.update_layout(yaxis_range=[0, 100])
    return fig

def create_department_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras horizontais da distribuição por departamento"""
    dept_gender = pd.crosstab(df['department'], df['gender'], normalize='columns') * 100
    fig = px.bar(
        dept_gender.reset_index(),
        x='department',
        y=dept_gender.columns.tolist(),
        title='Distribuição por Departamento',
        labels={'value': 'Percentual (%)', 'variable': 'Gênero'},
        barmode='group',
        color_discrete_map={'f': '#000000', 'm': '#7F7F7F'},  # Define a cor de 'f' como preto
        orientation='h'
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Percentual (%)")
    return fig

def create_age_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """Cria boxplot interativo da distribuição de idade"""
    fig = px.box(
        df,
        x='gender',
        y='age',
        title='Distribuição de Idade por Gênero',
        color='gender',
        color_discrete_sequence=['#000000']
    )
    fig.update_layout(showlegend=False)
    return fig

def display_key_metrics(resultados: Dict[str, Any]) -> None:
    """Exibe métricas principais em layout grid"""
    cols = st.columns(4)
    metrics = [
        ('📊 Média Idade', 'media_idade'),
        ('🏆 Média KPIs', 'media_kpi'),
        ('🎯 Média Score', 'media_score'),
        ('🚀 Taxa Promoção', 'taxa_promocao')
    ]
    
    for col, (title, key) in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='metric-card'><h3>{title}</h3>", unsafe_allow_html=True)
            for gender, value in resultados[key].items():
                if key == 'taxa_promocao':
                    st.metric(gender, f"{value:.1f}%")
                elif key == 'media_kpi':
                    st.metric(gender, f"{value*100:.1f}%")
                else:
                    st.metric(gender, f"{value:.1f}")
            st.markdown("</div>", unsafe_allow_html=True)

def generate_gender_report(resultados: Dict[str, Any]) -> str:
    """Gera relatório textual formatado"""
    report = f"""
    📌 Principais Insights

    **Distribuição de Gênero:**
    {''.join([f'\n- {k}: {v} funcionários ({(v/resultados["total"]*100):.1f}%)' for k, v in resultados['distribuicao_genero'].items()])}

    **Performance por Gênero:**
    - 🏆 KPIs Atingidos: {max(resultados['media_kpi'], key=resultados['media_kpi'].get).title()} lidera com {max(resultados['media_kpi'].values())*100:.1f}%
    - 🎯 Score de Treinamento: {max(resultados['media_score'], key=resultados['media_score'].get).title()} com média de {max(resultados['media_score'].values()):.1f} pontos

    **Recomendações Estratégicas:**
    - Implementar programas de mentoria cruzada
    - Revisar processos de promoção
    - Desenvolver treinamentos específicos por gênero
    """
    return report

def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="header-text">👥 Análise de Diversidade de Gênero</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    df = load_data('../data/processed/train_atualizado.csv')
    
    if not df.empty:
        # Filtros interativos
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                departments = ['Todos'] + df['department'].unique().tolist()
                selected_dept = st.selectbox("🏢 Departamento", options=departments)
            with col2:
                age_range = st.slider(
                    "📅 Faixa Etária",
                    min_value=int(df['age'].min()),
                    max_value=int(df['age'].max()),
                    value=(25, 55)
                )

        # Aplicar filtros
        filtered_df = df[df['age'].between(*age_range)]
        if selected_dept != 'Todos':
            filtered_df = filtered_df[filtered_df['department'] == selected_dept]

        # Calcular métricas
        resultados = {
            'distribuicao_genero': filtered_df['gender'].value_counts().to_dict(),
            'taxa_promocao': filtered_df.groupby('gender')['is_promoted'].mean().mul(100).round(1).to_dict(),
            'media_idade': filtered_df.groupby('gender')['age'].mean().round(1).to_dict(),
            'media_score': filtered_df.groupby('gender')['avg_training_score'].mean().round(1).to_dict(),
            'media_kpi': filtered_df.groupby('gender')['KPIs_met >80%'].mean().round(3).to_dict(),
            'total': len(filtered_df)
        }

        # Seção de métricas
        display_key_metrics(resultados)

        # Layout dos gráficos
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_gender_distribution_plot(filtered_df), use_container_width=True)
            st.plotly_chart(create_department_distribution_plot(filtered_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_promotion_analysis_plot(filtered_df), use_container_width=True)
            st.plotly_chart(create_age_distribution_plot(filtered_df), use_container_width=True)

        # Relatório textual
        with st.expander("📄 Ver Relatório Completo", expanded=True):
            st.markdown(f'<div class="report-box">{generate_gender_report(resultados)}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()