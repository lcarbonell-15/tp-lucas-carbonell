---
name: colab-notebook-optimizer
description: Usa cuando necesitas crear cuadernos Jupyter interactivos para ciencia de datos con parametros ajustables por usuarios sin editar codigo, cargar datos desde Google Drive o BigQuery, o optimizar el uso de aceleradores de hardware GPU/TPU.
compatibility: Python 3.10+ en Google Colab
metadata:
  author: dataops-standard-initiative
  version: "2.1.0"
---

# Colab Notebook Optimizer

## Descripcion General

Disena y optimiza cuadernos Jupyter para Google Colab con formularios interactivos, tablas de datos avanzadas, autenticacion en la nube y deteccion de aceleradores de hardware.

## Cuando Usar

- Crear cuadernos de ciencia de datos con hiperparametros ajustables por usuarios no tecnicos
- Cargar o guardar datos desde Google Drive en Colab
- Entrenar modelos PyTorch/TensorFlow con aceleracion GPU/TPU
- Crear plantillas de cuadernos reutilizables para equipos

## Patron Principal

### 1. Parametros Interactivos via Formularios Colab

Usa la sintaxis `#@param` en comentarios adyacentes a las asignaciones de variables:

```python
learning_rate = 0.001 #@param {type: "number"}
epochs = 150 #@param {type: "integer"}
dropout_rate = 0.3 #@param {type: "slider", min: 0.1, max: 0.9, step: 0.1}
batch_size = 64 #@param {type: "slider", min: 16, max: 512, step: 16}
optimizer_type = "AdamW" #@param ["AdamW", "SGD", "RMSprop"] {allow-input: true}
target_date = "2026-06-05" #@param {type: "date"}
enable_augmentation = True #@param {type: "boolean"}
```

### 2. Tablas de Datos Enriquecidas

Habilita el formateador dinamico de tablas de Colab para DataFrames de pandas:

```python
%load_ext google.colab.data_table
```

### 3. Almacenamiento en la Nube con Respaldo

```python
import os

def mount_storage_environment():
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        base_dir = '/content/drive/MyDrive/Colab_DataOps'
        os.makedirs(base_dir, exist_ok=True)
        print(f"Google Drive mounted: {base_dir}")
        return base_dir
    except ImportError:
        print("Local environment detected.")
        local_dir = './temp_dataops'
        os.makedirs(local_dir, exist_ok=True)
        return local_dir

workspace_path = mount_storage_environment()
```

### 4. Deteccion de Aceleradores de Hardware

```python
import torch

def verify_compute_backend():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("Using CPU")
    return device

device = verify_compute_backend()
```

## Referencia Rapida

| Tipo de Dato | Sintaxis |
|-----------|--------|
| Entero/Flotante | `#@param {type: "number"}` |
| Deslizador | `#@param {type: "slider", min: 0, max: 1, step: 0.1}` |
| Lista Desplegable | `#@param ["opt1", "opt2"] {allow-input: true}` |
| Fecha | `#@param {type: "date"}` |
| Booleano | `#@param {type: "boolean"}` |

## Librerias Fundamentales para Analisis Cuantitativo

Usa estas librerias segun el tipo de analisis requerido:

| Categoria | Libreria | Proposito |
|-----------|----------|-----------|
| Analisis de Datos | `pandas` | Manipular datos en tablas (DataFrames) |
| | `numpy` | Calculos numericos con arrays y matrices |
| | `scipy` | Funciones cientificas avanzadas (algebra, optimizacion, estadistica) |
| Graficos | `matplotlib` | Crear graficos (lineas, barras, dispersion) |
| | `seaborn` | Graficos estadisticos bonitos (mejora matplotlib) |
| Matematica Simbolica | `sympy` | Resolver ecuaciones, derivadas, integrales simbolicas |
| Finanzas | `numpy_financial` | Calculos financieros (intereses, VAN, TIR) |
| | `yfinance` | Descargar datos de precios de acciones y criptomonedas |
| Optimizacion | `pulp` | Resolver problemas de programacion lineal y entera |

### Instalacion en Colab

```python
!pip install pandas numpy scipy matplotlib seaborn sympy numpy_financial yfinance pulp
```

### Importacion Tipica

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sympy as sp
import numpy_financial as npf
import yfinance as yf
from pulp import *
```

## Errores Comunes

- **Omitir sintaxis de formularios** → Los usuarios deben editar codigo para cambiar parametros
- **Rutas hardcodeadas** → Falla al ejecutar localmente vs en Colab
- **Sin respaldo GPU** → El entrenamiento falla silenciosamente en CPU para modelos grandes
- **Falta `%load_ext`** → Las tablas de datos se renderizan como texto plano
- **No documentar librerias** → El usuario no sabe que dependencias instalar

## Banderas Rojas - DETENER

- Codigo sin `#@param` para hiperparametros ajustables
- `torch.device("cuda")` sin verificar `torch.cuda.is_available()`
- Montaje de Google Drive sin try/except para ejecucion local
- Cuaderno que solo funciona en GPU (sin respaldo CPU)
- Uso de libreria sin documentar su proposito o incluir instalacion
