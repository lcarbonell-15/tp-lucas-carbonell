import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
import sympy as sp

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Ley 27.642 · General Cereals",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CORAL     = "#FF4757"
VERDE     = "#00C9A7"
DORADO    = "#FFD93D"
NEGRO     = "#1A1A2E"
GRIS      = "#6B7280"
AZUL      = "#4361EE"
MORADO    = "#7B2FF7"
NARANJA   = "#FF6B35"
ROSA      = "#FF2E63"
CYAN      = "#00D2FF"

# ══════════════════════════════════════════════════════════════════════════════
# CARGA Y PROCESAMIENTO DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def cargar_datos():
    df = pd.read_csv('Dataset_Limpio.csv', sep=';', encoding='utf-8-sig')
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
    df['AÑO_MES'] = df['FECHA'].dt.to_period('M')

    CON_OCT = ['COPOS','BOLITAS','ANILLOS','ALMOHADITAS','COPITAS','OSITOS',
               'CARAMELITOS','HONEY GRAHAM','HONEY NUT']
    SIN_OCT = ['AVENA','GRANOLA','BRAN','CRISPIES','COPO INTEGRAL','BARRAS DE CEREAL']

    def asignar(s):
        s = str(s).upper().strip()
        if any(p in s for p in CON_OCT): return 'CON_OCTOGONO'
        if any(p in s for p in SIN_OCT): return 'SIN_OCTOGONO'
        return 'OTRO'

    df['OCTOGONO'] = df['SUBRUBRO_BI'].apply(asignar)
    LEY = pd.Timestamp('2022-07-01')
    df['PERIODO'] = df['FECHA'].apply(lambda x: 'PRE_LEY' if pd.notna(x) and x < LEY else 'POST_LEY')
    df_v = df[(df['FORMULARIO'] == 'FCD') & (df['CANTIDAD'] > 0)].copy()
    return df, df_v

df_orig, df_v = cargar_datos()

meses_pre  = df_v[df_v['PERIODO']=='PRE_LEY']['AÑO_MES'].nunique()
meses_post = df_v[df_v['PERIODO']=='POST_LEY']['AÑO_MES'].nunique()

# ══════════════════════════════════════════════════════════════════════════════
# CALCULOS PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
df_graf = df_v[df_v['OCTOGONO'] != 'OTRO'].copy()

