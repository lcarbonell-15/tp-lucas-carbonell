---
name: data-transformation-pipeline
description: Usa cuando necesitas convertir columnas a datetime, renombrar columnas a espanol, o fusionar dataframes con merge tipo left join en un pipeline de datos.
compatibility: Python 3.10+, pandas>=2.0
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Data Transformation Pipeline

## Descripcion General

Estandariza la transformacion de datos: conversion de tipos (especialmente fechas), renombramiento de columnas con diccionario descriptivo en espanol, y fusion de tablas mediante left join. Incluye validacion post-merge para detectar nulos generados.

## Cuando Usar

- Conversion de columnas string a formato datetime para analisis temporal
- Renombrar columnas de un dataset para legibilidad en espanol
- Enriquecer datasets principales con tablas auxiliares (maximo 2 tablas)
- Validar consistencia de datos despues de transformaciones
- Pipeline de enriquecimiento de datos para la catedra

## Patron Principal

### 1. Conversion a Datetime

```python
def convert_to_datetime(df, column, format=None, errors='coerce'):
    """
    Convierte columna a formato datetime.

    Args:
        df: DataFrame
        column: Nombre de columna a convertir
        format: Formato explicito (ej: '%Y-%m-%d') o None para deteccion automatica
        errors: 'coerce' para valores invalidos como NaT
    """
    df[column] = pd.to_datetime(df[column], format=format, errors=errors)
    return df
```

###2. Renombramiento de Columnas

```python
def rename_columns_to_spanish(df, rename_dict):
    """
    Renombra columnas usando diccionario descriptivo en espanol.

    Args:
        rename_dict: Dict {nombre_original: nombre_espanol}
    """
    return df.rename(columns=rename_dict)
```

### 3. Merge con Left Join

```python
def merge_left_join(df_main, df_aux, on_column, validate='1:1'):
    """
    Fusiona dataframes usando left join.

    Args:
        df_main: DataFrame principal
        df_aux: DataFrame auxiliar
        on_column: Columna clave para el merge
        validate: '1:1', '1:m', 'm:1' para verificar cardinalidad
    """
    df_merged = df_main.merge(df_aux, on=on_column, how='left', validate=validate)
    return df_merged
```

### 4. Validacion Post-Merge

```python
def validate_post_merge(df_before, df_after, key_columns):
    """
    Valida que el merge no genero nulos inesperados.

    Args:
        df_before: DataFrame antes del merge
        df_after: DataFrame despues del merge
        key_columns: Lista de columnas clave a verificar
    """
    validation_report = {}

    for col in key_columns:
        nulls_before = df_before[col].isna().sum() if col in df_before.columns else 0
        nulls_after = df_after[col].isna().sum()
        new_nulls = nulls_after - nulls_before

        validation_report[col] = {
            'nulls_before': nulls_before,
            'nulls_after': nulls_after,
            'new_nulls': new_nulls,
            'status': 'OK' if new_nulls == 0 else 'WARNING'
        }

    return validation_report
```

### 5. Pipeline Completo de Transformacion

```python
def full_transformation_pipeline(df, datetime_columns, rename_dict, df_aux=None, merge_key=None):
    """
    Pipeline completo de transformacion de datos.

    Args:
        df: DataFrame principal
        datetime_columns: Dict {columna: format} para conversion datetime
        rename_dict: Dict para renombrar a espanol
        df_aux: DataFrame auxiliar para merge (opcional)
        merge_key: Columna clave para merge (requiere df_aux)
    """
    df_transformed = df.copy()

    # 1. Convertir datetime
    for col, fmt in datetime_columns.items():
        df_transformed = convert_to_datetime(df_transformed, col, fmt)

    # 2. Renombrar columnas
    if rename_dict:
        df_transformed = rename_columns_to_spanish(df_transformed, rename_dict)

    # 3. Merge si hay dataframe auxiliar
    if df_aux is not None and merge_key:
        df_before_merge = df_transformed.copy()
        df_transformed = merge_left_join(df_transformed, df_aux, merge_key)

        # 4. Validar nulos post-merge
        validation = validate_post_merge(df_before_merge, df_transformed, [merge_key])
        print("Validacion post-merge:", validation)

    return df_transformed
```

## Restricciones del README

- **Maximo 2 tablas** en un merge (principal + auxiliar)
- Usar exclusivamente **left join** para enriquecimiento
- Documentar nulos generados por falta de coincidencia en la clave

## Errores Comunes

- **No convertir datetime antes de rename** → El diccionario puede no encontrar la columna
- **Olvidar validate post-merge** → Nulos silenciosos en datos enriquecidos
- **Merge con mas de 2 tablas** → Inconsistencia metodologica
- **No verificar tipos de datos** → Operaciones matematicas fallan en fechas tipo string

## Banderas Rojas - DETENER

- Usar merge que no sea left join para enriquecimiento de datos
- Fusionar mas de 2 tablas en un solo paso
- No validar nulos generados por el merge
- Renombrar columnas sin verificar que existen primero
