import streamlit as st
import pandas as pd
import plotly.express as px
# Configuración de la Página de Streamlit
st.set_page_config(
    page_title="World Alcohol Consumption Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de las Paletas de Colores
PALETTE_WORLD = ["#1a6b3c", "#2d9e6b", "#4cc38a", "#90dbb5", "#d4f0e3", "#000000"]
PALETTE_COLOURS = ["#1a6b3c", "#e07b39", "#3a7ebf", "#c94040", "#8e44ad"]
PRIMARY_COLOR = PALETTE_COLOURS[0]

DATA_URL = (
    "https://raw.githubusercontent.com/figueraandrea25-hub/alcohol-consumption-analysis/refs/heads/main/alcohol_data.csv"
)


# Carga y limpieza de los datos
@st.cache_data
def load_and_clean_data(url):
    """Carga y limpia los datos de consumo de alcohol mundial."""
    data = pd.read_csv(url)

    # Normalizar nombres de columnas: mayúsculas y sin espacios extra
    data.columns = data.columns.str.strip().str.upper().str.replace(' ', '_')

    # Normalizar columna SEX a mayúsculas
    if 'SEX' in data.columns:
        data['SEX'] = data['SEX'].str.strip().str.title()

    # Normalizar columna COUNTRY
    if 'COUNTRY' in data.columns:
        data['COUNTRY'] = data['COUNTRY'].str.strip()

    # Convertir columnas numéricas
    numeric_cols = ['ALCOHOL_LITERS_PER_CAPITA', 'LOWER_CI', 'UPPER_CI', 'CI_WIDTH', 'YEAR']
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')

    # Rellenar valores nulos en CI con la mediana
    for col in ['LOWER_CI', 'UPPER_CI', 'CI_WIDTH']:
        if col in data.columns:
            data[col] = data[col].fillna(data[col].median())

    return data


# Función Principal de la Aplicación
def main():
    # Cargar los datos
    try:
        data = load_and_clean_data(DATA_URL)
    except Exception as e:
        st.error(f"🔴 Error loading data: {e}")
        return

    # --- 1. Sidebar con Filtros Globales ---
    st.sidebar.header("Global Filters")

    # Filtro por Sexo
    sex_options = sorted(data['SEX'].dropna().unique().tolist())
    default_sex = [s for s in ["Both Sexes"] if s in sex_options] or sex_options[:1]
    selected_sex = st.sidebar.multiselect(
        "Select Sex Category",
        options=sex_options,
        default=default_sex
    )

    # Filtro por Año
    year_min = int(data['YEAR'].min())
    year_max = int(data['YEAR'].max())
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max)
    )

    # Filtro por Región (Top N países)
    top_n = st.sidebar.selectbox(
        "Show Top N Countries in rankings",
        options=[5, 10, 15, 20],
        index=1
    )

    # Aplicar filtros
    df_filtered = data.copy()
    if selected_sex:
        df_filtered = df_filtered[df_filtered['SEX'].isin(selected_sex)]
    df_filtered = df_filtered[
        (df_filtered['YEAR'] >= selected_years[0]) &
        (df_filtered['YEAR'] <= selected_years[1])
    ]

    # --- 2. Título Principal ---
    st.title("🌍 World Alcohol Consumption Analysis")
    st.markdown("*Liters of pure alcohol consumed per capita across countries and years.*")
    st.markdown("---")

    if df_filtered.empty:
        st.warning("No data available for the selected filters. Please adjust your selections.")
        return

    # --- 3. KPI Cards ---
    st.header("📊 General Overview")
    col1, col2, col3, col4 = st.columns(4)

    avg_consumption = df_filtered['ALCOHOL_LITERS_PER_CAPITA'].mean()
    max_consumption = df_filtered['ALCOHOL_LITERS_PER_CAPITA'].max()
    num_countries = df_filtered['COUNTRY'].nunique()
    num_years = df_filtered['YEAR'].nunique()

    with col1:
        st.metric("🌐 Countries Analyzed", f"{num_countries:,}")
    with col2:
        st.metric("📅 Years Covered", f"{num_years}")
    with col3:
        st.metric("🍺 Avg. Consumption (L/capita)", f"{avg_consumption:.2f}")
    with col4:
        st.metric("📈 Max. Consumption (L/capita)", f"{max_consumption:.2f}")

    st.markdown("---")

    # --- 4. Análisis General ---
    st.header("General Consumption Analysis")

    # 4.1 Distribución por sexo
    st.subheader("Consumption Distribution by Sex Category")

    sex_summary = (
        df_filtered.groupby('SEX')['ALCOHOL_LITERS_PER_CAPITA']
        .mean()
        .reset_index()
        .rename(columns={'ALCOHOL_LITERS_PER_CAPITA': 'Avg Liters per Capita'})
        .sort_values('Avg Liters per Capita', ascending=False)
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Table 1: Average Consumption by Sex")
        st.dataframe(
            sex_summary.style.format({'Avg Liters per Capita': '{:.2f}'}),
            use_container_width=True
        )

    with col2:
        fig_sex = px.bar(
            sex_summary,
            x='SEX',
            y='Avg Liters per Capita',
            color='SEX',
            title="Average Alcohol Consumption by Sex",
            color_discrete_sequence=PALETTE_COLOURS,
            text_auto='.2f'
        )
        fig_sex.update_layout(showlegend=False)
        st.plotly_chart(fig_sex, use_container_width=True)

    st.markdown("""
    **Analysis:** This chart shows the average alcohol consumption split by sex category.
    Male consumption is typically higher than female in most countries, while 'Both Sexes' reflects the overall population average.
    """)

    st.markdown("---")

    # 4.2 Top N Países por consumo medio
    st.subheader(f"Top {top_n} and Bottom {top_n} Countries by Average Consumption")

    country_avg = (
        df_filtered.groupby('COUNTRY')['ALCOHOL_LITERS_PER_CAPITA']
        .mean()
        .reset_index()
        .rename(columns={'ALCOHOL_LITERS_PER_CAPITA': 'Avg Liters per Capita'})
        .sort_values('Avg Liters per Capita', ascending=False)
    )

    top_countries = country_avg.head(top_n)
    bottom_countries = country_avg.tail(top_n).sort_values('Avg Liters per Capita')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### Table 2a: Top {top_n} Highest Consuming Countries")
        st.dataframe(
            top_countries.reset_index(drop=True).style.format({'Avg Liters per Capita': '{:.2f}'}),
            use_container_width=True
        )

    with col2:
        st.markdown(f"### Table 2b: Top {top_n} Lowest Consuming Countries")
        st.dataframe(
            bottom_countries.reset_index(drop=True).style.format({'Avg Liters per Capita': '{:.2f}'}),
            use_container_width=True
        )

    top_countries['Category'] = 'Highest'
    bottom_countries['Category'] = 'Lowest'
    combined = pd.concat([top_countries, bottom_countries])

    fig_top = px.bar(
        combined.sort_values('Avg Liters per Capita', ascending=True),
        x='Avg Liters per Capita',
        y='COUNTRY',
        color='Category',
        orientation='h',
        title=f"Top & Bottom {top_n} Countries by Avg. Alcohol Consumption",
        labels={'COUNTRY': 'Country', 'Avg Liters per Capita': 'Liters per Capita'},
        color_discrete_map={'Highest': PALETTE_COLOURS[0], 'Lowest': PALETTE_COLOURS[2]}
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("""
    **Analysis:** The horizontal bar chart clearly contrasts the highest and lowest consuming nations.
    European countries tend to dominate the top, while many low-income nations show minimal per-capita alcohol intake.
    """)

    st.markdown("---")

    # --- 5. Análisis Temporal ---
    st.header("📅 Trends Over Time")

    st.subheader("Global Average Consumption per Year")

    yearly_avg = (
        df_filtered.groupby('YEAR')['ALCOHOL_LITERS_PER_CAPITA']
        .mean()
        .reset_index()
        .rename(columns={'ALCOHOL_LITERS_PER_CAPITA': 'Avg Liters per Capita'})
    )

    fig_trend = px.line(
        yearly_avg,
        x='YEAR',
        y='Avg Liters per Capita',
        markers=True,
        title="Global Average Alcohol Consumption Over Time",
        labels={'YEAR': 'Year', 'Avg Liters per Capita': 'Avg Liters per Capita'},
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig_trend.update_traces(line=dict(width=3))
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("""
    **Analysis:** This trend line reveals whether global alcohol consumption is rising, falling, or remaining stable.
    Peaks may coincide with economic growth periods while drops can reflect health campaigns or global crises.
    """)

    st.subheader(f"Consumption Trend for Top {min(5, top_n)} Countries Over Time")

    top5_names = top_countries.head(5)['COUNTRY'].tolist()
    df_top5_trend = df_filtered[df_filtered['COUNTRY'].isin(top5_names)]

    yearly_country = (
        df_top5_trend.groupby(['YEAR', 'COUNTRY'])['ALCOHOL_LITERS_PER_CAPITA']
        .mean()
        .reset_index()
    )

    fig_country_trend = px.line(
        yearly_country,
        x='YEAR',
        y='ALCOHOL_LITERS_PER_CAPITA',
        color='COUNTRY',
        markers=True,
        title=f"Year-over-Year Consumption: Top {min(5, top_n)} Countries",
        labels={'YEAR': 'Year', 'ALCOHOL_LITERS_PER_CAPITA': 'Liters per Capita', 'COUNTRY': 'Country'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_country_trend, use_container_width=True)

    st.markdown("""
    **Analysis:** Tracking individual countries over time exposes unique trajectories.
    Some nations show consistent high consumption while others have declining trends, possibly due to policy interventions.
    """)

    st.markdown("---")

    # --- 6. Mapa Mundial ---
    st.header("🗺️ Geographic Distribution")
    st.subheader("World Map of Average Alcohol Consumption")

    map_data = (
        df_filtered.groupby(['COUNTRY', 'ISO3'])['ALCOHOL_LITERS_PER_CAPITA']
        .mean()
        .reset_index()
        .rename(columns={'ALCOHOL_LITERS_PER_CAPITA': 'Avg Liters per Capita'})
    )

    fig_map = px.choropleth(
        map_data,
        locations='ISO3',
        color='Avg Liters per Capita',
        hover_name='COUNTRY',
        color_continuous_scale='YlOrRd',
        title="Average Alcohol Consumption per Capita by Country",
        labels={'Avg Liters per Capita': 'Liters per Capita'}
    )
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("""
    **Analysis:** The choropleth map provides an immediate global perspective.
    Darker regions indicate heavier per-capita consumption. Clear geographic clusters emerge — notably in Eastern Europe and parts of the Pacific.
    """)

    st.markdown("---")

    # --- 7. Intervalos de Confianza ---
    st.header("📐 Confidence Interval Analysis")
    st.subheader(f"Uncertainty Range for Top {top_n} Countries")

    ci_data = (
        df_filtered[df_filtered['COUNTRY'].isin(top_countries['COUNTRY'])]
        .groupby('COUNTRY')[['ALCOHOL_LITERS_PER_CAPITA', 'LOWER_CI', 'UPPER_CI']]
        .mean()
        .reset_index()
        .sort_values('ALCOHOL_LITERS_PER_CAPITA', ascending=False)
    )

    fig_ci = px.scatter(
        ci_data,
        x='ALCOHOL_LITERS_PER_CAPITA',
        y='COUNTRY',
        error_x_minus=ci_data['ALCOHOL_LITERS_PER_CAPITA'] - ci_data['LOWER_CI'],
        error_x=ci_data['UPPER_CI'] - ci_data['ALCOHOL_LITERS_PER_CAPITA'],
        title=f"Consumption Estimate with 95% Confidence Intervals — Top {top_n} Countries",
        labels={'ALCOHOL_LITERS_PER_CAPITA': 'Liters per Capita', 'COUNTRY': 'Country'},
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig_ci.update_traces(marker=dict(size=10))
    st.plotly_chart(fig_ci, use_container_width=True)

    st.markdown("""
    **Analysis:** Confidence intervals reveal the reliability of the estimates.
    Countries with wide intervals have greater uncertainty in their reported data.
    """)

    st.markdown("---")

    # --- 8. Tabla Completa ---
    st.header("📋 Full Dataset Explorer")
    st.subheader("Filtered Data Table")

    display_cols = [c for c in ['COUNTRY', 'ISO3', 'YEAR', 'SEX', 'ALCOHOL_LITERS_PER_CAPITA', 'LOWER_CI', 'UPPER_CI', 'CI_WIDTH'] if c in df_filtered.columns]
    st.dataframe(
        df_filtered[display_cols]
        .sort_values(['COUNTRY', 'YEAR'])
        .reset_index(drop=True)
        .style.format({
            'ALCOHOL_LITERS_PER_CAPITA': '{:.3f}',
            'LOWER_CI': '{:.3f}',
            'UPPER_CI': '{:.3f}',
            'CI_WIDTH': '{:.3f}'
        }),
        use_container_width=True,
        height=400
    )

    st.caption(f"Showing {len(df_filtered):,} records | Source: WHO Global Alcohol Consumption Dataset")


if __name__ == "__main__":
    main()
