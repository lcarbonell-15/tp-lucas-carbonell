import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Ley 27.642 · General Cereals",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta
CORAL  = "#E63946"
VERDE  = "#2A9D8F"
DORADO = "#E9C46A"
NEGRO  = "#1A1A1A"
GRIS   = "#6B7280"

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
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

# Calculos principales
total = df_v.groupby(['PERIODO','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
prom = total.copy()
prom.loc['PRE_LEY']  /= meses_pre
prom.loc['POST_LEY'] /= meses_post

var_con = (prom.loc['POST_LEY','CON_OCTOGONO'] - prom.loc['PRE_LEY','CON_OCTOGONO']) / prom.loc['PRE_LEY','CON_OCTOGONO'] * 100
var_sin = (prom.loc['POST_LEY','SIN_OCTOGONO'] - prom.loc['PRE_LEY','SIN_OCTOGONO']) / prom.loc['PRE_LEY','SIN_OCTOGONO'] * 100

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

# ══════════════════════════════════════════════════════════════════════════════
# CSS PERSONALIZADO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .block-container { max-width: 1100px; padding-top: 2rem; }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.4rem 1.2rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .kpi-number {
        font-family: 'Inter', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 2.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 3px solid #E9C46A;
    }
    .callout {
        background: #f0f7f5;
        border-left: 4px solid #2A9D8F;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.95rem;
    }
    .callout-coral {
        background: #fdf0f0;
        border-left: 4px solid #E63946;
    }
    .callout-dorado {
        background: #fdf8eb;
        border-left: 4px solid #E9C46A;
    }
    .octagon-badge {
        display: inline-block;
        background: #1a1a1a;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    .footer-text {
        text-align: center;
        color: #aaa;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    .nutri-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .nutri-table th { background: #1F4E79; color: white; padding: 8px 12px; text-align: left; }
    .nutri-table td { padding: 6px 12px; border-bottom: 1px solid #eee; }
    .nutri-table tr:nth-child(even) { background: #f5f8fb; }
    .badge-si { background: #fde8e8; color: #991b1b; padding: 2px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .badge-no { background: #e8f5e9; color: #1b5e20; padding: 2px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="hero-title">¿Los octogonos hicieron vender menos?</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Impacto de la Ley 27.642 de Etiquetado Frontal sobre las ventas de General Cereals S.A. · FCE UBA · 1C 2026</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:{CORAL}">−18,0%</div>
        <div class="kpi-label">Vol. mensual CON octogono</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:{VERDE}">+16,6%</div>
        <div class="kpi-label">Vol. mensual SIN octogono</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#1F4E79">−0,15</div>
        <div class="kpi-label">Elasticidad CON octogono</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="color:#633806">34,6 p.p.</div>
        <div class="kpi-label">Brecha entre grupos</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONTEXTO
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

# ══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN NUTRICIONAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Clasificacion nutricional (Decreto 151/2022)</div>', unsafe_allow_html=True)
st.markdown("""
La clasificacion se basa en los **valores nutricionales reales** de los productos NUTRI FOODS
y en los limites del Decreto 151/2022. El umbral clave es **10g de azucares añadidos por cada 100g** de producto.
""")

nutri_data = [
    ("Copos azucarados", "~37g", "SI"), ("Bolitas de chocolate", "~35g", "SI"),
    ("Anillos frutales", "~40g", "SI"), ("Almohaditas rellenas", "~30g", "SI"),
    ("Copitas / Ositos", "~38g", "SI"), ("Honey Graham / Honey Nut", "~25g", "SI"),
    ("Avena natural", "~1g", "NO"), ("Granola", "~8g", "NO"),
    ("Bran / Salvado", "~2g", "NO"), ("Crispies / Barras", "~5g", "NO"),
]

tabla_html = '<table class="nutri-table"><tr><th>Producto</th><th>Azucares/100g</th><th>Umbral</th><th>Octogono</th></tr>'
for prod, azucar, octogono in nutri_data:
    badge = f'<span class="badge-si">SI</span>' if octogono == "SI" else f'<span class="badge-no">NO</span>'
    tabla_html += f'<tr><td>{prod}</td><td>{azucar}</td><td>10g</td><td>{badge}</td></tr>'
tabla_html += '</table>'
st.markdown(tabla_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1: Serie temporal
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Evolucion mensual de ventas</div>', unsafe_allow_html=True)

df_graf = df_v[df_v['OCTOGONO'] != 'OTRO'].copy()
serie = df_graf.groupby(['AÑO_MES','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
serie.index = serie.index.to_timestamp()

fig1, ax1 = plt.subplots(figsize=(12, 4.5))
ax1.plot(serie.index, serie['CON_OCTOGONO']/1e6, color=CORAL, lw=2.5, label='CON octogono')
ax1.plot(serie.index, serie['SIN_OCTOGONO']/1e6, color=VERDE, lw=2.5, label='SIN octogono')
ax1.axvline(pd.Timestamp('2022-07-01'), color=DORADO, lw=2, ls='--', label='Ley 27.642 (jul-2022)')
ax1.set_ylabel('Millones de unidades', fontsize=11)
ax1.set_xlabel('')
ax1.legend(fontsize=10)
ax1.grid(True, ls='--', alpha=0.3)
ax1.set_facecolor('#FAFAFA')
fig1.patch.set_facecolor('#FAFAFA')
plt.tight_layout()
st.pyplot(fig1)
plt.close()

st.markdown("""<div class="callout">
Las dos lineas cuentan historias distintas. Los productos <strong>CON octogono</strong> (rojo)
caen de forma sostenida desde julio 2022. Los <strong>SIN octogono</strong> (verde) se mantienen
estables e incluso crecen. Mismo contexto economico, reacciones opuestas.
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2: Barras pre/post
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Promedio mensual: antes vs despues de la ley</div>', unsafe_allow_html=True)

df_prom = prom[['CON_OCTOGONO','SIN_OCTOGONO']]
x = np.arange(2)
w = 0.35

fig2, ax2 = plt.subplots(figsize=(8, 4.5))
bars1 = ax2.bar(x, df_prom['CON_OCTOGONO']/1e6, w, label='CON octogono', color=CORAL, alpha=0.9)
bars2 = ax2.bar(x+w, df_prom['SIN_OCTOGONO']/1e6, w, label='SIN octogono', color=VERDE, alpha=0.9)
ax2.set_xticks(x + w/2)
ax2.set_xticklabels(['Pre Ley\n(ene-jun 2022)', 'Post Ley\n(jul 2022 - dic 2024)'], fontsize=11)
ax2.set_ylabel('Promedio mensual (millones)', fontsize=11)
ax2.legend(fontsize=10)
ax2.grid(True, axis='y', ls='--', alpha=0.3)

# Anotar variaciones
ax2.annotate(f'{var_con:+.1f}%', xy=(1, df_prom.loc['POST_LEY','CON_OCTOGONO']/1e6),
             ha='center', va='bottom', fontweight='bold', color=CORAL, fontsize=13)
ax2.annotate(f'{var_sin:+.1f}%', xy=(1+w, df_prom.loc['POST_LEY','SIN_OCTOGONO']/1e6),
             ha='center', va='bottom', fontweight='bold', color=VERDE, fontsize=13)

ax2.set_facecolor('#FAFAFA')
fig2.patch.set_facecolor('#FAFAFA')
plt.tight_layout()
st.pyplot(fig2)
plt.close()

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""<div class="callout callout-coral">
    <strong>CON octogono:</strong> el volumen mensual cayo un <strong>18%</strong>
    con un aumento de precios de +{p_dict['CON_OCTOGONO']['var']:.1f}%.
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="callout">
    <strong>SIN octogono:</strong> el volumen mensual crecio un <strong>16,6%</strong>
    pese a un aumento de precios aun mayor: +{p_dict['SIN_OCTOGONO']['var']:.1f}%.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3: Variación interanual
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Variacion interanual: ¿efecto puntual o sostenido?</div>', unsafe_allow_html=True)

var_anual = df_graf.groupby(['AÑO','OCTOGONO'])['CANTIDAD'].sum().unstack()
var_pct = var_anual.pct_change() * 100

fig3, ax3 = plt.subplots(figsize=(8, 4.5))
ax3.plot(var_pct.index, var_pct['CON_OCTOGONO'], marker='o', color=CORAL, lw=2.5, ms=10, label='CON octogono')
ax3.plot(var_pct.index, var_pct['SIN_OCTOGONO'], marker='s', color=VERDE, lw=2.5, ms=10, label='SIN octogono')
ax3.axhline(0, color='gray', ls=':', lw=1)
ax3.set_ylabel('Variacion % vs año anterior', fontsize=11)
ax3.set_xticks([2022, 2023, 2024])
ax3.legend(fontsize=10)
ax3.grid(True, ls='--', alpha=0.3)
ax3.set_facecolor('#FAFAFA')
fig3.patch.set_facecolor('#FAFAFA')
plt.tight_layout()
st.pyplot(fig3)
plt.close()

st.markdown("""<div class="callout callout-dorado">
Si el octogono generara un efecto puntual, la brecha deberia cerrarse en 2024.
Pero no se cierra: el patron se mantiene. El cambio en las preferencias de los consumidores
es <strong>estructural</strong>, no pasajero.
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ELASTICIDADES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Elasticidad precio-cantidad</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {CORAL};">
        <div class="kpi-number" style="color:{CORAL}; font-size:2.2rem;">{e_dict['CON_OCTOGONO']:.4f}</div>
        <div class="kpi-label"><strong>CON octogono</strong><br>
        Inelastica con caida de volumen.<br>
        El octogono amplifico la resistencia al precio.</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {VERDE};">
        <div class="kpi-number" style="color:{VERDE}; font-size:2.2rem;">+{e_dict['SIN_OCTOGONO']:.4f}</div>
        <div class="kpi-label"><strong>SIN octogono</strong><br>
        Elasticidad positiva: crece pese a mayor precio.<br>
        Efecto sustituto inducido por el etiquetado.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
La **elasticidad positiva** del grupo SIN octogono es el hallazgo mas llamativo:
los consumidores pagaron mas y aun asi compraron mas. Esto solo se explica si una parte
de la demanda fue redirigida desde los productos con octogono hacia los percibidos como mas saludables.
""")

# ══════════════════════════════════════════════════════════════════════════════
# CONCLUSIÓN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)

st.markdown(f"""
Los productos **CON octogono** de General Cereals cayeron un **18%** en volumen mensual promedio
tras la entrada en vigor de la ley. Los productos **SIN octogono** crecieron un **16,6%**.
Una brecha de **34,6 puntos porcentuales** entre dos grupos de la misma empresa,
bajo la misma inflacion y los mismos canales de distribucion.

Los productos SIN octogono tuvieron una inflacion de precios **mayor** (+451,6%) que los CON octogono (+406,9%)
y aun asi vendieron mas. Si la inflacion fuera el unico factor, el patron seria al reves.

**La diferencia es el efecto del etiquetado.**
""")

st.markdown("""<div class="callout callout-dorado">
<strong>Limitaciones:</strong> datos de una sola empresa · clasificacion por valores nutricionales
aproximados · no se aislan completamente otros factores simultaneos.
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATOS INTERACTIVOS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Explorar los datos</div>', unsafe_allow_html=True)

with st.expander("Ver tabla de resumen por año y categoria"):
    resumen = df_v.groupby(['AÑO','OCTOGONO'])['CANTIDAD'].sum().unstack(fill_value=0)
    st.dataframe(resumen.style.format("{:,.0f}"), use_container_width=True)

with st.expander("Ver promedio mensual normalizado por periodo"):
    st.dataframe(prom[['CON_OCTOGONO','SIN_OCTOGONO']].style.format("{:,.0f}"), use_container_width=True)

with st.expander("Ver dataset completo (primeras 100 filas)"):
    cols_ver = ['FECHA','FORMULARIO','DETALLE','PRECIO','CANTIDAD','SUBRUBRO_BI','OCTOGONO','PERIODO']
    st.dataframe(df_v[cols_ver].head(100), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="footer-text">
General Cereals S.A. · Ley 27.642 de Etiquetado Frontal · Laboratorio de Metodos Cuantitativos · FCE UBA · 1C 2026<br>
Dataset: 54.769 transacciones, enero 2022 – diciembre 2024 · Herramientas: Python (pandas, numpy, matplotlib, sympy) · VS Code
</div>""", unsafe_allow_html=True)
