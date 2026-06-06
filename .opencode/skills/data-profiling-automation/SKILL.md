---
name: data-profiling-automation
description: Usa cuando necesitas generar reportes automatizados de Analisis Exploratorio de Datos (EDA) en HTML o JSON, o cuando quieres detectar problemas de calidad de datos como valores faltantes, correlaciones y distribuciones.
compatibility: Python 3.10+, fg-data-profiling>=4.19
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Data Profiling Automation

## Descripcion General

Automatiza el Analisis Exploratorio de Datos (EDA) usando fg-data-profiling (anteriormente ydata-profiling) para generar reportes HTML/JSON completos con una sola linea de codigo. Detecta automaticamente problemas de calidad de datos.

## Cuando Usar

- Generar reportes EDA iniciales para datasets nuevos
- Detectar valores faltantes, duplicados y outliers
- Analizar correlaciones entre variables numericas
- Comparar versiones de datasets (antes/despues de preprocessing)
- Generar reportes de calidad de datos para stakeholders
- Analisis de series temporales con estacionalidad

## Patron Principal

### 1. Instalacion

```bash
pip install fg-data-profiling
```

### 2. Generacion Rapida de Reporte

```python
import pandas as pd
from data_profiling import ProfileReport

# Cargar datos
df = pd.read_csv('tu_dataset.csv')

# Generar reporte (1 linea)
profile = ProfileReport(df, title="Reporte de Datos")

# Exportar como HTML interactivo
profile.to_file("reporte_eda.html")

# O como JSON para integracion en pipelines
profile.to_file("reporte_eda.json")
```

### 3. Uso en Jupyter Notebooks

```python
# Widgets interactivos dentro del notebook
profile.to_widgets()

# Iframe embebido
profile.to_notebook_iframe()
```

### 4. Configuracion Avanzada

```python
# Reporte minimalista para datasets grandes
profile = ProfileReport(
    df,
    title="Reporte EDA",
    minimal=True,  # Solo analisis esencial
    explorative=True  # Incluye analisis de series temporales
)

# Excluir secciones especificas
profile = ProfileReport(
    df,
    title="Reporte EDA",
    correlations={
        "pearson": {"calculate": False},  # Desactivar correlacion Pearson
        "spearman": {"calculate": False}
    }
)
```

### 5. Comparacion de Datasets

```python
from data_profiling import ProfileReport

# Comparar antes y despues de preprocessing
df_before = pd.read_csv('raw_data.csv')
df_after = pd.read_csv('cleaned_data.csv')

before_profile = ProfileReport(df_before, title="Datos Crudos")
after_profile = ProfileReport(df_after, title="Datos Limpiados")

# Generar reporte comparativo
comparison = before_profile.compare(before_profile, after_profile)
comparison.to_file("comparacion_prepost.html")
```

## Contenido del Reporte

| Seccion | Contenido |
|---------|-----------|
| **Overview** | Shape, variables, missing values, duplicates |
| **Alerts** | Problemas de calidad (alta correlacion, skewness, ceros) |
| **Univariate** | Distribuciones, estadisticas descriptivas |
| **Multivariate** | Correlaciones, interacciones entre variables |
| **Time-Series** | Autocorrelacion, estacionalidad (si aplica) |
| **Text** | Categorias mas comunes, scripts, bloques (si aplica) |

## Librerias Relacionadas para EDA

| Proposito | Libreria | Install |
|-----------|----------|---------|
| Manipulacion de datos | `pandas` | `pip install pandas` |
| Calculos numericos | `numpy` | `pip install numpy` |
| Graficos estadisticos | `seaborn` | `pip install seaborn` |
| Analisis de series | `statsmodels` | `pip install statsmodels` |

## Errores Comunes

- **No leer documentacion de columnas** → El reporte incluye warnings sobre interpretacion de tipos
- **Datasets muy grandes sin minimal=True** → Memoria insuficiente
- **No comparar antes/despues** → No se evidencia el impacto del limpieza
- **Olvidar guardar el reporte** → El reporte solo existe en memoria

## Banderas Rojas - DETENER

- Escribir codigo EDA manual cuando fg-data-profiling puede hacerlo en 1 linea
- Generar reportes sin guardarlos a archivo
- No revisar la seccion "Alerts" del reporte
- Usar `ydata_profiling` en lugar de `data_profiling` (paquete renombrado)
