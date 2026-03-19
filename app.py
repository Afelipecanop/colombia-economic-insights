"""
Colombia Economic Insights - Streamlit Dashboard
Interactive web application for exploring Colombian economic data
"""

import os
import glob
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Colombia Economic Insights",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_latest_csv_files():
    """Load the most recent CSV files from each category"""
    output_dir = Path("output")
    csv_files = {}

    # Define file patterns
    patterns = {
        'basic_stats': 'colombia_economic_basic_stats_*.csv',
        'yearly_stats': 'colombia_economic_yearly_stats_*.csv',
        'percentiles': 'colombia_economic_percentiles_*.csv',
        'summary': 'colombia_economic_summary_*.csv',
        'outliers': 'colombia_economic_outliers_*.csv'
    }

    for key, pattern in patterns.items():
        files = list(output_dir.glob(pattern))
        if files:
            # Get the most recent file
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            try:
                # Some CSV outputs use the first column as an index (e.g., basic stats)
                # When reading, we force the first column to be the index to preserve labels like 'count'.
                if key in ('basic_stats', 'percentiles', 'outliers'):
                    df = pd.read_csv(latest_file, index_col=0)
                else:
                    df = pd.read_csv(latest_file)

                csv_files[key] = df
                csv_files[f'{key}_path'] = str(latest_file)
            except Exception as e:
                st.error(f"Error loading {key}: {e}")

    return csv_files

def create_time_series_chart(yearly_data):
    """Create an interactive time series chart"""
    fig = px.line(
        yearly_data,
        x='year',
        y='mean',
        title='Inflación Anual Promedio - Colombia',
        labels={'year': 'Año', 'mean': 'Inflación (%)'},
        markers=True
    )

    # Add range slider
    fig.update_xaxes(rangeslider_visible=True)

    # Add trend line
    fig.add_trace(
        go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['mean'].rolling(window=5).mean(),
            mode='lines',
            name='Tendencia (5 años)',
            line=dict(color='red', dash='dash')
        )
    )

    return fig

def create_distribution_chart(yearly_data):
    """Create a distribution chart"""
    fig = px.histogram(
        yearly_data,
        x='mean',
        title='Distribución de la Inflación Anual',
        labels={'mean': 'Inflación (%)'},
        nbins=10
    )
    return fig

