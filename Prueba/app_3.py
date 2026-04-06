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

    # Solo trabajaremos con 2015-2019 como pediste.
    df = df[df["YEAR"].between(ANIOS_ANALISIS[0], ANIOS_ANALISIS[1])].copy()

    # Crear columna de región respetando el orden dado.
    df["REGION"] = df["ISO3"].apply(asignar_region)

    # Mantener solo los países que quedaron dentro de las 5 regiones definidas.
    df = df[df["REGION"].isin(REGION_ORDER)].copy()

    # Relleno conservador para columnas de intervalo.
    for col in ["LOWER_CI", "UPPER_CI", "CI_WIDTH"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df


def tabla_formateada(df: pd.DataFrame, columnas_decimales=None):
    """Aplica formato simple para mostrar tablas de forma más limpia."""
    columnas_decimales = columnas_decimales or []
    formato = {col: "{:.2f}" for col in columnas_decimales if col in df.columns}
    return df.style.format(formato)


# ==========================================================
# App principal
# ==========================================================
def main():
    st.title("🌍 Dashboard de Consumo de Alcohol por Regiones")
    st.markdown(
        "Análisis interactivo del consumo de alcohol per cápita **solo entre 2015 y 2019**, "
        "organizado por regiones y países."
    )
    st.markdown("---")

    try:
        data = cargar_y_preparar_datos(DATA_URL)
        st.sidebar.success("✅ Datos cargados correctamente")
    except Exception as e:
        st.error(f"No se pudo cargar la información: {e}")
        return

    if data.empty:
        st.warning("No hay datos disponibles para el rango 2015-2019.")
        return

    # ------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------
    st.sidebar.header("Filtros globales")

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
        default=REGION_ORDER
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

    df_filtered = data.copy()
    if selected_sex:
        df_filtered = df_filtered[df_filtered["SEX"].isin(selected_sex)]
    if selected_regions_global:
        df_filtered = df_filtered[df_filtered["REGION"].isin(selected_regions_global)]
    df_filtered = df_filtered[df_filtered["YEAR"].between(selected_years[0], selected_years[1])]

    if df_filtered.empty:
        st.warning("No hay datos con la combinación de filtros seleccionada.")
        return

    # ------------------------------------------------------
    # KPIs
    # ------------------------------------------------------
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

    st.markdown("---")

    # ------------------------------------------------------
    # Tabla ordenada por región solicitada
    # ------------------------------------------------------
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

    st.markdown("---")

    # ------------------------------------------------------
    # Comparación general entre regiones
    # ------------------------------------------------------
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

    st.markdown(
        "**Lectura rápida:** esta vista permite comparar de forma directa el consumo promedio "
        "de alcohol entre las grandes regiones definidas en tu clasificación."
    )

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

    st.markdown("---")

    # ------------------------------------------------------
    # Comparación de países dentro de una misma región
    # ------------------------------------------------------
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

    if not df_country_compare.empty:
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
    else:
        st.info("Selecciona al menos un país para activar la comparación interna de la región.")

    st.markdown("---")

    # ------------------------------------------------------
    # Rankings de países
    # ------------------------------------------------------
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

    st.markdown("---")

    # ------------------------------------------------------
    # Mapa global
    # ------------------------------------------------------
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

    st.markdown("---")

    # ------------------------------------------------------
    # Explorador final
    # ------------------------------------------------------
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


if __name__ == "__main__":
    main()
