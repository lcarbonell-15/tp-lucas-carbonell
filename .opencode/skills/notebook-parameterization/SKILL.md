---
name: notebook-parameterization
description: Usa cuando necesitas ejecutar cuadernos Jupyter programaticamente con diferentes parametros desde CLI o API, para pipelines de datos que procesan笔记本 con diferentes fechas o configuraciones.
compatibility: Python 3.10+, papermill>=3.0
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Notebook Parameterization

## Descripcion General

Usa papermill para parametrizar, ejecutar y analizar cuadernos Jupyter programaticamente. Ideal para pipelines de datos que requieren ejecucion con diferentes configuraciones (fechas, paths, hiperparametros).

## Cuando Usar

- Ejecutar pipelines de datos diarios con diferentes fechas
- Optimizar hiperparametros de modelos iterando sobre valores
- Generar reportes automatizados para diferentes periodos
- Integrar cuadernos en sistemas de orquestacion (Airflow, Prefect, Dagster)
- CI/CD pipelines que requieren ejecucion de notebooks

## Patron Principal

### 1. Configurar Celda de Parametros

En el cuaderno, marca una celda con el tag `parameters`:

```python
# Este codigo se reemplazara en ejecucion
date = "2024-01-01"  #@param {type: "string"}
input_path = "/data/raw"  #@param {type: "string"}
output_path = "/data/processed"  #@param {type: "string"}
```

Para agregar el tag en Jupyter:
1. Selecciona la celda
2. Click en el icono de celda (celdas > tags)
3. Agrega el tag `parameters`

### 2. Ejecutar via Python API

```python
import papermill as pm

def execute_pipeline(notebook_path, output_path, parameters):
    """
    Ejecuta un cuaderno con parametros override.

    Args:
        notebook_path: Ruta al cuaderno de entrada (.ipynb)
        output_path: Ruta al cuaderno de salida
        parameters: Dict con parametros a inyectar
    """
    pm.execute_notebook(
        notebook_path,
        output_path,
        parameters=parameters,
        kernel_name="python3"
    )

# Ejemplo de uso
execute_pipeline(
    'pipeline_notebook.ipynb',
    'outputs/pipeline_2024-01-15.ipynb',
    parameters={
        'date': '2024-01-15',
        'input_path': '/data/raw',
        'output_path': '/data/processed'
    }
)
```

### 3. Ejecutar via CLI

```bash
# Instalacion
pip install papermill

# Ejecucion basica con -p para cada parametro
papermill input.ipynb output.ipynb -p date2024-01-15 -p input_path /data/raw

# Usando archivo YAML para parametros
papermill input.ipynb output.ipynb -f parameters.yaml

# Usando YAML inline
papermill input.ipynb output.ipynb -y "date: 2024-01-15\ninput_path: /data/raw"
```

### 4. Integracion con Cron

```bash
# Ejecutar diariamente a las 2 AM
0 2 * * * papermill /path/to/pipeline.ipynb /path/to/outputs/pipeline_$(date +\%Y-\%m-\%d).ipynb -p date $(date +\%Y-\%m-\%d)
```

## Parametros Soportados

| Tipo | Ejemplo | Conversion |
|------|---------|------------|
| Strings | `-p name "value"` | str |
| Numeros | `-p alpha 0.5` | float/int |
| Booleanos | `-p verbose true` | bool |
| YAML file | `-f params.yaml` | dict |

## Errores Comunes

- **No etiquetar celda como `parameters`** → Papermill inserta celda al inicio, comportamiento inesperado
- **Parametros con nombres incorrectos** → Verificar nombres exactos en la celda tagged
- **Sin manejo de excepciones** → La ejecucion puede fallar silenciosamente
- **Rutas hardcodeadas** → Usar parametros para rutas, no valores absolutos

## Banderas Rojas - DETENER

- Ejecutar notebook sin celda tagged `parameters`
- Usar `papermill` sin try/except para capturar errores
- Pasar parametros con nombres que no existen en el notebook
- No documentar parametros requeridos en el cuaderno

## Integracion con Storage

```python
import papermill as pm
import os

def execute_with_storage(notebook, output, params):
    # Montar Google Drive si esta en Colab
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        base_dir = '/content/drive/MyDrive'
    except ImportError:
        base_dir = os.getcwd()

    # Resolver rutas relativas
    input_path = os.path.join(base_dir, notebook) if not os.path.isabs(notebook) else notebook
    output_path = os.path.join(base_dir, output) if not os.path.isabs(output) else output

    pm.execute_notebook(input_path, output_path, parameters=params)
```
