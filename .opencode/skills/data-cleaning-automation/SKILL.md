---
name: data-cleaning-automation
description: Usa cuando necesitas limpiar datasets con valores nulos, datos duplicados, o cuando debes reordenar indices despues de eliminaciones en un pipeline de ciencia de datos.
compatibility: Python 3.10+, pandas>=2.0
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Data Cleaning Automation

## Descripcion General

Estandariza la limpieza de datos siguiendo un pipeline estructurado: deteccion de nulos, estrategias de imputacion, eliminacion de duplicados, y reindexacion secuencial. Garantiza datos de calidad para analisis posterior.

## Cuando Usar

- Cargar datasets crudos que requieren limpieza antes de analisis
- Pipeline de datos donde cada fase debe dejar el dataframe en estado limpio
- Datasets con columnas numericas con valores faltantes (ej: salarios)
- Registros duplicados que distorsionan metricas
- **Paso obligatorio** antes de cualquier modelado predictivo

## Patron Principal

### 1. Deteccion de Valores Nulos

```python
import pandas as pd

def detect_nulls(df):
    """Analiza valores nulos por columna."""
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    null_df = pd.DataFrame({
        'columna': null_counts.index,
        'nulos': null_counts.values,
        'porcentaje': null_pct.values
    }).sort_values('porcentaje', ascending=False)
    return null_df[null_df['nulos'] > 0]
```

### 2. Estrategias de Imputacion

```python
def clean_numeric_nulls(df, column, strategy='median'):
    """
    Limpia valores nulos en columnas numericas.

    Args:
        df: DataFrame
        column: Nombre de columna a imputar
        strategy: 'median' (recomendado), 'mean', 'zero', 'drop'
    """
    if strategy == 'median':
        fill_value = df[column].median()
    elif strategy == 'mean':
        fill_value = df[column].mean()
    elif strategy == 'zero':
        fill_value = 0
    elif strategy == 'drop':
        return df.dropna(subset=[column])

    return df.fillna({column: fill_value})
```

###3. Imputacion para Variables Categoricas

```python
def clean_categorical_nulls(df, column, fill_value='Desconocido'):
    """Para variables categoricas o texto, usar valor fijo."""
    return df.fillna({column: fill_value})
```

### 4. Eliminacion de Duplicados

```python
def remove_duplicates(df, subset=None, keep='first'):
    """
    Elimina filas duplicadas.

    Args:
        subset: Columnas a considerar para identificar duplicados
        keep: 'first', 'last', False (eliminar todos)
    """
    return df.drop_duplicates(subset=subset, keep=keep)
```

### 5. Reindexacion Secuencial (OBLIGATORIO)

```python
def reindex_cleaned_data(df):
    """
    Reordena indices secuencialmente despues de cualquier limpieza.
    Este paso es OBLIGATORIO posterior a eliminacion de nulos o duplicados.
    """
    return df.reset_index(drop=True)
```

### 6. Pipeline Completo de Limpieza

```python
def full_cleaning_pipeline(df, numeric_strategies=None, categorical_strategies=None):
    """
    Pipeline completo de limpieza de datos.

    Args:
        numeric_strategies: Dict {columna: strategy} para numericas
        categorical_strategies: Dict {columna: fill_value} para categoricas
    """
    df_clean = df.copy()

    # 1. Eliminar duplicados primero
    df_clean = remove_duplicates(df_clean)

    # 2. Limpiar numericas
    if numeric_strategies:
        for col, strategy in numeric_strategies.items():
            df_clean = clean_numeric_nulls(df_clean, col, strategy)

    # 3. Limpiar categoricas
    if categorical_strategies:
        for col, fill_value in categorical_strategies.items():
            df_clean = clean_categorical_nulls(df_clean, col, fill_value)

    # 4. REINDEXAR (OBLIGATORIO)
    df_clean = reindex_cleaned_data(df_clean)

    return df_clean

# Ejemplo de uso
df_cleaned = full_cleaning_pipeline(
    df,
    numeric_strategies={'salary': 'median', 'age': 'mean'},
    categorical_strategies={'department': 'Desconocido'}
)
```

## Errores Comunes

- **No detectar nulos primero** → No sabes que columnas requieren limpieza
- **Usar media para columnas con outliers** → La media es sensible a valores extremos
- **Olvidar reindexar** → Indices no secuenciales causan errores en analisis posterior
- **No validar limpieza** → Verificar que los nulos fueron resueltos

## Banderas Rojas - DETENER

- Eliminar filas con nulos sin evaluar si son una porcion insignificante
- Usar `.mean()` para columnas con alta dispersion (salarios, precios)
- No hacer `.reset_index(drop=True)` despues de dropna() o drop_duplicates()
- Dejar valores nulos sin documentar la estrategia usada
