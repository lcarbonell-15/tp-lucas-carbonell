# Guía de Inicio: Trabajo Práctico Final

## Laboratorio de Métodos Cuantitativos Aplicados a la Gestión

Este repositorio contiene el desarrollo del **Trabajo Práctico Final**. A continuación, se detalla el pipeline estandarizado y estructurado paso a paso para el procesamiento, limpieza, enriquecimiento y análisis exploratorio de datos (EDA) según los lineamientos de la cátedra.

---

## 📋 Pipeline del Ciclo de Datos (Data Pipeline)

El ciclo de trabajo obligatorio para el procesamiento de la/s base/s de datos seleccionada/s se compone de las siguientes fases consecutivas:

```txt
[ Carga e Inspección ] ──> [ Limpieza de Nulos/Duplicados ] ──> [ Transformación/Merge ] ──> [ Análisis Exploratorio (EDA) ]
```

### 1. Selección e Inspección Inicial

* **Estructura de Datos:** Cargar la base de datos (CSV o Excel) utilizando Pandas. Inspeccionar las dimensiones básicas mediante `.shape` y los primeros registros con `.head()`.
* **Estadísticas Descriptivas:** Utilizar `.describe()` para obtener un panorama rápido de las métricas estadísticas clave (mínimos, máximos, desvíos estándares, percentiles y promedios).
* **Validación de Datos Curados:** En caso de utilizar un dataset pre-procesado o "curado", es obligatorio incluir y ejecutar las líneas de código de validación para fundamentar metodológicamente que la base se encuentra limpia.

### 2. Limpieza y Procesamiento de Datos (Fase Crítica)

El correcto tratamiento de anomalías evita la contaminación de los modelos predictivos y el sesgo en las visualizaciones:

* **Valores Nulos (`NaN` - Not a Number):**
  * Detectar la cantidad de nulos por columna utilizando `.isnull().sum()`.
  * **Estrategias Remediales:**
    1. *Eliminar filas:* Aplicable cuando las filas con datos faltantes representan una porción insignificante del dataset.
    2. *Imputación por la Mediana:* Recomendable para variables numéricas con alta dispersión (como salarios), previniendo el sesgo que introducen los valores extremos en la media tradicional.
    3. *Relleno Fijo:* Para variables categóricas o de texto, reemplazar los vacíos por términos como `"Desconocido"` mediante `.fillna()`.
* **Datos Duplicados:**
  * Evaluar si la repetición de registros distorsiona el objetivo del análisis.
  * Para eliminarlos, ejecutar `.drop_duplicates(subset=[...])` especificando la clave primaria o el identificador único.
* **Reindexación:** * **¡Paso Obligatorio!** Posterior a cualquier eliminación de nulos o duplicados, se debe reordenar la numeración secuencial de las filas utilizando `.reset_index(drop=True)`.

### 3. Transformación de Variables y Enriquecimiento

* **Normalización de Columnas:** Renombrar los encabezados utilizando `.rename(columns={...})` aplicando un diccionario descriptivo en español. Esto facilita la legibilidad del código y la prolijidad de los gráficos.
* **Tipos de Datos Temporales:** Convertir de forma explícita las columnas con fechas de tipo cadena/texto (`object`) a formato temporal (`datetime`).
* **Unión de Tablas (Merge):** * En caso de enriquecer el dataset principal con una segunda tabla, utilizar exclusivamente la lógica de **Left Join** (`.merge(..., how='left', on='clave_comun')`).
  * *Restricción:* Se permite trabajar con un máximo de **dos (2) tablas**. Evitar el uso de tres o más para mantener la consistencia metodológica.
  * Validar inmediatamente después del merge si se generaron nuevos valores nulos por falta de coincidencia.

### 4. Análisis Exploratorio de Datos (EDA) y Modelado

* **Agrupaciones Inteligentes:** Cruzar variables cualitativas con métricas cuantitativas utilizando `.groupby()`.
* **Filtros por Extremos:** Extraer subconjuntos de datos de interés (top rankings de rendimiento positivo o negativo) mediante `.nlargest()` y `.nsmallest()`.
* **Visualización Profesional:** * Emplear librerías como `Seaborn` o `Matplotlib`.
  * Diseñar gráficos limpios (de barras, histogramas de distribución, diagramas de dispersión) que prescindan de ruido visual.
  * Utilizar paletas de colores armónicas y de un mismo rango tonal, evitando saturaciones o efectos arcoíris distractores.
* **Modelado Predictivo (Regresión Lineal):**
  * Si el planteamiento de la hipótesis requiere estimaciones o proyecciones, utilizar el módulo `LinearRegression` de la librería `SKLearn`.
  * Evaluar la precisión predictiva y el ajuste de la nube de datos a la recta estimada a través del coeficiente de determinación **R-cuadrado ($R^2$)**.

---

## 🛠️ Herramientas y Librerías Utilizadas

* **Python 3.x**
* **Pandas** (Estructuración y manipulación de DataFrames)
* **NumPy** (Operaciones matriciales y algebraicas)
* **Matplotlib & Seaborn** (Visualización estática y análisis gráfico)
* **Scikit-Learn (SKLearn)** (Implementación de modelos analíticos cuantitativos)

---
