import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Impacto Ley 27.642 — General Cereals",
    page_icon="📊",
    layout="wide",
)

BASE = Path(__file__).parent

# ── CSS global — paleta verde y negro ──────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; background-color: #0a0a0a; }
    .stApp { background-color: #0a0a0a; }
    h1, h2, h3, h4 { color: #00e676 !important; }
    h2 { border-bottom: 2px solid #00e676; padding-bottom: 0.3rem; }
    .stMetric { background: #1a1a2e; border-radius: 8px; padding: 12px; border-left: 4px solid #00e676; }
    .stMetric label { color: #b0bec5 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #00e676 !important; }
    .stTabs [data-baseweb="tab"] { color: #b0bec5; }
    .stTabs [aria-selected="true"] { color: #00e676 !important; border-bottom-color: #00e676 !important; }
    .stMarkdown { color: #e0e0e0; }
    .stDataFrame { background-color: #1a1a2e; }
    div[data-testid="stVerticalBlock"] > div { color: #e0e0e0; }
    .stInfo { background-color: #1a1a2e; border-left-color: #00e676; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════
st.title("Impacto de la Ley 27.642 de Etiquetado Frontal sobre General Cereals S.A.")
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

    Su portfolio incluye:
    - **Cereales azucarados** (copos, bolitas, anillos, almohaditas) → reciben octogono
    - **Productos naturales** (avena, granola, salvado) → no reciben octogono

    En 2014 fue adquirida por el **Grupo Georgalos** y actualmente exporta a mas de 10 paises.
    """)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 2 — PREGUNTA DE INVESTIGACION
# ═══════════════════════════════════════════════════════════════════════
st.header("2. Pregunta de investigacion")

st.markdown("""
> **¿Los productos de General Cereals que recibieron octogonos de advertencia por la Ley 27.642
> vendieron menos unidades que los que no los recibieron, teniendo en cuenta que la inflacion
> ya de por si redujo el consumo general?**
""")

col1, col2, col3 = st.columns(3)
col1.metric("Volumen vendido", "Columna CANTIDAD")
col2.metric("Corte temporal", "PRE/POST ley (jul-2022)")
col3.metric("Clasificacion", "CON vs SIN octogono")

st.markdown("""
La empresa vende simultaneamente productos CON y SIN octogono, todos operando bajo la misma
inflacion, con la misma fuerza de ventas y distribuidos por los mismos canales. Si la inflacion
fuera el unico factor, esperariamos que ambos grupos evolucionaran de manera similar.
Una divergencia sostenida seria evidencia de que algo mas esta operando.
""")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 3 — METODOLOGIA
# ═══════════════════════════════════════════════════════════════════════
st.header("3. Metodologia: transformaciones aplicadas")

tab1, tab2, tab3 = st.tabs([
    "T1 — Clasificacion octogono",
    "T2 — Periodes pre/post ley",
    "T3 — Precio real deflactado",
])

with tab1:
    st.subheader("Transformacion 1: Clasificacion OCTOGONO")
    st.markdown("""
    Se creo la columna `OCTOGONO` que clasifica cada producto segun los limites del
    **Decreto 151/2022**: `CON_OCTOGONO` o `SIN_OCTOGONO`.

    **Limites del Decreto (Primera Etapa, vigente desde jul-2022):**
    """)

    df_limites = pd.DataFrame({
        "Nutriente critico": ["Azucares anadidos", "Grasas saturadas", "Grasas totales", "Sodio", "Calorias"],
        "Limite": [">= 10g/100g", ">= 4g/100g", ">= 10g/100g", ">= 400mg/100g", ">= 275 kcal/100g"],
    })
    st.dataframe(df_limites, use_container_width=True, hide_index=True)

    st.markdown("**Productos clasificados:**")
    df_prod = pd.DataFrame({
        "Producto": ["Copos azucarados", "Bolitas de chocolate", "Anillos frutales", "Almohaditas rellenas",
                      "Avena natural", "Granola", "Bran / Salvado", "Crispies de arroz"],
        "Azucares (g)": ["~37", "~35", "~40", "~30", "~1", "~8", "~2", "~5"],
        "Grasas tot. (g)": ["~1.5", "~4.5", "~1.5", "~8", "~7", "~9", "~3", "~1"],
        "Octogono": ["SI", "SI", "SI", "SI", "NO", "NO", "NO", "NO"],
    })
    st.dataframe(df_prod, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Transformacion 2: Periodes pre/post ley y normalizacion temporal")
    st.markdown("""
    Dos operaciones en una misma transformacion:

    1. **Etiquetado temporal**: cada transaccion es `PRE_LEY` (antes de julio 2022) o `POST_LEY` (desde julio 2022)
    2. **Filtrado**: solo ventas validas (formulario FCD, cantidad positiva)
    """)

    st.markdown("**Por que es critica la normalizacion:**")
    df_periodos = pd.DataFrame({
        "Periodo": ["PRE_LEY (ene-jun 2022)", "POST_LEY (jul 2022 - dic 2024)"],
        "Meses": [6, 30],
    })
    st.dataframe(df_periodos, use_container_width=True, hide_index=True)

    st.markdown("""
    El periodo POST_LEY dura **5x mas**. Comparar totales brutos seria como comparar el sueldo
    de un mes con el de cinco meses. Por eso todos los calculos comparativos usan
    **promedios mensuales**, no totales.
    """)

with tab3:
    st.subheader("Transformacion 3: Precio real deflactado por IPC")
    st.markdown("""
    Los precios nominales se deflactan usando los coeficientes de la tabla FACPCE para
    expresarlos en **moneda de diciembre 2024**.

    **Inflacion acumulada (ene 2022 -> dic 2024): ~1171%**
    """)

    df_precio = pd.DataFrame({
        "Grupo": ["CON_OCTOGONO", "SIN_OCTOGONO"],
        "Precio real pre": ["$21,554", "$24,640"],
        "Precio real post": ["$23,512", "$29,632"],
        "Variacion": ["+9.1%", "+20.3%"],
    })
    st.dataframe(df_precio, use_container_width=True, hide_index=True)

    st.warning("""
    **Hallazgo clave:** El grupo SIN octogono se encarecio **mas** en terminos reales que el CON,
    y sin embargo vendio mas. Que el grupo con mayor aumento de precio real sea el que gano
    volumen descarta la explicacion de precio como causa de la divergencia.
    """)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 4 — ESTADISTICAS CLAVE (INTERACTIVO)
# ═══════════════════════════════════════════════════════════════════════
st.header("4. Resultados estadisticos")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Dataset", "54,769 transacciones")
col2.metric("Periodo", "Ene 2022 - Dic 2024")
col3.metric("Categorias", "17 subrubros")
col4.metric("Ventas validas", "52,437 (FCD)")

st.markdown("")

# Selector interactivo de grupo
grupoSeleccionado = st.radio(
    "Seleccionar grupo para ver detalle:",
    ["CON octogono", "SIN octogono", "Comparar ambos"],
    horizontal=True,
)

if grupoSeleccionado == "CON octogono":
    st.subheader("Productos CON octogono")
    c1, c2, c3 = st.columns(3)
    c1.metric("Variacion cantidad mensual", "-18.3%", delta="Caida post-ley", delta_color="inverse")
    c2.metric("Precio real (pre -> post)", "+9.1%", delta="Menor que SIN")
    c3.metric("Elasticidad-arco", "-0.15", delta="Inelastica")
elif grupoSeleccionado == "SIN octogono":
    st.subheader("Productos SIN octogono")
    c1, c2, c3 = st.columns(3)
    c1.metric("Variacion cantidad mensual", "+16.6%", delta="Crecimiento post-ley", delta_color="normal")
    c2.metric("Precio real (pre -> post)", "+20.3%", delta="Mayor que CON")
    c3.metric("Elasticidad-arco", "+0.11", delta="Positiva (inusual)")
else:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("CON octogono")
        st.metric("Variacion cantidad mensual", "-18.3%", delta="Caida post-ley", delta_color="inverse")
        st.metric("Precio real (pre -> post)", "+9.1%", delta="Menor que SIN")
        st.metric("Elasticidad-arco", "-0.15", delta="Inelastica")
    with col_b:
        st.subheader("SIN octogono")
        st.metric("Variacion cantidad mensual", "+16.6%", delta="Crecimiento post-ley", delta_color="normal")
        st.metric("Precio real (pre -> post)", "+20.3%", delta="Mayor que CON")
        st.metric("Elasticidad-arco", "+0.11", delta="Positiva (inusual)")

st.markdown("")

st.subheader("Tabla resumen completa")

df_resumen = pd.DataFrame({
    "Indicador": [
        "Variacion cantidad mensual (pre vs post ley)",
        "Variacion precio REAL (deflactado FACPCE)",
        "Variacion precio NOMINAL (pre vs post ley)",
        "Elasticidad-arco precio/cantidad",
        "Tendencia interanual 2023",
        "Tendencia interanual 2024",
    ],
    "CON octogono": ["-18.3%", "+9.1%", "+408%", "-0.15 (inelastica)", "-12.1%", "-23.3%"],
    "SIN octogono": ["+16.6%", "+20.3%", "+452%", "+0.11 (positiva)", "+14.0%", "-28.0%"],
})

st.dataframe(df_resumen, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 5 — ANALISIS GRAFICO (INTERACTIVO)
# ═══════════════════════════════════════════════════════════════════════
st.header("5. Analisis grafico")

# Selector de grafico
graficoSeleccionado = st.selectbox(
    "Seleccionar grafico a visualizar:",
    [
        "Grafico 1 — Serie temporal de cantidades vendidas",
        "Grafico 2 — Comparacion pre/post ley por categoria",
        "Grafico 3 — Precio real y cantidad: las dos variables en paralelo",
    ],
)

IMG1 = BASE / "data" / "grafico1_serie_temporal.png"
IMG2 = BASE / "data" / "grafico2_barras.png"
IMG3 = BASE / "data" / "grafico3_precio_real_cantidad.png"

if graficoSeleccionado.startswith("Grafico 1"):
    st.subheader("Grafico 1 — Serie temporal de cantidades vendidas")
    st.image(str(IMG1), use_container_width=True)
    with st.expander("Ver interpretacion", expanded=True):
        st.markdown("""
        Los productos CON octogono vienen de un volumen mucho mas alto en 2022,
        pero muestran una tendencia clara hacia abajo que se sostiene en el tiempo.
        Los productos SIN octogono arrancan mas bajos, crecen durante 2023 y
        caen junto con el consumo general en 2024.
        Ambos grupos vivieron la misma inflacion, pero reaccionaron de forma opuesta
        en 2023 — cuando la brecha es mas clara.
        """)

elif graficoSeleccionado.startswith("Grafico 2"):
    st.subheader("Grafico 2 — Comparacion pre/post ley por categoria")
    st.image(str(IMG2), use_container_width=True)
    with st.expander("Ver interpretacion", expanded=True):
        st.markdown("""
        Con el mismo punto de partida aproximado y el mismo contexto economico,
        un grupo cayo 18,3% y el otro subio 16,6%. Una brecha de casi 35 puntos porcentuales
        entre dos grupos dentro de la misma empresa, bajo la misma inflacion y distribuidos
        por los mismos canales. Esa magnitud es consistente con un efecto del etiquetado
        sobre la demanda, aunque no prueba causalidad por si sola.
        """)

else:
    st.subheader("Grafico 3 — Precio real y cantidad: las dos variables en paralelo")
    st.image(str(IMG3), use_container_width=True)
    with st.expander("Ver interpretacion", expanded=True):
        st.markdown("""
        En ambos paneles el precio real sube de manera muy similar (+9.1% CON,
        +20.3% SIN). Sin embargo, la cantidad cuenta historias completamente distintas:
        en el panel CON octogono, la cantidad cae desde julio 2022 sin recuperacion visible.
        En el panel SIN octogono, la cantidad sube durante 2023 y solo cae en 2024.

        El patron clave esta en el cruce de las lineas: en CON, precio real sube y cantidad baja;
        en SIN, precio y cantidad suben juntos en 2023. Esa diferencia de comportamiento,
        bajo precios reales casi identicos, es consistente con un efecto del etiquetado.
        """)


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 6 — ELASTICIDAD (INTERACTIVO)
# ═══════════════════════════════════════════════════════════════════════
st.header("6. Elasticidad-arco precio/cantidad")

st.markdown("""
La **elasticidad precio de la demanda** mide que tan sensible es la cantidad demandada
ante un cambio en el precio. Usamos la formula del punto medio (arco):

$$E = \\frac{(Q_1 - Q_0) / ((Q_0 + Q_1)/2)}{(P_1 - P_0) / ((P_0 + P_1)/2)}$$
""")

with st.expander("¿Como se interpreta?", expanded=False):
    st.markdown("""
    - $|E| < 1$: demanda **inelastica** — los consumidores no cambian mucho su compra
    - $|E| > 1$: demanda **elastica** — muy sensibles al precio
    - Signo negativo: relacion inversa normal (sube precio → baja cantidad)
    - Signo positivo inesperado: otros factores compensan el aumento de precio
    """)

# Slider interactivo para comparar elasticidades
st.subheader("Comparacion interactiva de elasticidades")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### CON octogono")
    e_con = st.slider("Elasticidad CON", -1.0, 0.0, -0.15, 0.01, key="econ")
    st.markdown(f"""
    - **E = {e_con:.2f}** → demanda {'INELASTICA' if abs(e_con) < 1 else 'ELASTICA'}
    - Precio nominal: $1,982 → $10,072 (+408.3%)
    - Precio real: $21,554 → $23,512 (+9.1%)
    - Cantidad: -18.3%
    """)

with col2:
    st.markdown("#### SIN octogono")
    e_sin = st.slider("Elasticidad SIN", 0.0, 1.0, 0.11, 0.01, key="esin")
    st.markdown(f"""
    - **E = +{e_sin:.2f}** → elasticidad {'POSITIVA (inusual)' if e_sin > 0 else 'NORMAL'}
    - Precio nominal: $2,279 → $12,570 (+451.6%)
    - Precio real: $24,640 → $29,632 (+20.3%)
    - Cantidad: +16.6%
    """)

# Visualizacion de la diferencia
st.metric(
    "Brecha entre elasticidades",
    f"{abs(e_con) + abs(e_sin):.2f}",
    delta=f"CON {e_con:.2f} vs SIN +{e_sin:.2f}",
)

st.info("""
**Nota metodologica:** La elasticidad-arco usa precios NOMINALES (formula del punto medio,
vista en clase). El analisis de precio real (T3) es complementario y sirve para verificar
que la divergencia de cantidades no se explica por precio.
""")


# ═══════════════════════════════════════════════════════════════════════
#  SECCION 7 — CONCLUSIONES
# ═══════════════════════════════════════════════════════════════════════
st.header("7. Conclusiones")

st.markdown("""
### Hallazgo principal

Los datos muestran una **divergencia clara y sostenida** entre productos CON y SIN octogono.
No es un efecto marginal ni puntual: se mantiene en el tiempo y aparece desde distintos
angulos del analisis.
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ¿Que descartamos?")
    st.error("""
    La explicacion por **precio queda descartada** como factor determinante de la divergencia:
    el grupo SIN octogono se encarecio **mas** en terminos reales (+20.3% vs +9.1%)
    y sin embargo vendio mas. Si el precio hubiera sido el factor determinante, el resultado
    deberia ser el contrario.
    """)

with col2:
    st.markdown("### ¿Que queda como factor mas plausible?")
    st.success("""
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
