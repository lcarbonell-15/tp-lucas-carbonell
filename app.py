import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

st.set_page_config(
    page_title="Impacto Ley 27.642 — General Cereals",
    page_icon="📊",
    layout="wide",
)

BASE = Path(__file__).parent

# ── CSS verde oscuro, blanco ────────────────────────────────────────────
BG = "#0d2818"
BG_CARD = "#1a4d2e"
BG_CARD_WARN = "#4d2b1a"
BG_CARD_ERR = "#4d1a1a"
BG_CARD_OK = "#1a4d2e"
BG_EXPANDER = "#153d24"
GREEN = "#00e676"
CYAN = "#00bcd4"
AMBER = "#ff9800"
RED = "#f44336"

st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.5rem; background-color: {BG}; }}
    .stApp {{ background-color: {BG}; }}
    h1, h2, h3, h4, h5 {{ color: #ffffff !important; }}
    h2 {{ border-bottom: 2px solid {GREEN}; padding-bottom: 0.3rem; }}
    p, li, span, label, div[data-testid="stMarkdownContainer"] {{ color: #e0e0e0 !important; }}
    .stMetric {{ background: {BG_CARD}; border-radius: 8px; padding: 12px; border-left: 4px solid {GREEN}; }}
    .stMetric label {{ color: #b0bec5 !important; }}
    .stMetric [data-testid="stMetricValue"] {{ color: #ffffff !important; }}
    .stMetric [data-testid="stMetricDelta"] {{ color: {GREEN} !important; }}
    .stTabs [data-baseweb="tab"] {{ color: #b0bec5; }}
    .stTabs [aria-selected="true"] {{ color: {GREEN} !important; border-bottom-color: {GREEN} !important; }}
    .stDataFrame {{ background-color: {BG_CARD}; }}
    div[data-testid="stVerticalBlock"] > div {{ color: #e0e0e0; }}
    .stAlert {{ background-color: {BG_CARD}; color: #ffffff; }}
    .stInfo {{ background-color: {BG_CARD}; border-left-color: {CYAN}; }}
    .stWarning {{ background-color: {BG_CARD_WARN}; border-left-color: {AMBER}; }}
    .stSuccess {{ background-color: {BG_CARD_OK}; border-left-color: {GREEN}; }}
    .stError {{ background-color: {BG_CARD_ERR}; border-left-color: {RED}; }}
    div[data-testid="stExpander"] {{ background-color: {BG_EXPANDER}; border: 1px solid {GREEN}; }}
    div[data-testid="stExpander"] summary {{ color: #ffffff !important; }}
    div[data-testid="stRadio"] label {{ color: #e0e0e0 !important; }}
    div[data-testid="stSelectbox"] label {{ color: #e0e0e0 !important; }}
    div[data-testid="stCheckbox"] label {{ color: #e0e0e0 !important; }}
    .stSelectbox div[data-baseweb="input"] {{ background-color: {BG_CARD}; color: #ffffff; }}
    .stMultiSelect div[data-baseweb="input"] {{ background-color: {BG_CARD}; color: #ffffff; }}
    code {{ background-color: {BG_CARD}; color: {GREEN}; }}
</style>
""", unsafe_allow_html=True)

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG_CARD,
    "axes.edgecolor": "#2e7d4f",
    "axes.labelcolor": "#ffffff",
    "xtick.color": "#b0bec5",
    "ytick.color": "#b0bec5",
    "text.color": "#ffffff",
    "grid.color": "#2e7d4f",
    "grid.alpha": 0.4,
    "legend.facecolor": BG_CARD,
    "legend.edgecolor": "#2e7d4f",
    "legend.labelcolor": "#ffffff",
})


# ═══════════════════════════════════════════════════════════════════════
#  CARGA DE DATOS (del notebook)
# ═══════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv(BASE / "data" / "Dataset_Limpio.csv", sep=";", encoding="utf-8-sig")
    df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
    df["AÑO_MES"] = df["FECHA"].dt.to_period("M")

    CON_OCTOGONO = ["COPOS","BOLITAS","ANILLOS","ALMOHADITAS",
                    "COPITAS","OSITOS","CARAMELITOS","HONEY GRAHAM","HONEY NUT",
                    "MANI","TURRON"]
    SIN_OCTOGONO = ["AVENA","GRANOLA","BRAN","CRISPIES",
                    "COPO INTEGRAL","BARRAS DE CEREAL"]

    def asignar(sub):
        s = str(sub).upper().strip()
        if any(p in s for p in CON_OCTOGONO):
            return "CON_OCTOGONO"
        if any(p in s for p in SIN_OCTOGONO):
            return "SIN_OCTOGONO"
        return "SIN_CLASIFICAR"

    df["OCTOGONO"] = df["SUBRUBRO_BI"].apply(asignar)

    LEY_DATE = pd.Timestamp("2022-07-01")
    df["PERIODO"] = df["FECHA"].apply(
        lambda x: "PRE_LEY" if pd.notna(x) and x < LEY_DATE else "POST_LEY"
    )

    df_v = df[(df["FORMULARIO"] == "FCD") & (df["CANTIDAD"] > 0)].copy()

    deflactor = {
        "2022-01": 12.71, "2022-02": 12.14, "2022-03": 11.38,
        "2022-04": 10.73, "2022-05": 10.21, "2022-06":  9.70,
        "2022-07":  9.03, "2022-08":  8.44, "2022-09":  7.95,
        "2022-10":  7.48, "2022-11":  7.13, "2022-12":  6.78,
        "2023-01":  6.40, "2023-02":  6.00, "2023-03":  5.57,
        "2023-04":  5.14, "2023-05":  4.77, "2023-06":  4.50,
        "2023-07":  4.23, "2023-08":  3.76, "2023-09":  3.34,
        "2023-10":  3.08, "2023-11":  2.73, "2023-12":  2.18,
        "2024-01":  1.81, "2024-02":  1.60, "2024-03":  1.44,
        "2024-04":  1.32, "2024-05":  1.27, "2024-06":  1.21,
        "2024-07":  1.17, "2024-08":  1.12, "2024-09":  1.08,
        "2024-10":  1.05, "2024-11":  1.02, "2024-12":  1.00,
    }
    df_v["MES_KEY"] = df_v["AÑO_MES"].astype(str)
    df_v["PRECIO_REAL"] = df_v["PRECIO"] * df_v["MES_KEY"].map(deflactor)

    meses_pre = df_v[df_v["PERIODO"] == "PRE_LEY"]["AÑO_MES"].nunique()
    meses_post = df_v[df_v["PERIODO"] == "POST_LEY"]["AÑO_MES"].nunique()

    return df, df_v, meses_pre, meses_post


df, df_v, MESES_PRE, MESES_POST = load_data()


# ═══════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════
st.title("Impacto de la Ley 27.642 de Etiquetado Frontal")
st.title("sobre General Cereals S.A.")
st.caption("Trabajo Practico Grupal  ·  Laboratorio de Metodos Cuantitativos  ·  FCE UBA  ·  1C 2026")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 1 — SOBRE LA EMPRESA
# ═══════════════════════════════════════════════════════════════════════
st.header("1. Sobre la empresa analizada")

with st.expander("Leer mas sobre General Cereals S.A.", expanded=False):
    st.markdown("""
**General Cereals S.A.** es una empresa argentina de capitales nacionales fundada en 1994,
dedicada a la elaboracion de cereales para el desayuno bajo su marca principal **NUTRI FOODS**.

Su portfolio incluye cereales azucarados (copos, bolitas, anillos, almohaditas) y
productos naturales (avena, granola, salvado), tanto para consumo hogar como insumos industriales.

En 2014 fue adquirida por el **Grupo Georgalos** y actualmente exporta a mas de 10 paises.
    """)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 2 — PREGUNTA DE INVESTIGACION
# ═══════════════════════════════════════════════════════════════════════
st.header("2. Pregunta de investigacion")

st.markdown("""
> **¿Los productos de General Cereals que recibieron octogonos de advertencia por la
> Ley 27.642 de etiquetado frontal vendieron menos unidades que los que no los recibieron,
> teniendo en cuenta que la inflacion ya de por si redujo el consumo general?**
""")

col1, col2, col3 = st.columns(3)
col1.metric("Volumen vendido", "Columna CANTIDAD")
col2.metric("Corte temporal", "PRE/POST ley (jul-2022)")
col3.metric("Clasificacion", "CON vs SIN octogono")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 3 — EXPLORACION DEL DATASET (INTERACTIVO)
# ═══════════════════════════════════════════════════════════════════════
st.header("3. Exploracion del dataset")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transacciones", f"{len(df):,}")
col2.metric("Columnas", df.shape[1])
col3.metric("Periodo", "Ene 2022 - Dic 2024")
col4.metric("Ventas validas (FCD)", f"{len(df_v):,}")

st.markdown("")

# Checkbox para explorar datos crudos
if st.checkbox("Mostrar primeras filas del dataset"):
    st.dataframe(df[["FECHA","FORMULARIO","DETALLE","PRECIO","CANTIDAD","SUBRUBRO_BI","MARCA_BI","AÑO"]].head(10), use_container_width=True)

if st.checkbox("Mostrar tipos de transaccion (FORMULARIO)"):
    form_counts = df["FORMULARIO"].value_counts()
    st.dataframe(
        pd.DataFrame({
            "Tipo": form_counts.index,
            "Cantidad": form_counts.values,
            "Descripcion": ["Factura de Venta (ventas reales)", "Nota de Credito (devoluciones)", "Factura Rectificativa (correcciones)"]
        }),
        use_container_width=True, hide_index=True
    )
    st.caption("Solo las FCD representan ventas reales. Las NCD tienen cantidad negativa (devoluciones).")

if st.checkbox("Mostrar distribucion por subrubro (SUBRUBRO_BI)"):
    subrubros = df["SUBRUBRO_BI"].value_counts()
    st.bar_chart(subrubros, color="#00e676")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 4 — CLASIFICACION OCTOGONO
# ═══════════════════════════════════════════════════════════════════════
st.header("4. Clasificacion: ¿Quienes llevan octogono?")

st.markdown("""
La columna `OCTOGONO` clasifica cada producto segun los limites del **Decreto 151/2022**.
""")

octo_counts = df["OCTOGONO"].value_counts()
col1, col2 = st.columns(2)
col1.metric("CON octogono", f"{octo_counts.get('CON_OCTOGONO', 0):,}")
col2.metric("SIN octogono", f"{octo_counts.get('SIN_OCTOGONO', 0):,}")

with st.expander("Ver productos clasificados en cada grupo", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**CON octogono**")
        con_rubros = df[df["OCTOGONO"] == "CON_OCTOGONO"]["SUBRUBRO_BI"].value_counts()
        st.dataframe(pd.DataFrame({"Subrubro": con_rubros.index, "Registros": con_rubros.values}), hide_index=True)
    with col2:
        st.markdown("**SIN octogono**")
        sin_rubros = df[df["OCTOGONO"] == "SIN_OCTOGONO"]["SUBRUBRO_BI"].value_counts()
        st.dataframe(pd.DataFrame({"Subrubro": sin_rubros.index, "Registros": sin_rubros.values}), hide_index=True)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 5 — PERIODO PRE/POST LEY
# ═══════════════════════════════════════════════════════════════════════
st.header("5. Corte temporal: pre vs post ley")

col1, col2 = st.columns(2)
col1.metric("Meses PRE_LEY", MESES_PRE, help="Enero - Junio 2022")
col2.metric("Meses POST_LEY", MESES_POST, help="Julio 2022 - Diciembre 2024")

st.warning(
    f"El periodo POST_LEY dura **{MESES_POST // MESES_PRE}x mas** que el PRE_LEY. "
    "Por eso todos los calculos comparativos usan **promedios mensuales**, no totales."
)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 6 — TRANSFORMACION 3: PRECIO REAL
# ═══════════════════════════════════════════════════════════════════════
st.header("6. Precio real deflactado por IPC")

st.markdown("""
Precios nominales deflactados con coeficientes FACPCE (base diciembre 2024).
**Inflacion acumulada (ene 2022 -> dic 2024): ~1171%**
""")

with st.expander("Ver coeficientes de deflacion FACPCE", expanded=False):
    deflactor_data = {
        "2022-01": 12.71, "2022-02": 12.14, "2022-03": 11.38,
        "2022-04": 10.73, "2022-05": 10.21, "2022-06":  9.70,
        "2022-07":  9.03, "2022-08":  8.44, "2022-09":  7.95,
        "2022-10":  7.48, "2022-11":  7.13, "2022-12":  6.78,
        "2023-01":  6.40, "2023-02":  6.00, "2023-03":  5.57,
        "2023-04":  5.14, "2023-05":  4.77, "2023-06":  4.50,
        "2023-07":  4.23, "2023-08":  3.76, "2023-09":  3.34,
        "2023-10":  3.08, "2023-11":  2.73, "2023-12":  2.18,
        "2024-01":  1.81, "2024-02":  1.60, "2024-03":  1.44,
        "2024-04":  1.32, "2024-05":  1.27, "2024-06":  1.21,
        "2024-07":  1.17, "2024-08":  1.12, "2024-09":  1.08,
        "2024-10":  1.05, "2024-11":  1.02, "2024-12":  1.00,
    }
    df_def = pd.DataFrame({"Mes": deflactor_data.keys(), "Coeficiente": deflactor_data.values()})
    st.dataframe(df_def, use_container_width=True, hide_index=True)

# Precio real por grupo
for grupo in ["CON_OCTOGONO", "SIN_OCTOGONO"]:
    sub = df_v[df_v["OCTOGONO"] == grupo]
    p_pre = sub[sub["PERIODO"] == "PRE_LEY"]["PRECIO_REAL"].mean()
    p_post = sub[sub["PERIODO"] == "POST_LEY"]["PRECIO_REAL"].mean()
    var = (p_post - p_pre) / p_pre * 100
    label = "CON octogono" if grupo == "CON_OCTOGONO" else "SIN octogono"
    st.metric(
        f"Precio real {label}",
        f"${p_post:,.0f}",
        delta=f"{var:+.1f}% desde pre-ley (${p_pre:,.0f})",
    )


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 7 — ESTADISTICAS + GRAFICOS INTERACTIVOS
# ═══════════════════════════════════════════════════════════════════════
st.header("7. Analisis grafico")

# ── GRAFICO 1: Serie temporal ──────────────────────────────────────────
st.subheader("Grafico 1 — Evolucion mensual de cantidades vendidas")

serie = (
    df_v.groupby(["AÑO_MES", "OCTOGONO"])["CANTIDAD"]
    .sum().unstack(fill_value=0)
)
serie.index = serie.index.to_timestamp()

fig1, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(serie.index, serie["CON_OCTOGONO"] / 1e6,
         color=GREEN, lw=2, label="CON octogono (copos, bolitas, anillos...)")
ax1.plot(serie.index, serie["SIN_OCTOGONO"] / 1e6,
         color=CYAN, lw=2, label="SIN octogono (avena, granola, bran...)")
ax1.axvline(pd.Timestamp("2022-07-01"), color=AMBER,
            lw=2, ls="--", label="Ley 27.642 (jul-2022)")
ax1.set_title("Evolucion mensual de cantidades vendidas\n"
              "Productos CON vs SIN octogono — General Cereals 2022-2024",
              fontsize=13)
ax1.set_xlabel("Mes")
ax1.set_ylabel("Millones de unidades vendidas")
ax1.legend()
ax1.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

with st.expander("Interpretacion del Grafico 1", expanded=True):
    st.markdown("""
    Las dos lineas cuentan historias distintas.
    Los productos CON octogono vienen de un volumen mucho mas alto en 2022,
    pero muestran una tendencia clara hacia abajo que se sostiene en el tiempo.
    Los productos SIN octogono arrancan mas bajos, crecen durante 2023 y
    caen junto con el consumo general en 2024.
    Ambos grupos vivieron la misma inflacion, pero reaccionaron de forma opuesta
    en 2023 — cuando la brecha es mas clara.
    """)

st.markdown("---")

# ── GRAFICO 2: Barras comparativas ─────────────────────────────────────
st.subheader("Grafico 2 — Promedio mensual pre/post ley")

total_periodo = (
    df_v.groupby(["PERIODO", "OCTOGONO"])["CANTIDAD"]
    .sum().unstack(fill_value=0)
)
prom_mensual = total_periodo.copy()
prom_mensual.loc["PRE_LEY"] /= MESES_PRE
prom_mensual.loc["POST_LEY"] /= MESES_POST

x = np.arange(2)
w = 0.35

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(x, prom_mensual["CON_OCTOGONO"] / 1e6, w,
        label="CON octogono", color=GREEN, alpha=0.85)
ax2.bar(x + w, prom_mensual["SIN_OCTOGONO"] / 1e6, w,
        label="SIN octogono", color=CYAN, alpha=0.85)

ax2.set_xticks(x + w / 2)
ax2.set_xticklabels(["Pre Ley\n(ene-jun 2022)", "Post Ley\n(jul 2022 - dic 2024)"])
ax2.set_ylabel("Promedio mensual (millones de unidades)")
ax2.set_title("Promedio mensual de ventas antes y despues de la Ley 27.642\n"
              "Normalizado por cantidad de meses — General Cereals",
              fontsize=12)
ax2.legend()
ax2.grid(True, axis="y", linestyle="--", alpha=0.4)

for i, col, color in [(0, "CON_OCTOGONO", GREEN), (1, "SIN_OCTOGONO", CYAN)]:
    v_pre = prom_mensual.loc["PRE_LEY", col]
    v_post = prom_mensual.loc["POST_LEY", col]
    var = (v_post - v_pre) / v_pre * 100
    ax2.annotate(f"{var:+.1f}%",
                 xy=(i + i * w + w / 2, v_post / 1e6 + 0.01),
                 ha="center", va="bottom", fontweight="bold",
                 color=color, fontsize=12)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

with st.expander("Interpretacion del Grafico 2", expanded=True):
    st.markdown("""
    Con el mismo punto de partida aproximado y el mismo contexto economico,
    un grupo cayo 18,3% y el otro subio 16,6%.
    Una brecha de casi 35 puntos porcentuales entre dos grupos dentro de la misma empresa,
    bajo la misma inflacion y distribuidos por los mismos canales.
    Esa magnitud es consistente con un efecto del etiquetado sobre la demanda,
    aunque no prueba causalidad por si sola.
    """)

st.markdown("---")

# ── GRAFICO 3: Precio real y cantidad ──────────────────────────────────
st.subheader("Grafico 3 — Precio real y cantidad vendida (paneles)")

precio_mes = (
    df_v.groupby(["AÑO_MES", "OCTOGONO"])["PRECIO_REAL"]
    .mean().unstack()
)
precio_mes.index = precio_mes.index.to_timestamp()

cant_mes = (
    df_v.groupby(["AÑO_MES", "OCTOGONO"])["CANTIDAD"]
    .sum().unstack()
)
cant_mes.index = cant_mes.index.to_timestamp()

fig3, axes = plt.subplots(1, 2, figsize=(12, 4))
fig3.suptitle(
    "Evolucion mensual del precio real y la cantidad vendida\n"
    "General Cereals 2022-2024 — por grupo de etiquetado",
    fontsize=13,
)

grupos = [
    ("CON_OCTOGONO", "CON octogono", GREEN, axes[0]),
    ("SIN_OCTOGONO", "SIN octogono", CYAN, axes[1]),
]

for col, label, color, ax in grupos:
    ax.plot(precio_mes.index, precio_mes[col] / 1000,
            color=color, lw=2, linestyle="-",
            label="Precio real prom. mensual (miles $, eje izq.)")
    ax.set_ylabel("Precio real promedio mensual\n(miles de $ de dic-2024)", fontsize=9)

    ax2 = ax.twinx()
    ax2.plot(cant_mes.index, cant_mes[col] / 1e6,
             color=color, lw=2, linestyle="--", alpha=0.6,
             label="Cantidad vendida (millones, eje der.)")
    ax2.set_ylabel("Cantidad total vendida por mes\n(millones de unidades)", fontsize=9)

    ax.axvline(pd.Timestamp("2022-07-01"), color=AMBER,
               lw=2, ls="--", label="Ley 27.642 (jul-2022)")

    ax.set_title(f"Productos {label}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Mes")
    ax.grid(True, linestyle="--", alpha=0.35)

    lineas_izq, etiq_izq = ax.get_legend_handles_labels()
    lineas_der, etiq_der = ax2.get_legend_handles_labels()
    ax.legend(lineas_izq + lineas_der, etiq_izq + etiq_der,
              fontsize=8, loc="upper left")

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

with st.expander("Interpretacion del Grafico 3", expanded=True):
    st.markdown("""
    En ambos paneles el precio real sube de manera muy similar: +9,1% para los CON octogono
    y +20,3% para los SIN octogono en terminos reales a lo largo de todo el periodo.

    Sin embargo, la cantidad cuenta historias completamente distintas en cada panel.
    En el panel CON octogono, la cantidad cae de manera sostenida desde julio 2022.
    En el panel SIN octogono, la cantidad sube durante 2023 y solo cae en 2024.

    El patron clave: en CON, el precio real sube mientras la cantidad baja.
    En SIN, precio y cantidad suben juntos en 2023.
    Esa diferencia de comportamiento, bajo precios reales casi identicos,
    es consistente con un efecto del etiquetado.
    """)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 8 — VENTAS ANUALES
# ═══════════════════════════════════════════════════════════════════════
st.header("8. Ventas anuales por grupo")

resumen_anual = (
    df_v.groupby(["AÑO", "OCTOGONO"])["CANTIDAD"]
    .sum().unstack(fill_value=0)
)

# Selector de año
años_disponibles = sorted(resumen_anual.index.tolist())
año_sel = st.selectbox("Seleccionar año para ver detalle:", años_disponibles, index=len(años_disponibles)-1)

if año_sel:
    col1, col2 = st.columns(2)
    con_val = resumen_anual.loc[año_sel, "CON_OCTOGONO"] if "CON_OCTOGONO" in resumen_anual.columns else 0
    sin_val = resumen_anual.loc[año_sel, "SIN_OCTOGONO"] if "SIN_OCTOGONO" in resumen_anual.columns else 0
    col1.metric(f"CON octogono ({año_sel})", f"{con_val:,.0f} unidades")
    col2.metric(f"SIN octogono ({año_sel})", f"{sin_val:,.0f} unidades")

st.markdown("**Tabla de ventas anuales:**")
st.dataframe(resumen_anual.style.format("{:,.0f}"), use_container_width=True)

st.markdown("**Variacion interanual:**")
var_anual = resumen_anual.pct_change().mul(100).round(1)
st.dataframe(var_anual.style.format("{:+.1f}%"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 9 — ELASTICIDAD INTERACTIVA
# ═══════════════════════════════════════════════════════════════════════
st.header("9. Elasticidad-arco precio/cantidad")

st.markdown("""
La **elasticidad precio de la demanda** usa la formula del punto medio (arco):

$$E = \\frac{(Q_1 - Q_0) / ((Q_0 + Q_1)/2)}{(P_1 - P_0) / ((P_0 + P_1)/2)}$$
""")

# Calcular elasticidad desde los datos
def elasticidad_arco(q0, q1, p0, p1):
    delta_q = (q1 - q0) / ((q0 + q1) / 2)
    delta_p = (p1 - p0) / ((p0 + p1) / 2)
    if delta_p == 0:
        return np.nan
    return delta_q / delta_p

resultados_e = []
for grupo in ["CON_OCTOGONO", "SIN_OCTOGONO"]:
    sub = df_v[df_v["OCTOGONO"] == grupo]
    pre = sub[sub["PERIODO"] == "PRE_LEY"]
    post = sub[sub["PERIODO"] == "POST_LEY"]
    q0 = pre["CANTIDAD"].sum() / MESES_PRE
    q1 = post["CANTIDAD"].sum() / MESES_POST
    p0 = pre["PRECIO"].mean()
    p1 = post["PRECIO"].mean()
    e = elasticidad_arco(q0, q1, p0, p1)
    vq = (q1 - q0) / q0 * 100
    vp = (p1 - p0) / p0 * 100
    resultados_e.append({"grupo": grupo, "q0": q0, "q1": q1, "p0": p0, "p1": p1, "vq": vq, "vp": vp, "e": e})

df_elast = pd.DataFrame(resultados_e)
df_elast["grupo_display"] = df_elast["grupo"].map({"CON_OCTOGONO": "CON octogono", "SIN_OCTOGONO": "SIN octogono"})

st.dataframe(
    df_elast[["grupo_display", "q0", "q1", "p0", "p1", "vq", "vp", "e"]].rename(columns={
        "grupo_display": "Categoria",
        "q0": "Q pre/mes", "q1": "Q post/mes",
        "p0": "P pre", "p1": "P post",
        "vq": "Var Q", "vp": "Var P", "e": "Elasticidad"
    }).style.format({
        "Q pre/mes": "{:,.0f}", "Q post/mes": "{:,.0f}",
        "P pre": "${:,.0f}", "P post": "${:,.0f}",
        "Var Q": "{:+.1f}%", "Var P": "{:+.1f}%",
        "Elasticidad": "{:.4f}",
    }),
    use_container_width=True, hide_index=True
)

# Interpretacion de elasticidades
e_con = df_elast[df_elast["grupo"] == "CON_OCTOGONO"]["e"].values[0]
e_sin = df_elast[df_elast["grupo"] == "SIN_OCTOGONO"]["e"].values[0]

st.subheader("Interpretacion interactiva")

grupo_elast = st.radio(
    "Elegir grupo para ver interpretacion de la elasticidad:",
    ["CON octogono", "SIN octogono"],
    horizontal=True,
)

if grupo_elast == "CON octogono":
    st.markdown(f"""
    **CON octogono: E = {e_con:.4f}** → demanda **INELASTICA** con caida de volumen

    - Precio nominal: ${resultados_e[0]["p0"]:,.0f} → ${resultados_e[0]["p1"]:,.0f} ({resultados_e[0]["vp"]:+.1f}%)
    - Precio real: $21,554 → $23,512 (+9.1%)
    - Cantidad: {resultados_e[0]["vq"]:+.1f}%
    - Por cada 1% de aumento de precio nominal, la cantidad cayo un {abs(e_con):.2f}%.
    - La demanda es inelastica: la caida de cantidad fue menor que el aumento de precio.
    """)
else:
    st.markdown(f"""
    **SIN octogono: E = +{e_sin:.4f}** → elasticidad **POSITIVA** (inusual)

    - Precio nominal: ${resultados_e[1]["p0"]:,.0f} → ${resultados_e[1]["p1"]:,.0f} ({resultados_e[1]["vp"]:+.1f}%)
    - Precio real: $24,640 → $29,632 (+20.3%)
    - Cantidad: {resultados_e[1]["vq"]:+.1f}%
    - El precio real de SIN subio mas que el de CON, pero la cantidad igualmente crecio.
    - Esto confirma que la diferencia no es de precio: es de preferencia.
    """)

st.info("""
**Nota metodologica:** La elasticidad-arco usa precios NOMINALES (formula del punto medio,
vista en clase). El analisis de precio real (T3) es complementario y sirve para verificar
que la divergencia de cantidades no se explica por precio.
""")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 10 — CONCLUSIONES
# ═══════════════════════════════════════════════════════════════════════
st.header("10. Conclusiones")

st.markdown("""
### Hallazgo principal

Los datos muestran una **divergencia clara y sostenida** entre productos CON y SIN octogono.
No es un efecto marginal ni puntual: se mantiene en el tiempo y aparece desde distintos
angulos del analisis.
""")

col1, col2 = st.columns(2)

with col1:
    st.error("""
### ¿Que descartamos?

La explicacion por **precio queda descartada** como factor determinante de la divergencia:
el grupo SIN octogono se encarecio **mas** en terminos reales (+20.3% vs +9.1%)
y sin embargo vendio mas. Si el precio hubiera sido el factor determinante, el resultado
deberia ser el contrario.
    """)

with col2:
    st.success("""
### ¿Que queda como factor mas plausible?

El **etiquetado frontal** como variable diferenciadora. Los consumidores respondieron
al octogono como senyal de alerta, reduciendo la compra de productos CON octogono
independientemente del precio.
    """)

st.markdown("---")

with st.expander("Limitaciones del estudio", expanded=False):
    st.markdown("""
    - Datos de **una sola empresa** (General Cereals) y un solo canal de distribucion
    - No sabemos si el comportamiento refleja lo que paso en el mercado argentino en general
    - No podemos descartar del todo otros factores internos de la empresa (cambios en portfolio,
      politica de precios, distribucion)
    """)

st.markdown("---")
st.caption("Trabajo Practico Grupal — Laboratorio de Metodos Cuantitativos — FCE UBA — 1C 2026")
