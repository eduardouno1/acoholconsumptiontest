import base64
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# Configuración general de la app
# ==========================================================
st.set_page_config(
    page_title="Dashboard de Consumo de Alcohol por Regiones",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_URL = "https://raw.githubusercontent.com/figueraandrea25-hub/alcohol-consumption-analysis/refs/heads/main/alcohol_data.csv"
ANIOS_ANALISIS = (2015, 2019)

PALETA_PRINCIPAL = ["#1a6b3c", "#2d9e6b", "#4cc38a", "#90dbb5", "#d4f0e3"]
COLOR_BASE = PALETA_PRINCIPAL[0]


# ==========================================================
# Catálogo de regiones solicitado por el usuario
# ==========================================================
REGION_MAP = {
    "América Latina y el Caribe": [
        "ATG", "ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DMA",
        "DOM", "ECU", "SLV", "GRD", "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN",
        "PRY", "PER", "KNA", "LCA", "VCT", "SUR", "TTO", "URY", "VEN"
    ],
    "América del Norte": ["CAN", "USA"],
    "Asia": [
        "AFG", "BHR", "BGD", "BTN", "BRN", "KHM", "CHN", "COK", "CYP", "PRK", "EGY", "FJI",
        "IND", "IDN", "IRN", "IRQ", "ISR", "JPN", "JOR", "KAZ", "KGZ", "KIR", "KWT", "LAO",
        "LBN", "MYS", "MDV", "MHL", "FSM", "MNG", "MMR", "NRU", "NPL", "NZL", "NIU", "OMN",
        "PAK", "PLW", "PNG", "PHL", "QAT", "KOR", "WSM", "SAU", "SGP", "SLB", "LKA", "SYR",
        "TJK", "THA", "TLS", "TON", "TUR", "TKM", "TUV", "ARE", "UZB", "VUT", "VNM", "YEM"
    ],
    "Europa": [
        "ALB", "AND", "ARM", "AUT", "AZE", "BLR", "BEL", "BIH", "BGR", "HRV", "CZE", "DNK",
        "EST", "FIN", "FRA", "GEO", "DEU", "GRC", "HUN", "ISL", "IRL", "ISR", "ITA", "KAZ",
        "KGZ", "LVA", "LTU", "LUX", "MLT", "MCO", "MNE", "NLD", "MKD", "NOR", "POL", "PRT",
        "MDA", "ROU", "RUS", "SMR", "SRB", "SVK", "SVN", "ESP", "SWE", "CHE", "TJK", "TUR",
        "TKM", "UKR", "GBR", "UZB"
    ],
    "África": [
        "DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CMR", "CPV", "CAF", "TCD", "COM", "COG",
        "CIV", "COD", "DJI", "EGY", "GNQ", "ERI", "ETH", "GAB", "GMB", "GHA", "GIN", "GNB",
        "KEN", "LSO", "LBR", "LBY", "MDG", "MWI", "MLI", "MRT", "MUS", "MAR", "MOZ", "NAM",
        "NER", "NGA", "RWA", "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "SYR",
        "TGO", "TUN", "UGA", "TZA", "ZMB", "ZWE"
    ]
}

REGION_ORDER = [
    "América Latina y el Caribe",
    "América del Norte",
    "Asia",
    "Europa",
    "África"
]

SECCIONES = [
    "Resumen general",
    "Países por región",
    "Comparación entre regiones",
    "Comparación dentro de una región",
    "Ranking de países",
    "Mapa mundial",
    "Explorador de datos"
]


# ==========================================================
# Estilos visuales
# ==========================================================
def aplicar_estilos():
    """Aplica un fondo temático suave y mejora el aspecto visual general."""
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='900' height='700' viewBox='0 0 900 700'>
      <rect width='100%' height='100%' fill='#f8fbf9'/>
      <g opacity='0.08' fill='#7a1730'>
        <path d='M115 90 C85 90 75 135 98 162 C118 186 130 212 130 245 L100 245 L100 260 L180 260 L180 245 L150 245 C150 212 162 186 182 162 C205 135 195 90 165 90 Z'/>
        <path d='M345 140 C315 140 305 185 328 212 C348 236 360 262 360 295 L330 295 L330 310 L410 310 L410 295 L380 295 C380 262 392 236 412 212 C435 185 425 140 395 140 Z'/>
        <path d='M615 100 C585 100 575 145 598 172 C618 196 630 222 630 255 L600 255 L600 270 L680 270 L680 255 L650 255 C650 222 662 196 682 172 C705 145 695 100 665 100 Z'/>
        <path d='M740 430 C740 375 780 345 810 345 C842 345 875 375 875 430 L860 520 L755 520 Z'/>
        <rect x='785' y='520' width='50' height='80' rx='10'/>
        <rect x='795' y='600' width='30' height='30' rx='6'/>
        <circle cx='235' cy='500' r='52'/>
        <rect x='225' y='548' width='20' height='70' rx='8'/>
        <ellipse cx='245' cy='620' rx='45' ry='10'/>
      </g>
    </svg>
    """
    background_image = base64.b64encode(svg.encode("utf-8")).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.92)),
                url("data:image/svg+xml;base64,{background_image}");
            background-size: cover;
            background-attachment: fixed;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(245,250,247,0.98), rgba(232,244,237,0.98));
        }}

        div[data-testid="metric-container"] {{
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(26,107,60,0.12);
            padding: 12px 16px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }}

        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# Funciones auxiliares
# ==========================================================
def asignar_region(iso3: str) -> str:
    """Asigna una región según el orden definido por el usuario."""
    if pd.isna(iso3):
        return "Otras / Sin clasificar"

    for region in REGION_ORDER:
        if iso3 in REGION_MAP[region]:
            return region
    return "Otras / Sin clasificar"


@st.cache_data
def cargar_y_preparar_datos(url: str) -> pd.DataFrame:
    """Carga la base, normaliza columnas y deja lista la data para el dashboard."""
    df = pd.read_csv(url)

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_", regex=False)
    )

    columnas_numericas = [
        "YEAR", "ALCOHOL_LITERS_PER_CAPITA", "LOWER_CI", "UPPER_CI", "CI_WIDTH"
    ]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "COUNTRY" in df.columns:
        df["COUNTRY"] = df["COUNTRY"].astype(str).str.strip()

    if "SEX" in df.columns:
        df["SEX"] = df["SEX"].astype(str).str.strip().str.title()

    if "ISO3" in df.columns:
        df["ISO3"] = df["ISO3"].astype(str).str.strip().str.upper()

    df = df[df["YEAR"].between(ANIOS_ANALISIS[0], ANIOS_ANALISIS[1])].copy()
    df["REGION"] = df["ISO3"].apply(asignar_region)
    df = df[df["REGION"].isin(REGION_ORDER)].copy()

    for col in ["LOWER_CI", "UPPER_CI", "CI_WIDTH"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df


def tabla_formateada(df: pd.DataFrame, columnas_decimales=None):
    """Aplica formato simple para mostrar tablas de forma más limpia."""
    columnas_decimales = columnas_decimales or []
    formato = {col: "{:.2f}" for col in columnas_decimales if col in df.columns}
    return df.style.format(formato)


def construir_filtros(data: pd.DataFrame):
    """Centraliza los filtros globales y la navegación por secciones."""
    st.sidebar.header("Navegación y filtros")

    seccion_activa = st.sidebar.radio(
        "Sección del dashboard",
        options=SECCIONES,
        index=0
    )

    sex_options = sorted(data["SEX"].dropna().unique().tolist())
    default_sex = ["Both Sexes"] if "Both Sexes" in sex_options else sex_options[:1]
    selected_sex = st.sidebar.multiselect(
        "Sexo",
        options=sex_options,
        default=default_sex
    )

    selected_regions_global = st.sidebar.multiselect(
        "Regiones a incluir",
        options=REGION_ORDER,
        default=REGION_ORDER,
        help="Este filtro afecta todo el dashboard."
    )

    selected_years = st.sidebar.slider(
        "Rango de años",
        min_value=ANIOS_ANALISIS[0],
        max_value=ANIOS_ANALISIS[1],
        value=ANIOS_ANALISIS
    )

    top_n = st.sidebar.selectbox(
        "Top de países para rankings",
        options=[5, 10, 15, 20],
        index=1
    )

    return seccion_activa, selected_sex, selected_regions_global, selected_years, top_n


def mostrar_encabezado():
    st.title("🌍 Dashboard de Consumo de Alcohol por Regiones")
    st.markdown(
        "Análisis interactivo del consumo de alcohol per cápita **solo entre 2015 y 2019**, "
        "organizado por regiones y países."
    )
    st.caption(
        "Ahora el panel funciona por secciones: eliges una vista y solo se muestra esa página para que la lectura sea más limpia."
    )
    st.markdown("---")


def mostrar_resumen_general(df_filtered: pd.DataFrame):
    st.header("📌 Resumen general")
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Regiones analizadas", df_filtered["REGION"].nunique())
    with k2:
        st.metric("Países analizados", df_filtered["COUNTRY"].nunique())
    with k3:
        st.metric("Promedio general (L/cápita)", f"{df_filtered['ALCOHOL_LITERS_PER_CAPITA'].mean():.2f}")
    with k4:
        st.metric("Valor máximo observado", f"{df_filtered['ALCOHOL_LITERS_PER_CAPITA'].max():.2f}")

    st.markdown("### Vista rápida de evolución anual")
    resumen_anual = (
        df_filtered.groupby("YEAR")["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
    )
    fig = px.line(
        resumen_anual,
        x="YEAR",
        y="ALCOHOL_LITERS_PER_CAPITA",
        markers=True,
        title="Promedio general por año",
        labels={"YEAR": "Año", "ALCOHOL_LITERS_PER_CAPITA": "Litros per cápita"}
    )
    st.plotly_chart(fig, use_container_width=True)


def mostrar_paises_por_region(df_filtered: pd.DataFrame):
    st.header("📋 Países organizados por región (2015–2019)")

    tabla_regiones = (
        df_filtered[["REGION", "COUNTRY", "ISO3"]]
        .drop_duplicates()
        .sort_values(["REGION", "COUNTRY"])
        .reset_index(drop=True)
    )

    resumen_region = (
        tabla_regiones.groupby("REGION")
        .agg(Paises=("COUNTRY", "nunique"))
        .reset_index()
    )

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### Resumen de países por región")
        st.dataframe(resumen_region, use_container_width=True)
    with c2:
        st.markdown("### Tabla ordenada por región y país")
        st.dataframe(tabla_regiones, use_container_width=True, height=420)


def mostrar_comparacion_regiones(df_filtered: pd.DataFrame):
    st.header("🌎 Comparación general entre regiones")

    region_avg = (
        df_filtered.groupby("REGION")["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
        .rename(columns={"ALCOHOL_LITERS_PER_CAPITA": "Promedio litros per cápita"})
        .sort_values("Promedio litros per cápita", ascending=False)
    )

    col_tabla_reg, col_graf_reg = st.columns([1, 2])

    with col_tabla_reg:
        st.markdown("### Tabla: promedio por región")
        st.dataframe(
            tabla_formateada(region_avg, ["Promedio litros per cápita"]),
            use_container_width=True
        )

    with col_graf_reg:
        fig_region = px.bar(
            region_avg,
            x="REGION",
            y="Promedio litros per cápita",
            color="REGION",
            text_auto=".2f",
            title="Consumo promedio por región (2015–2019)",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_region.update_layout(showlegend=False, xaxis_title="Región", yaxis_title="Litros per cápita")
        st.plotly_chart(fig_region, use_container_width=True)

    region_year = (
        df_filtered.groupby(["YEAR", "REGION"])["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
    )

    fig_region_trend = px.line(
        region_year,
        x="YEAR",
        y="ALCOHOL_LITERS_PER_CAPITA",
        color="REGION",
        markers=True,
        title="Evolución anual del consumo promedio por región",
        labels={
            "YEAR": "Año",
            "ALCOHOL_LITERS_PER_CAPITA": "Litros per cápita",
            "REGION": "Región"
        }
    )
    st.plotly_chart(fig_region_trend, use_container_width=True)


def mostrar_comparacion_paises_en_region(df_filtered: pd.DataFrame):
    st.header("🧭 Comparación entre países de una misma región")

    region_for_countries = st.selectbox(
        "Selecciona una región para comparar sus países",
        options=REGION_ORDER,
        index=0
    )

    countries_in_region = sorted(
        df_filtered.loc[df_filtered["REGION"] == region_for_countries, "COUNTRY"].dropna().unique().tolist()
    )

    default_countries = countries_in_region[: min(5, len(countries_in_region))]

    selected_countries = st.multiselect(
        f"Países disponibles en {region_for_countries}",
        options=countries_in_region,
        default=default_countries
    )

    df_country_compare = df_filtered[
        (df_filtered["REGION"] == region_for_countries) &
        (df_filtered["COUNTRY"].isin(selected_countries))
    ].copy()

    if df_country_compare.empty:
        st.info("Selecciona al menos un país para activar la comparación interna de la región.")
        return

    country_summary = (
        df_country_compare.groupby(["COUNTRY", "ISO3"])["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
        .rename(columns={"ALCOHOL_LITERS_PER_CAPITA": "Promedio litros per cápita"})
        .sort_values("Promedio litros per cápita", ascending=False)
    )

    cc1, cc2 = st.columns([1, 2])
    with cc1:
        st.markdown("### Tabla comparativa por país")
        st.dataframe(
            tabla_formateada(country_summary, ["Promedio litros per cápita"]),
            use_container_width=True
        )

    with cc2:
        fig_country_region = px.bar(
            country_summary,
            x="COUNTRY",
            y="Promedio litros per cápita",
            color="COUNTRY",
            text_auto=".2f",
            title=f"Comparación de países en {region_for_countries}",
            labels={
                "COUNTRY": "País",
                "Promedio litros per cápita": "Litros per cápita"
            }
        )
        fig_country_region.update_layout(showlegend=False)
        st.plotly_chart(fig_country_region, use_container_width=True)

    country_year = (
        df_country_compare.groupby(["YEAR", "COUNTRY"])["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
    )

    fig_country_trend = px.line(
        country_year,
        x="YEAR",
        y="ALCOHOL_LITERS_PER_CAPITA",
        color="COUNTRY",
        markers=True,
        title=f"Tendencia anual de países en {region_for_countries}",
        labels={
            "YEAR": "Año",
            "ALCOHOL_LITERS_PER_CAPITA": "Litros per cápita",
            "COUNTRY": "País"
        }
    )
    st.plotly_chart(fig_country_trend, use_container_width=True)


def mostrar_ranking_paises(df_filtered: pd.DataFrame, top_n: int):
    st.header("🏆 Ranking de países")

    country_avg = (
        df_filtered.groupby(["COUNTRY", "REGION"])["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
        .rename(columns={"ALCOHOL_LITERS_PER_CAPITA": "Promedio litros per cápita"})
        .sort_values("Promedio litros per cápita", ascending=False)
    )

    top_countries = country_avg.head(top_n).copy()
    bottom_countries = country_avg.tail(top_n).sort_values("Promedio litros per cápita", ascending=True).copy()

    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(f"### Top {top_n} países con mayor consumo")
        st.dataframe(
            tabla_formateada(top_countries.reset_index(drop=True), ["Promedio litros per cápita"]),
            use_container_width=True
        )
    with rc2:
        st.markdown(f"### Top {top_n} países con menor consumo")
        st.dataframe(
            tabla_formateada(bottom_countries.reset_index(drop=True), ["Promedio litros per cápita"]),
            use_container_width=True
        )


def mostrar_mapa(df_filtered: pd.DataFrame):
    st.header("🗺️ Mapa mundial")

    map_data = (
        df_filtered.groupby(["COUNTRY", "ISO3", "REGION"])["ALCOHOL_LITERS_PER_CAPITA"]
        .mean()
        .reset_index()
        .rename(columns={"ALCOHOL_LITERS_PER_CAPITA": "Promedio litros per cápita"})
    )

    fig_map = px.choropleth(
        map_data,
        locations="ISO3",
        color="Promedio litros per cápita",
        hover_name="COUNTRY",
        hover_data={"REGION": True, "Promedio litros per cápita": ":.2f", "ISO3": False},
        color_continuous_scale="YlOrRd",
        title="Consumo promedio de alcohol por país (2015–2019)"
    )
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True))
    st.plotly_chart(fig_map, use_container_width=True)


def mostrar_explorador(df_filtered: pd.DataFrame):
    st.header("🔎 Explorador de datos")
    display_cols = [
        c for c in [
            "REGION", "COUNTRY", "ISO3", "YEAR", "SEX",
            "ALCOHOL_LITERS_PER_CAPITA", "LOWER_CI", "UPPER_CI", "CI_WIDTH"
        ] if c in df_filtered.columns
    ]

    df_display = (
        df_filtered[display_cols]
        .sort_values(["REGION", "COUNTRY", "YEAR"])
        .reset_index(drop=True)
    )

    st.dataframe(
        tabla_formateada(
            df_display,
            ["ALCOHOL_LITERS_PER_CAPITA", "LOWER_CI", "UPPER_CI", "CI_WIDTH"]
        ),
        use_container_width=True,
        height=450
    )

    st.caption(
        f"Mostrando {len(df_display):,} registros filtrados | Fuente: WHO Global Alcohol Consumption Dataset"
    )


# ==========================================================
# App principal
# ==========================================================
def main():
    aplicar_estilos()
    mostrar_encabezado()

    try:
        data = cargar_y_preparar_datos(DATA_URL)
        st.sidebar.success("✅ Datos cargados correctamente")
    except Exception as e:
        st.error(f"No se pudo cargar la información: {e}")
        return

    if data.empty:
        st.warning("No hay datos disponibles para el rango 2015-2019.")
        return

    seccion_activa, selected_sex, selected_regions_global, selected_years, top_n = construir_filtros(data)

    df_filtered = data.copy()
    if selected_sex:
        df_filtered = df_filtered[df_filtered["SEX"].isin(selected_sex)]
    if selected_regions_global:
        df_filtered = df_filtered[df_filtered["REGION"].isin(selected_regions_global)]
    df_filtered = df_filtered[df_filtered["YEAR"].between(selected_years[0], selected_years[1])]

    if df_filtered.empty:
        st.warning("No hay datos con la combinación de filtros seleccionada.")
        return

    if seccion_activa == "Resumen general":
        mostrar_resumen_general(df_filtered)
    elif seccion_activa == "Países por región":
        mostrar_paises_por_region(df_filtered)
    elif seccion_activa == "Comparación entre regiones":
        mostrar_comparacion_regiones(df_filtered)
    elif seccion_activa == "Comparación dentro de una región":
        mostrar_comparacion_paises_en_region(df_filtered)
    elif seccion_activa == "Ranking de países":
        mostrar_ranking_paises(df_filtered, top_n)
    elif seccion_activa == "Mapa mundial":
        mostrar_mapa(df_filtered)
    elif seccion_activa == "Explorador de datos":
        mostrar_explorador(df_filtered)


if __name__ == "__main__":
    main()