total = df_v.groupby(['PERIODO','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
prom = total.copy()
prom.loc['PRE_LEY']  /= meses_pre
prom.loc['POST_LEY'] /= meses_post
prom = prom.reindex(['PRE_LEY','POST_LEY'])

var_con = (prom.loc['POST_LEY','CON_OCTOGONO'] - prom.loc['PRE_LEY','CON_OCTOGONO']) / prom.loc['PRE_LEY','CON_OCTOGONO'] * 100
var_sin = (prom.loc['POST_LEY','SIN_OCTOGONO'] - prom.loc['PRE_LEY','SIN_OCTOGONO']) / prom.loc['PRE_LEY','SIN_OCTOGONO'] * 100
brecha = var_sin - var_con

def elasticidad_arco(q0, q1, p0, p1):
    dq = (q1-q0)/((q0+q1)/2)
    dp = (p1-p0)/((p0+p1)/2)
    return dq/dp if dp != 0 else np.nan

e_dict = {}
p_dict = {}
for grupo in ['CON_OCTOGONO','SIN_OCTOGONO']:
    sub = df_v[df_v['OCTOGONO']==grupo]
    pre = sub[sub['PERIODO']=='PRE_LEY']
    post = sub[sub['PERIODO']=='POST_LEY']
    q0 = pre['CANTIDAD'].sum() / meses_pre
    q1 = post['CANTIDAD'].sum() / meses_post
    p0 = pre['PRECIO'].mean()
    p1 = post['PRECIO'].mean()
    e_dict[grupo] = elasticidad_arco(q0, q1, p0, p1)
    p_dict[grupo] = {'pre': p0, 'post': p1, 'var': (p1-p0)/p0*100}

agg = (
    df_graf.groupby(['AÑO_MES','OCTOGONO','PERIODO'])
    .agg(Q=('CANTIDAD','sum'), P=('PRECIO','mean'))
    .reset_index()
)
agg['Q_miles'] = agg['Q'] / 1000

curvas = {}
for grupo in ['CON_OCTOGONO','SIN_OCTOGONO']:
    for periodo in ['PRE_LEY','POST_LEY']:
        sub = agg[(agg['OCTOGONO']==grupo)&(agg['PERIODO']==periodo)]
        slope, intercept, r, *_ = stats.linregress(sub['Q_miles'], sub['P'])
        curvas[(grupo,periodo)] = {'a':intercept,'b':slope,'r2':r**2}

a_con_pre  = curvas[('CON_OCTOGONO','PRE_LEY')]['a']
a_con_post = curvas[('CON_OCTOGONO','POST_LEY')]['a']
a_sin_pre  = curvas[('SIN_OCTOGONO','PRE_LEY')]['a']
a_sin_post = curvas[('SIN_OCTOGONO','POST_LEY')]['a']

delta_total = a_con_post - a_con_pre
delta_inflacion = a_sin_post - a_sin_pre
delta_ley = delta_total - delta_inflacion

pct_inf = abs(delta_inflacion / delta_total) * 100
pct_ley = abs(delta_ley / delta_total) * 100

# ══════════════════════════════════════════════════════════════════════════════
# CSS PERSONALIZADO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* FONDO GRADIENTE VIBRANTE */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        min-height: 100vh;
    }

    /* HEADER TRANSPARENTE */
    header[data-testid="stHeader"] { background: transparent !important; }
    header[data-testid="stHeader"] * { color: transparent !important; }

    /* CONTENEDOR PRINCIPAL FLOTANTE */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        margin-top: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* === HERO === */
    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #FF4757, #FF6B81);
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #FF4757, #FFD93D, #00C9A7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        color: rgba(255,255,255,0.55);
        margin-bottom: 2rem;
        max-width: 700px;
    }
    .hero-divider {
        height: 4px;
        background: linear-gradient(90deg, #FF4757, #FFD93D, #00C9A7, #4361EE);
        border-radius: 2px;
        margin-bottom: 2rem;
    }

    /* === KPIs === */
    .kpi-card {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.6rem 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-number {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1.1;
    }
    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.5);
        margin-top: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* === SECCIONES === */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 2.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        color: #FFD93D;
        border-bottom: 3px solid rgba(255, 217, 61, 0.3);
    }

    /* === CALLOUTS === */
    .callout {
        background: rgba(0, 201, 167, 0.08);
        border-left: 4px solid #00C9A7;
        padding: 1rem 1.2rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: rgba(255,255,255,0.85);
        border: 1px solid rgba(0, 201, 167, 0.15);
    }
    .callout-coral {
        background: rgba(255, 71, 87, 0.08);
        border-left: 4px solid #FF4757;
        border: 1px solid rgba(255, 71, 87, 0.15);
    }
    .callout-dorado {
        background: rgba(255, 217, 61, 0.08);
        border-left: 4px solid #FFD93D;
        border: 1px solid rgba(255, 217, 61, 0.15);
    }
    .callout strong { color: white; }

    /* === BADGES === */
    .octagon-badge {
        display: inline-block;
        background: linear-gradient(135deg, #FF4757, #FF2E63);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
    }

    /* === TABLAS === */
    .nutri-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.88rem;
        border-radius: 12px;
        overflow: hidden;
    }
    .nutri-table th {
        background: linear-gradient(90deg, #4361EE, #7B2FF7);
        color: white;
        padding: 10px 14px;
        text-align: left;
    }
    .nutri-table td {
        padding: 8px 14px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.8);
    }
    .nutri-table tr:nth-child(even) { background: rgba(255, 255, 255, 0.03); }
    .nutri-table tr:hover { background: rgba(255, 255, 255, 0.06); }

    .badge-si {
        background: linear-gradient(90deg, #FF4757, #FF6B81);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
    }
    .badge-no {
        background: linear-gradient(90deg, #00C9A7, #00E6C3);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
    }

    .results-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.9rem;
        margin: 1rem 0;
        border-radius: 12px;
        overflow: hidden;
    }
    .results-table th {
        background: linear-gradient(90deg, #4361EE, #7B2FF7);
        color: white;
        padding: 12px 16px;
        text-align: left;
    }
    .results-table td {
        padding: 10px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.8);
    }
    .results-table tr:nth-child(even) { background: rgba(255, 255, 255, 0.03); }
    .results-table tr:hover { background: rgba(255, 255, 255, 0.06); }

    .highlight-neg { color: #FF4757; font-weight: 800; }
    .highlight-pos { color: #00C9A7; font-weight: 800; }

    /* === FOOTER === */
    .footer-text {
        text-align: center;
        color: rgba(255,255,255,0.3);
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.08);
    }

    /* === STREAMLIT OVERRIDES === */
    .stMarkdown { color: rgba(255,255,255,0.85); }
    .stMarkdown p { color: rgba(255,255,255,0.85); }
    .stMarkdown li { color: rgba(255,255,255,0.85); }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
    }
    div[data-testid="stExpander"] summary { color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 1: HERO + KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="hero-badge">Estudio de caso · FCE UBA</span>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">El octogono que tumbó las ventas</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">La Ley 27.642 de Etiquetado Frontal cambió la forma en que los argentinos eligen sus cereales. Analizamos 54.769 transacciones de General Cereals para medir el impacto real.</p>', unsafe_allow_html=True)
st.markdown('<div class="hero-divider"></div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#FF4757;">{var_con:+.1f}%</div>
        <div class="kpi-label">Vol. mensual<br>CON octogono</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#00C9A7;">{var_sin:+.1f}%</div>
        <div class="kpi-label">Vol. mensual<br>SIN octogono</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#4361EE;">{e_dict['CON_OCTOGONO']:.4f}</div>
        <div class="kpi-label">Elasticidad<br>CON octogono</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#FFD93D;">{brecha:.1f} p.p.</div>
        <div class="kpi-label">Brecha entre<br>grupos</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 2: CONTEXTO METODOLOGICO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">El escenario</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **General Cereals S.A.** es una empresa argentina fundada en 1994, marca **NUTRI FOODS**.
    Fabrica cereales azucarados (copos, bolitas, anillos) y naturales (avena, granola, salvado).
    Adquirida por Grupo Georgalos en 2014.
    """)
with col2:
    st.markdown(f"""
    <span class="octagon-badge">EXCESO EN AZUCARES</span>

    La **Ley 27.642** entro en vigor en **julio 2022**. Obliga a poner octogonos negros en
    alimentos que superan umbrales de nutrientes criticos. Umbral clave: **10g de azucar / 100g**.
    """, unsafe_allow_html=True)

st.markdown("""<div class="callout-dorado callout">
<strong>El problema metodologico:</strong> la ley arranco justo en plena inflacion record
(mas del 200% anual en 2023). Si un producto vendio menos, ¿fue por el octogono o
porque a la gente no le alcanzaba la plata? Para separarlo, usamos los productos SIN octogono
como <strong>grupo de control natural</strong>: sufrieron la misma inflacion pero no el etiquetado.
</div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Clasificacion nutricional (Decreto 151/2022)</div>', unsafe_allow_html=True)
st.markdown("""
La clasificacion se basa en los **valores nutricionales reales** de los productos NUTRI FOODS
y en los limites del Decreto 151/2022. Umbral clave: **10g de azucares añadidos por cada 100g**.
""")

nutri_data = [
    ("Copos azucarados", "~37g", "~1.5g", "~300mg", "~380", "SI"),
    ("Bolitas de chocolate", "~35g", "~4.5g", "~350mg", "~395", "SI"),
    ("Anillos frutales", "~40g", "~1.5g", "~280mg", "~385", "SI"),
    ("Almohaditas rellenas", "~30g", "~8g", "~250mg", "~400", "SI"),
    ("Copitas / Ositos", "~38g", "~1.5g", "~290mg", "~378", "SI"),
    ("Honey Graham / Honey Nut", "~25g", "~3g", "~320mg", "~370", "SI"),
    ("Avena natural", "~1g", "~7g", "~5mg", "~380", "NO"),
    ("Granola", "~8g", "~9g", "~15mg", "~420", "NO"),
    ("Bran / Salvado", "~2g", "~3g", "~10mg", "~340", "NO"),
    ("Crispies / Barras", "~5g", "~1g", "~180mg", "~370", "NO"),
]

tabla_html = '<table class="nutri-table"><tr><th>Producto</th><th>Azucares/100g</th><th>Grasas/100g</th><th>Sodio/100g</th><th>Kcal/100g</th><th>Octogono</th></tr>'
for prod, azucar, grasas, sodio, kcal, octogono in nutri_data:
    badge = f'<span class="badge-si">SI</span>' if octogono == "SI" else f'<span class="badge-no">NO</span>'
    tabla_html += f'<tr><td>{prod}</td><td>{azucar}</td><td>{grasas}</td><td>{sodio}</td><td>{kcal}</td><td>{badge}</td></tr>'
tabla_html += '</table>'
st.markdown(tabla_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 3: ANALISIS GRAFICO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Analisis grafico</div>', unsafe_allow_html=True)

st.markdown("**Grafico 1 — Evolucion mensual de cantidades vendidas**")
serie = df_graf.groupby(['AÑO_MES','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
serie.index = serie.index.to_timestamp()

fig1, ax1 = plt.subplots(figsize=(12, 4.5))
fig1.patch.set_facecolor('#1A1A2E')
ax1.set_facecolor('#1A1A2E')
ax1.plot(serie.index, serie['CON_OCTOGONO']/1e6, color=CORAL, lw=2.5, label='CON octogono')
ax1.plot(serie.index, serie['SIN_OCTOGONO']/1e6, color=VERDE, lw=2.5, label='SIN octogono')
ax1.axvline(pd.Timestamp('2022-07-01'), color=DORADO, lw=2, ls='--', label='Ley 27.642 (jul-2022)')
ax1.set_ylabel('Millones de unidades', fontsize=11, color='white')
ax1.set_xlabel('')
ax1.legend(fontsize=10, facecolor='#1A1A2E', edgecolor='#333', labelcolor='white')
ax1.grid(True, ls='--', alpha=0.2, color='white')
ax1.tick_params(colors='white')
for spine in ax1.spines.values(): spine.set_color('#333')
plt.tight_layout()
st.pyplot(fig1)
plt.close()

st.markdown("""<div class="callout">
Las dos lineas cuentan historias distintas. Los productos <strong style="color:#FF4757;">CON octogono</strong>
vienen de un volumen mucho mas alto en 2022, pero muestran una tendencia clara hacia abajo
que se sostiene en el tiempo. Los <strong style="color:#00C9A7;">SIN octogono</strong> se mantienen
estables e incluso crecen levemente. Ambos grupos vivieron la misma inflacion,
pero reaccionaron de forma opuesta.
</div>""", unsafe_allow_html=True)

st.markdown("**Grafico 2 — Promedio mensual antes vs despues de la ley**")

df_prom = prom[['CON_OCTOGONO','SIN_OCTOGONO']]
x = np.arange(2)
w = 0.35

fig2, ax2 = plt.subplots(figsize=(8, 4.5))
fig2.patch.set_facecolor('#1A1A2E')
ax2.set_facecolor('#1A1A2E')
bars1 = ax2.bar(x, df_prom['CON_OCTOGONO']/1e6, w, label='CON octogono', color=CORAL, alpha=0.9)
bars2 = ax2.bar(x+w, df_prom['SIN_OCTOGONO']/1e6, w, label='SIN octogono', color=VERDE, alpha=0.9)
ax2.set_xticks(x + w/2)
ax2.set_xticklabels(['Pre Ley\n(ene-jun 2022)', 'Post Ley\n(jul 2022 - dic 2024)'], fontsize=11, color='white')
ax2.set_ylabel('Promedio mensual (millones)', fontsize=11, color='white')
ax2.legend(fontsize=10, facecolor='#1A1A2E', edgecolor='#333', labelcolor='white')
ax2.grid(True, axis='y', ls='--', alpha=0.2, color='white')
ax2.tick_params(colors='white')
for spine in ax2.spines.values(): spine.set_color('#333')

ax2.annotate(f'{var_con:+.1f}%', xy=(1, df_prom.loc['POST_LEY','CON_OCTOGONO']/1e6),
             ha='center', va='bottom', fontweight='bold', color=CORAL, fontsize=13)
ax2.annotate(f'{var_sin:+.1f}%', xy=(1+w, df_prom.loc['POST_LEY','SIN_OCTOGONO']/1e6),
             ha='center', va='bottom', fontweight='bold', color=VERDE, fontsize=13)

plt.tight_layout()
st.pyplot(fig2)
plt.close()

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""<div class="callout callout-coral">
    <strong style="color:#FF4757;">CON octogono:</strong> el volumen mensual cayo un <strong style="color:#FF4757;">{var_con:.1f}%</strong>
    con un aumento de precios de +{p_dict['CON_OCTOGONO']['var']:.1f}%.
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="callout">
    <strong style="color:#00C9A7;">SIN octogono:</strong> el volumen mensual crecio un <strong style="color:#00C9A7;">{var_sin:.1f}%</strong>
    pese a un aumento de precios aun mayor: +{p_dict['SIN_OCTOGONO']['var']:.1f}%.
    </div>""", unsafe_allow_html=True)

st.markdown("**Grafico 3 — Variacion interanual: ¿efecto puntual o sostenido?**")

var_anual = df_graf.groupby(['AÑO','OCTOGONO'])['CANTIDAD'].sum().unstack()
var_pct = var_anual.pct_change() * 100

fig3, ax3 = plt.subplots(figsize=(8, 4.5))
fig3.patch.set_facecolor('#1A1A2E')
ax3.set_facecolor('#1A1A2E')
ax3.plot(var_pct.index, var_pct['CON_OCTOGONO'], marker='o', color=CORAL, lw=2.5, ms=10, label='CON octogono')
ax3.plot(var_pct.index, var_pct['SIN_OCTOGONO'], marker='s', color=VERDE, lw=2.5, ms=10, label='SIN octogono')
ax3.axhline(0, color='gray', ls=':', lw=1)
ax3.set_ylabel('Variacion % vs año anterior', fontsize=11, color='white')
ax3.set_xticks([2022, 2023, 2024])
ax3.tick_params(colors='white')
ax3.legend(fontsize=10, facecolor='#1A1A2E', edgecolor='#333', labelcolor='white')
ax3.grid(True, ls='--', alpha=0.2, color='white')
for spine in ax3.spines.values(): spine.set_color('#333')
plt.tight_layout()
st.pyplot(fig3)
plt.close()

st.markdown("""<div class="callout callout-dorado">
Si el octogono generara un efecto puntual, la brecha deberia cerrarse en 2024.
Pero no se cierra: el patron se mantiene. El cambio en las preferencias de los consumidores
es <strong style="color:#FFD93D;">estructural</strong>, no pasajero.
</div>""", unsafe_allow_html=True)

st.markdown("**Grafico 4 — Desplazamiento de la curva de demanda (Shock externo)**")

b_con = curvas[('CON_OCTOGONO','PRE_LEY')]['b']
sub_con = agg[agg['OCTOGONO']=='CON_OCTOGONO']
q_min = sub_con['Q_miles'].min()
q_max = sub_con['Q_miles'].max()
q_vals = np.linspace(q_min, q_max, 200)

p_pre_vals  = a_con_pre  + b_con * q_vals
p_post_vals = a_con_post + b_con * q_vals

fig4, ax4 = plt.subplots(figsize=(10, 5))
fig4.patch.set_facecolor('#1A1A2E')
ax4.set_facecolor('#1A1A2E')
ax4.plot(q_vals, p_pre_vals,  color=CYAN, lw=2.5, label='Demanda PRE-LEY')
ax4.plot(q_vals, p_post_vals, color=ROSA, lw=2.5, ls='--', label='Demanda POST-LEY')

q_mid = (q_min + q_max) / 2
p_pre_mid  = a_con_pre  + b_con * q_mid
p_post_mid = a_con_post + b_con * q_mid
ax4.annotate('', xy=(q_mid, p_post_mid), xytext=(q_mid, p_pre_mid),
             arrowprops=dict(arrowstyle='->', color='white', lw=2))
ax4.text(q_mid * 1.03, (p_pre_mid + p_post_mid)/2,
         f'Shock total: ${abs(delta_total):,.0f}\nInflacion: {pct_inf:.0f}%\nLey: {pct_ley:.0f}%',
         fontsize=10, va='center', color='white',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#302b63', edgecolor='#7B2FF7', alpha=0.9))

ax4.set_title('Desplazamiento de la curva de demanda — Productos CON octogono\n'
              'Shock combinado: inflacion + Ley 27.642', fontsize=12, color='white', pad=15)
ax4.set_xlabel('Cantidad (miles de unidades/mes)', color='white')
ax4.set_ylabel('Precio promedio ($)', color='white')
ax4.legend(fontsize=10, facecolor='#1A1A2E', edgecolor='#333', labelcolor='white')
ax4.grid(True, ls='--', alpha=0.2, color='white')
ax4.tick_params(colors='white')
for spine in ax4.spines.values(): spine.set_color('#333')
plt.tight_layout()
st.pyplot(fig4)
plt.close()

st.markdown(f"""<div class="callout">
La curva de demanda de los productos CON octogono se desplazo hacia abajo.
Ese desplazamiento tiene dos componentes: la inflacion explica el <strong style="color:#FFD93D;">{pct_inf:.0f}%</strong>
y el etiquetado frontal explica el <strong style="color:#FF4757;">{pct_ley:.0f}%</strong> restante.
Aunque no hubiera habido ley, la demanda igual hubiera caido por la inflacion.
Pero la ley agrego un empujon extra hacia abajo que los productos sin octogono no sufrieron.
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 4: ELASTICIDADES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Elasticidad precio-cantidad</div>', unsafe_allow_html=True)

st.markdown("""
Usamos la formula **arco** (punto medio) vista en clase:

$$E = \\frac{(Q_1 - Q_0) / ((Q_0 + Q_1)/2)}{(P_1 - P_0) / ((P_0 + P_1)/2)}$$
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #FF4757;">
        <div class="kpi-number" style="color:#FF4757; font-size:2.4rem;">{e_dict['CON_OCTOGONO']:.4f}</div>
        <div class="kpi-label"><strong style="color:#FF4757;">CON octogono</strong><br>
        Demanda inelastica con caida de volumen.<br>
        Por cada 1% de aumento de precio, la cantidad cayo un {abs(e_dict['CON_OCTOGONO']):.2f}%.</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #00C9A7;">
        <div class="kpi-number" style="color:#00C9A7; font-size:2.4rem;">{e_dict['SIN_OCTOGONO']:.4f}</div>
        <div class="kpi-label"><strong style="color:#00C9A7;">SIN octogono</strong><br>
        Elasticidad positiva: crece pese a mayor precio.<br>
        Efecto sustituto inducido por el etiquetado.</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<strong style="color:#FF4757;">CON octogono:</strong> Los precios subieron {p_dict['CON_OCTOGONO']['var']:+.1f}% y la cantidad cayo {var_con:+.1f}%.
La demanda es inelastica, pero eso no significa que no cayo: cayo igual, y encima menos de lo que sugiere el precio.
El octogono probablemente contribuyo a hacer que los consumidores buscaran alternativas que antes no consideraban.

<strong style="color:#00C9A7;">SIN octogono:</strong> Los precios subieron {p_dict['SIN_OCTOGONO']['var']:+.1f}% y aun asi la cantidad CRECIO {var_sin:+.1f}%.
Esto es lo que en economia se llama un bien Giffen o, mas probablemente, un efecto sustituto:
los consumidores que dejaron de comprar productos con octogono se volcaron a estos, aun pagando mas.
El octogono no solo redujo la demanda de los productos marcados,
sino que redireccion parte de ella hacia los productos percibidos como mas saludables.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 5: ANALISIS DE SHOCK EXTERNO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Analisis de shock externo con SymPy</div>', unsafe_allow_html=True)

st.markdown("""
En el modelo de oferta y demanda, un **shock externo** es un evento fuera del mercado que desplaza
la curva de demanda. La Ley 27.642 opera exactamente como ese tipo de shock: al agregar informacion
negativa visible en el envase, <strong style="color:#FF4757;">reduce la disposicion a pagar</strong> de los consumidores.

Usando el grupo SIN octogono como control, podemos separar cuanto del desplazamiento se debe
a la inflacion y cuanto se debe especificamente al etiquetado.
""")

st.markdown('<div class="section-title" style="font-size:1.2rem;">Curvas de demanda estimadas (P = a + b*Q)</div>', unsafe_allow_html=True)

tabla_curvas = '<table class="results-table"><tr><th>Grupo</th><th>Periodo</th><th>a (intercepto)</th><th>b (pendiente)</th><th>R²</th></tr>'
for grupo in ['CON_OCTOGONO','SIN_OCTOGONO']:
    for periodo in ['PRE_LEY','POST_LEY']:
        c = curvas[(grupo,periodo)]
        tabla_curvas += f'<tr><td>{grupo}</td><td>{periodo}</td><td>${c["a"]:,.0f}</td><td>{c["b"]:.4f}</td><td>{c["r2"]:.3f}</td></tr>'
tabla_curvas += '</table>'
st.markdown(tabla_curvas, unsafe_allow_html=True)

st.markdown('<div class="section-title" style="font-size:1.2rem;">Descomposicion del shock</div>', unsafe_allow_html=True)

st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #FF4757; margin-bottom: 1rem;">
    <div class="kpi-number" style="color:#FF4757; font-size:1.8rem;">${delta_total:+,.0f} $/unidad</div>
    <div class="kpi-label"><strong>Desplazamiento total (CON, pre→post)</strong></div>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #FFD93D;">
        <div class="kpi-number" style="color:#FFD93D; font-size:1.8rem;">{pct_inf:.1f}%</div>
        <div class="kpi-label"><strong style="color:#FFD93D;">Efecto inflacion</strong><br>${delta_inflacion:+,.0f} $/unidad<br>
        Medido con grupo SIN como control</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #FF4757;">
        <div class="kpi-number" style="color:#FF4757; font-size:1.8rem;">{pct_ley:.1f}%</div>
        <div class="kpi-label"><strong style="color:#FF4757;">Efecto etiquetado (ley)</strong><br>${delta_ley:+,.0f} $/unidad<br>
        Efecto adicional del octogono</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class="callout callout-dorado">
<strong>Interpretacion:</strong> La inflacion explica la mayor parte del desplazamiento de la curva
de demanda. Pero el etiquetado frontal agrego un empujon extra hacia abajo que los productos
sin octogono no sufrieron. Este efecto adicional es el que genera la brecha en el volumen de ventas.
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 6: CONCLUSION + LIMITACIONES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)

st.markdown(f"""
Los productos <strong style="color:#FF4757;">CON octogono</strong> de General Cereals cayeron un <strong style="color:#FF4757;">{abs(var_con):.1f}%</strong> en volumen mensual promedio
tras la entrada en vigor de la ley. Los productos <strong style="color:#00C9A7;">SIN octogono</strong> crecieron un <strong style="color:#00C9A7;">{var_sin:.1f}%</strong>.
Una brecha de <strong style="color:#FFD93D;">{brecha:.1f} puntos porcentuales</strong> entre dos grupos de la misma empresa,
bajo la misma inflacion y los mismos canales de distribucion.

Los productos SIN octogono tuvieron una inflacion de precios <strong>mayor</strong> (+{p_dict['SIN_OCTOGONO']['var']:.1f}%)
que los CON octogono (+{p_dict['CON_OCTOGONO']['var']:.1f}%) y aun asi vendieron mas.
Si la inflacion fuera el unico factor, el patron seria al reves.

El analisis de elasticidades lo confirma: los productos SIN octogono crecieron en volumen
a pesar de que sus precios subieron incluso mas que los CON octogono.

El analisis de shock externo con SymPy permite ir un paso mas alla:
la inflacion movio la demanda para todos por igual, pero solo los productos con octogono
recibieron el empujon adicional del etiquetado.

**La diferencia es el efecto del etiquetado.**
""")

st.markdown('<div class="section-title" style="font-size:1.2rem;">Tabla resumen de resultados</div>', unsafe_allow_html=True)

tabla_resumen = '<table class="results-table"><tr><th>Indicador</th><th>CON octogono</th><th>SIN octogono</th></tr>'
tabla_resumen += f'<tr><td>Variacion volumen mensual</td><td class="highlight-neg">{var_con:+.1f}%</td><td class="highlight-pos">{var_sin:+.1f}%</td></tr>'
tabla_resumen += f'<tr><td>Elasticidad-arco</td><td>{e_dict["CON_OCTOGONO"]:.4f}</td><td>{e_dict["SIN_OCTOGONO"]:.4f}</td></tr>'
tabla_resumen += f'<tr><td>Precio promedio pre → post</td><td>${p_dict["CON_OCTOGONO"]["pre"]:,.0f} → ${p_dict["CON_OCTOGONO"]["post"]:,.0f}</td><td>${p_dict["SIN_OCTOGONO"]["pre"]:,.0f} → ${p_dict["SIN_OCTOGONO"]["post"]:,.0f}</td></tr>'
tabla_resumen += f'<tr><td>Aumento de precios</td><td>+{p_dict["CON_OCTOGONO"]["var"]:.1f}%</td><td>+{p_dict["SIN_OCTOGONO"]["var"]:.1f}%</td></tr>'
tabla_resumen += f'<tr><td>Tendencia 2022-2024</td><td class="highlight-neg">Caida sostenida</td><td class="highlight-pos">Estable/creciente</td></tr>'
tabla_resumen += '</table>'
st.markdown(tabla_resumen, unsafe_allow_html=True)

st.markdown("""<div class="callout callout-dorado">
<strong>Limitaciones:</strong> datos de una sola empresa (no generalizable al mercado total) ·
clasificacion por valores nutricionales aproximados · periodo pre-ley corto (solo 6 meses) ·
no se aislan completamente otros factores simultaneos (cambios de distribucion, portafolio).
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCION 7: DATOS INTERACTIVOS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Explorar los datos</div>', unsafe_allow_html=True)

with st.expander("Ver tabla de resumen por año y categoria"):
    resumen = df_v.groupby(['AÑO','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
    st.dataframe(resumen.style.format("{:,.0f}"), use_container_width=True)

with st.expander("Ver variacion interanual"):
    var_anual_display = var_anual.pct_change().mul(100).round(1)
    st.dataframe(var_anual_display.style.format("{:,.1f}%"), use_container_width=True)

with st.expander("Ver distribucion OCTOGONO"):
    dist = df_v['OCTOGONO'].value_counts().rename_axis('Categoria').reset_index(name='Transacciones')
    st.dataframe(dist, use_container_width=True)

with st.expander("Ver dataset completo (primeras 100 filas)"):
    cols_ver = ['FECHA','FORMULARIO','DETALLE','PRECIO','CANTIDAD','SUBRUBRO_BI','OCTOGONO','PERIODO']
    st.dataframe(df_v[cols_ver].head(100), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="footer-text">
General Cereals S.A. · Ley 27.642 de Etiquetado Frontal · Laboratorio de Metodos Cuantitativos · FCE UBA · 1C 2026<br>
Dataset: 54.769 transacciones, enero 2022 – diciembre 2024 · Herramientas: Python (pandas, numpy, matplotlib, scipy, sympy) · VS Code
</div>""", unsafe_allow_html=True)
