---
name: data-visualization-best-practices
description: Usa cuando necesitas crear graficos profesionales para informes o presentaciones, sin ruido visual, con paletas de color armonicas y siguiendo estandares de legibilidad.
compatibility: Python 3.10+, matplotlib>=3.7, seaborn>=0.12
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Data Visualization Best Practices

## Descripcion General

Crea visualizaciones profesionales siguiendo principios de Edward Tufte: maxima informacion con minima tinta, eliminacion de ruido visual, y paletas de color armonicas de un mismo tono.

## Cuando Usar

- Graficos para informes academicos o de gestion
- Dashboards que requieren claridad y profesionalismo
- Presentaciones donde la audiencia es no tecnica
- Cualquier visualizacion que accompagna texto explicativo
- Evitar graficos "arcoiris" o con saturacion excesiva

## Patron Principal

### 1. Configuracion Base

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configuracion profesional
plt.style.use('seaborn-v0_8-whitegrid')  # Fondo limpio con grid sutil
sns.set_palette("Blues")  # Paleta tonal azul (armonico)

# Configuracion de spines
def clean_spines(ax, keep=['bottom', 'left']):
    """Elimina spines innecesarios."""
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in keep:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_color('gray')
        ax.spines[spine].set_linewidth(0.5)
```

### 2. Paletas de Color Tonales

```python
# Paletas tonales (un solo color, diferentes intensidades)
TONAL_PALETTES = {
    'blues': sns.color_palette("Blues_d", n_colors=6),
    'greens': sns.color_palette("Greens_d", n_colors=6),
    'oranges': sns.color_palette("Oranges_d", n_colors=6),
    'grays': sns.color_palette("Greys_d", n_colors=6),
}

def get_tonal_palette(n_categories, palette='blues'):
    """Retorna paleta tonal para n categorias."""
    return sns.color_palette(palette, n_colors=n_categories)
```

### 3. Grafico de Barras Profesional

```python
def professional_bar_chart(df, x_col, y_col, title, xlabel, ylabel, palette='blues'):
    """
    Crea grafico de barras profesional.

    Args:
        df: DataFrame con datos
        x_col: Columna para eje X (categorica)
        y_col: Columna para eje Y (numerica)
        title: Titulo del grafico
        xlabel: Label eje X
        ylabel: Label eje Y
        palette: Nombre de paleta tonal
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = get_tonal_palette(len(df), palette)

    bars = ax.bar(df[x_col], df[y_col], color=colors, edgecolor='white', linewidth=1.5)

    # Limpiar spines
    clean_spines(ax)

    # Titulo y labels
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    # Eliminar gridlines verticales (ruido visual)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(False)

    # Formato de valores en Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    plt.tight_layout()
    return fig, ax
```

### 4. Grafico de Dispersion

```python
def professional_scatter_plot(df, x_col, y_col, hue_col, title, xlabel, ylabel):
    """Grafico de dispersion con paleta tonal."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Usar paleta tonal para el hue
    palette = sns.color_palette("Blues_d", n_colors=df[hue_col].nunique())

    scatter = sns.scatterplot(
        data=df, x=x_col, y=y_col, hue=hue_col,
        palette=palette, s=80, edgecolor='white', linewidth=0.5, ax=ax
    )

    clean_spines(ax)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    # Leyenda fuera del grafico
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    plt.tight_layout()
    return fig, ax
```

### 5. Histograma de Distribucion

```python
def professional_histogram(df, col, title, xlabel, bins=30):
    """Histograma con paleta tonal."""
    fig, ax = plt.subplots(figsize=(10, 6))

    n, bins, patches = ax.hist(df[col], bins=bins, color='steelblue',
                               edgecolor='white', linewidth=0.5)

    # Aplicar gradiente de color tonal
    colors = sns.color_palette("Blues_d", n_colors=len(patches))
    for patch, color in zip(patches, colors):
        patch.set_facecolor(color)

    clean_spines(ax)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel('Frecuencia', fontsize=11)

    plt.tight_layout()
    return fig, ax
```

## Reglas de Oro (Tufte Principles)

| Principio | Aplicacion |
|-----------|------------|
| **Maxima informacion, minima tinta** | Eliminar gridlines verticales, spines innecesarios |
| **No ruido visual** | Evitar 3D, efectos de sombra, colores brillantes |
| **Paletas tonales** | Un color, multiples intensidades (no arcoiris) |
| **Datos sobre decoracion** | El grafico debe poder entenderse en blanco y negro |
| **Proporcion** | Relación alto/ancho adecuada al tipo de dato |

## Errores Comunes

- **Usar paleta multicolor** → Grafico luce "arcoiris" y poco profesional
- **Mantener gridlines excesivos** → Distraen de los datos
- **No limpiar spines** → Apariencia de grafico por defecto de Excel
- **Labels sin formato** → Numeros sin separadores de miles o con demasiados decimales

## Banderas Rojas - DETENER

- Usar `plt.cm.rainbow` o paletas multicolor para comparaciones
- Mantener `ax.spines['top'].set_visible(True)` (spine superior distrae)
- Agregar efectos3D a graficos 2D
- Usar colores brillantes saturated (saturados > 80%)
- No incluir labels en ejes o titulos sin informacion