def create_year_over_year_chart(yearly_data):
    """Create year-over-year change chart"""
    # Filter out NaN values
    yoy_data = yearly_data.dropna(subset=['yoy_change'])

    fig = px.bar(
        yoy_data,
        x='year',
        y='yoy_change',
        title='Cambio Porcentual Anual (YoY)',
        labels={'year': 'Año', 'yoy_change': 'Cambio YoY (%)'},
        color='yoy_change',
        color_continuous_scale=['red', 'yellow', 'green']
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black")
    return fig

def create_moving_averages_charts(yearly_data):
    """Create moving averages charts for trend analysis"""
    ma_3 = yearly_data['mean'].rolling(window=3).mean()
    ma_5 = yearly_data['mean'].rolling(window=5).mean()

    fig_3 = px.line(
        yearly_data, 
        x='year', 
        y=ma_3,
        title='Media Móvil (3 años)',
        labels={'year': 'Año', 'y': 'Inflación (%)'}
    )

    fig_5 = px.line(
        yearly_data, 
        x='year', 
        y=ma_5,
        title='Media Móvil (5 años)',
        labels={'year': 'Año', 'y': 'Inflación (%)'}
    )

    return fig_3, fig_5

def display_metrics(basic_stats):
    """Display key metrics in cards"""

    def metric_value(label):
        try:
            return float(basic_stats.loc[label, 'Value'])
        except Exception:
            return None

    total = metric_value('count')
    avg = metric_value('mean')
    med = metric_value('median')
    std = metric_value('std')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Registros", f"{int(total):,}" if total is not None else "N/A")

    with col2:
        st.metric("Promedio", f"{avg:.2f}%" if avg is not None else "N/A")

    with col3:
        st.metric("Mediana", f"{med:.2f}%" if med is not None else "N/A")

    with col4:
        st.metric("Desviación Estándar", f"{std:.2f}%" if std is not None else "N/A")

def main():
    # Header
    st.markdown('<h1 class="main-header">🇨🇴 Colombia Economic Insights</h1>', unsafe_allow_html=True)
    st.markdown("### Dashboard Interactivo de Datos Económicos de Colombia")

    # Load data
    with st.spinner("Cargando datos más recientes..."):
        csv_files = load_latest_csv_files()

    if not csv_files:
        st.error("No se encontraron archivos CSV en el directorio output/. Por favor ejecute el análisis primero.")
        return

    # Sidebar
    st.sidebar.markdown('<h2 class="sidebar-header">📊 Navegación</h2>', unsafe_allow_html=True)

    # Data info
    st.sidebar.markdown("### 📁 Archivos Cargados")
    for key, path in [(k, v) for k, v in csv_files.items() if k.endswith('_path')]:
        category = key.replace('_path', '')
        st.sidebar.text(f"• {category}: {Path(path).name}")

    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Resumen", "📊 Estadísticas", "📉 Tendencias", "📋 Datos", "ℹ️ Información"])

    with tab1:
        st.markdown("## 📈 Resumen Ejecutivo")

        if 'basic_stats' in csv_files:
            display_metrics(csv_files['basic_stats'])

        col1, col2 = st.columns(2)

        with col1:
            if 'yearly_stats' in csv_files:
                st.markdown("### 📊 Serie Temporal")
                fig = create_time_series_chart(csv_files['yearly_stats'])
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'yearly_stats' in csv_files:
                st.markdown("### 📈 Distribución")
                fig = create_distribution_chart(csv_files['yearly_stats'])
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("## 📊 Estadísticas Detalladas")

        if 'basic_stats' in csv_files:
            st.markdown("### Estadísticas Básicas")
            st.dataframe(csv_files['basic_stats'], use_container_width=True)

        if 'percentiles' in csv_files:
            st.markdown("### Percentiles")
            st.dataframe(csv_files['percentiles'], use_container_width=True)

        if 'outliers' in csv_files:
            st.markdown("### Análisis de Valores Atípicos")
            st.dataframe(csv_files['outliers'], use_container_width=True)

    with tab3:
        st.markdown("## 📉 Análisis de Tendencias")

        if 'yearly_stats' in csv_files:
            st.markdown("### Cambio Porcentual Anual (YoY)")
            fig = create_year_over_year_chart(csv_files['yearly_stats'])
            st.plotly_chart(fig, use_container_width=True)

            # Additional trend analysis
            st.markdown("### Medias Móviles")
            col1, col2 = st.columns(2)

            fig_3, fig_5 = create_moving_averages_charts(csv_files['yearly_stats'])

            with col1:
                st.plotly_chart(fig_3, use_container_width=True)

            with col2:
                st.plotly_chart(fig_5, use_container_width=True)

    with tab4:
        st.markdown("## 📋 Datos Crudos")

        if 'yearly_stats' in csv_files:
            st.markdown("### Estadísticas por Año")
            st.dataframe(csv_files['yearly_stats'], use_container_width=True)

            # Download button
            csv_data = csv_files['yearly_stats'].to_csv(index=False)
            st.download_button(
                label="📥 Descargar Datos Anuales",
                data=csv_data,
                file_name="colombia_inflation_yearly.csv",
                mime="text/csv"
            )

        if 'summary' in csv_files:
            st.markdown("### Resumen General")
            st.dataframe(csv_files['summary'], use_container_width=True)

    with tab5:
        st.markdown("## ℹ️ Información del Proyecto")

        st.markdown("""
        ### 📋 Descripción
        Este dashboard presenta un análisis completo de los datos económicos de Colombia,
        específicamente la evolución de la inflación desde 1960 hasta 2020.

        ### 🔧 Tecnologías Utilizadas
        - **BigQuery**: Extracción de datos desde Google Cloud
        - **Python**: Procesamiento y análisis de datos
        - **Pandas**: Manipulación de datos
        - **Streamlit**: Interfaz web interactiva
        - **Plotly**: Visualizaciones interactivas

        ### 📊 Metodología
        1. **Extracción**: Datos obtenidos desde BigQuery
        2. **Análisis Estadístico**: Cálculo de métricas básicas, percentiles y outliers
        3. **Visualización**: Gráficos interactivos para explorar tendencias
        4. **Dashboard**: Interfaz web para acceso fácil a los insights

        ### 📈 Métricas Disponibles
        - Estadísticas básicas (media, mediana, desviación estándar)
        - Análisis por año con cambios porcentuales
        - Percentiles y distribución
        - Detección de valores atípicos
        - Tendencias a largo plazo
        """)

        # Historical Context
        st.markdown("### 📜 Contexto Histórico de la Inflación")
        st.markdown("""
        Basado en el análisis de datos, los dos años con la inflación más alta en Colombia (1960-2020) fueron 1977 (34.09%) y 1991 (30.35%).
        A continuación, se detalla el contexto social y político que explica estos picos inflacionarios.
        """)

        with st.expander("1977: Inflación del 34.09%"):
            st.markdown("""
            **Contexto político y social**:
            - **Crisis petrolera global (1973-1974)**: Factor principal. La crisis del petróleo cuadruplicó los precios internacionales. Colombia, importadora neta, sufrió impacto directo en costos de combustibles, transporte y productos derivados.
            - **Políticas económicas expansivas del gobierno de Alfonso López Michelsen (1974-1978)**: Medidas fiscales deficitarias para financiar infraestructura y subsidios sociales, inyectando liquidez pero presionando precios.
            - **Impacto social**: Aumentó desigualdad, afectando salarios y pobreza. Contribuyó a protestas y migración rural-urbana.
            """)

        with st.expander("1991: Inflación del 30.35%"):
            st.markdown("""
            **Contexto político y social**:
            - **Reforma constitucional y Asamblea Nacional Constituyente (1990-1991)**: Proceso que generó incertidumbre económica, aumento de gasto público y caída en confianza inversionista.
            - **Herencia de la crisis de los años 80**: Hiperinflación por narcotráfico, deuda externa y políticas de ajuste. Reformas estructurales incluyeron devaluaciones que encarecieron importaciones.
            - **Impacto social**: Golpeó clase media y baja, aumentando pobreza urbana. Protestas contra reformas en medio de violencia por narcotráfico.
            """)

        st.markdown("""
        Estos picos reflejan vulnerabilidades externas combinadas con decisiones políticas internas, siendo excepcionales en la serie histórica (media ~14%).
        """)

        # Project structure
        st.markdown("### 🏗️ Estructura del Proyecto")
        st.code("""
colombia-economic-insights/
├── src/
│   ├── bigquery_client.py      # Cliente BigQuery
│   ├── analysis.py             # Análisis estadístico
│   ├── main.py                 # Script principal
│   └── verify_config.py        # Verificación de configuración
├── output/                     # Archivos CSV generados
├── app.py                      # Dashboard Streamlit (este archivo)
├── requirements.txt            # Dependencias
└── README.md                   # Documentación
        """)

if __name__ == "__main__":
    main()