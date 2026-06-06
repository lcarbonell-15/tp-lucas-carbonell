---
name: regression-modeling
description: Usa cuando necesitas entrenar un modelo de regresion lineal para predecir una variable cuantitativa y evaluar su ajuste usando el coeficiente R-cuadrado.
compatibility: Python 3.10+, scikit-learn>=1.3, pandas>=2.0
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Regression Modeling

## Descripcion General

Implementa modelos de regresion lineal usando scikit-learn para predecir variables cuantitativas. Incluye split train/test, entrenamiento del modelo, y evaluacion con coeficiente R-cuadrado (R²).

## Cuando Usar

- Predecir valores continuos (ventas, precios, cantidades)
- Estimar proyecciones basadas en variables independientes
- Evaluar la precision predictiva de modelos lineales
- Analisis de hipotesis que requiere estimaciones o proyecciones
- Evaluar cuanto de la varianza explica el modelo

## Patron Principal

### 1. Preparacion de Features y Target

```python
import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_features_target(df, target_column, feature_columns):
    """
    Prepara matrices X (features) e y (target) para modelado.

    Args:
        df: DataFrame con datos
        target_column: Nombre de columna a predecir
        feature_columns: Lista de columnas predictoras
    """
    X = df[feature_columns]
    y = df[target_column]
    return X, y
```

### 2. Split Train/Test

```python
def split_train_test(X, y, test_size=0.2, random_state=42):
    """
    Divide datos en conjuntos de entrenamiento y prueba.

    Args:
        test_size: Proporcion para test (0.2 = 20%)
        random_state: Semilla para reproducibilidad
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test
```

### 3. Entrenamiento del Modelo

```python
from sklearn.linear_model import LinearRegression

def train_linear_regression(X_train, y_train):
    """
    Entrena modelo de regresion lineal.

    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
    """
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model
```

### 4. Prediccion y Evaluacion R²

```python
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def evaluate_model(model, X_test, y_test):
    """
    Evalua modelo con metricas de regresion.

    Returns:
        dict con R², RMSE, MAE
    """
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)

    return {
        'r2_score': r2,
        'rmse': rmse,
        'mae': mae,
        'predictions': y_pred
    }
```

### 5. Pipeline Completo de Regresion

```python
def full_regression_pipeline(df, target, features, test_size=0.2):
    """
    Pipeline completo de regresion lineal.

    Args:
        df: DataFrame con datos
        target: Nombre de columna objetivo
        features: Lista de columnas predictoras
        test_size: Proporcion de test
    """
    # 1. Preparar datos
    X, y = prepare_features_target(df, target, features)

    # 2. Split
    X_train, X_test, y_train, y_test = split_train_test(X, y, test_size)

    # 3. Entrenar
    model = train_linear_regression(X_train, y_train)

    # 4. Evaluar
    results = evaluate_model(model, X_test, y_test)

    # 5. Interpretar R²
    r2 = results['r2_score']
    if r2 >= 0.8:
        interpretation = "Excelente ajuste"
    elif r2 >= 0.6:
        interpretation = "Buen ajuste"
    elif r2 >= 0.4:
        interpretation = "Ajuste moderado"
    else:
        interpretation = "Ajuste faible - considerar mas features o otro modelo"

    results['interpretation'] = interpretation
    results['model'] = model
    results['features'] = features

    return results

# Ejemplo de uso
results = full_regression_pipeline(
    df,
    target='sales',
    features=['advertising_budget', 'population']
)

print(f"R²: {results['r2_score']:.4f}")
print(f"Interpretacion: {results['interpretation']}")
print(f"Coeficientes: {results['model'].coef_}")
print(f"Intercepto: {results['model'].intercept_}")
```

## Interpretacion de R²

| R² | Interpretacion |
|----|----------------|
| R² = 1.0 | Prediccion perfecta |
| R² ≥ 0.8 | Excelente ajuste - modelo explica >80% de varianza |
| 0.6 ≤ R² < 0.8 | Buen ajuste - considerar mejorar |
| 0.4 ≤ R² < 0.6 | Ajuste moderado - usable pero con limitaciones |
| R² < 0.4 | Ajuste faible - no confiable para prediccion |
| R² < 0 | Modelo peor que una linea horizontal |

## Errores Comunes

- **No verificarlinearidad** → Regresion lineal asume relacion lineal
- **Olvidar split train/test** → Sobreajuste si se evalua en datos de entrenamiento
- **No escalar features** → Coeficientes no comparables entre variables
- **Interpretar R² mal** → R² no indica causalidad

## Banderas Rojas - DETENER

- Entrenar regresion sin split train/test
- Usar R² como unica metrica (tambien incluir RMSE, MAE)
- No documentar que features se usaron y sus coeficientes
- Hacer predicciones fuera del rango de datos de entrenamiento
