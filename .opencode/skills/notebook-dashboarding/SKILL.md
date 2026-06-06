---
name: notebook-dashboarding
description: Usa cuando necesitas convertir cuadernos Jupyter en aplicaciones web interactivas para usuarios no tecnicos, o cuando quieres crear dashboardsstandalone con widgets como sliders y dropdowns.
compatibility: Python 3.10+, voila>=0.5, ipywidgets>=8.0
metadata:
  author: dataops-standard-initiative
  version: "1.0.0"
---

# Notebook Dashboarding

## Descripcion General

Convierte cuadernos Jupyter en aplicaciones web standalone usando Voila, preservando la estructura del cuaderno mientras agrega interactividad via ipywidgets. Ideal para crear dashboards para usuarios no tecnicos.

## Cuando Usar

- Crear dashboards interactivos para stakeholders no tecnicos
- Desplegar modelos ML como aplicaciones web sin refactorizar codigo
- Crear herramientas de simulacion con parametros ajustables
- Compartir analisis interactivo sin exponer codigo Python
- Prototipar rapidamente interfaces de aplicaciones de datos

## Patron Principal

### 1. Instalacion

```bash
pip install voila
```

### 2. Crear Notebook con Widgets Interactivos

```python
import ipywidgets as widgets
from IPython.display import display

# Widgets basicos
slider = widgets.IntSlider(
    value=50,
    min=0,
    max=100,
    step=1,
    description='Umbral:',
    style={'description_width': 'initial'}
)

dropdown = widgets.Dropdown(
    options=['Opcion A', 'Opcion B', 'Opcion C'],
    value='Opcion A',
    description='Seleccion:'
)

button = widgets.Button(
    description='Ejecutar',
    button_style='success',
    icon='check'
)

output = widgets.Output()

def on_button_click(b):
    with output:
        output.clear_output()
        print(f"Umbral: {slider.value}, Seleccion: {dropdown.value}")

button.on_click(on_button_click)

# Mostrar widgets
display(slider, dropdown, button, output)
```

### 3. Ejecutar como Aplicacion Web

```bash
# Ejecutar Voila con un notebook especifico
voila mi_notebook.ipynb --port 5000

# Ejecutar todos los notebooks en un directorio
voila /ruta/a/dashboard/

# Con especificacion de plantilla (gridstack para layout)
voila mi_notebook.ipynb --template gridstack
```

### 4. Configuracion de Seguridad

```bash
# Por defecto, Voila usa strip_sources=True (oculta codigo)
# Para mostrar el codigo fuente:
voila mi_notebook.ipynb --strip_sources=False

# Configuracion en jupyter_config.json
cat > jupyter_config.json << 'EOF'
{
  "VoilaConfiguration": {
    "strip_sources": true,
    "enable_nbextensions": true
  }
}
EOF
```

### 5. Despliegue en JupyterHub

```python
# En jupyterhub_config.py
c.VoilaExecutor.enable_nbextensions = True
c.VoilaConfiguration.template = "gridstack"
```

## Widgets Comunes para Dashboards

| Widget | Uso | Ejemplo |
|--------|-----|---------|
| `IntSlider` / `FloatSlider` | Parametros numericos continuos | `widgets.IntSlider(min=0, max=100)` |
| `Dropdown` | Seleccion de opciones | `widgets.Dropdown(options=['A','B'])` |
| `SelectMultiple` | Seleccion multiple | `widgets.SelectMultiple(options=['A','B','C'])` |
| `DatePicker` | Seleccion de fechas | `widgets.DatePicker()` |
| `ColorPicker` | Seleccion de colores | `widgets.ColorPicker()` |
| `FileUpload` | Carga de archivos | `widgets.FileUpload()` |
| `Button` | Acciones | `widgets.Button(description='Ejecutar')` |

## Librerias de Visualizacion Compatibles

| Libreria | Tipo | Instalacion |
|----------|------|-------------|
| `bqplot` | Graficos interactivos | `pip install bqplot` |
| `ipyleaflet` | Mapas | `pip install ipyleaflet` |
| `ipyvolume` | Visualizacion 3D | `pip install ipyvolume` |
| `plotly` | Graficos advanced | `pip install plotly` |
| `matplotlib` | Graficos basicos | `pip install matplotlib` |

## Errores Comunes

- **No instalar voila como servidor extension** → No funciona como /voila endpoint
- **Widgets fuera de orden en display()** → Layout incorrecto en el dashboard
- **Sin manejo de callbacks** → Los widgets no responden a interacciones
- **No probar localmente antes de desplegar** → Errores en produccion

## Banderas Rojas - DETENER

- Crear aplicaciones web custom cuando Voila puede convertir el notebook directamente
- No usar `strip_sources=True` si no quieres exponer el codigo fuente
- Desplegar sin probar localmente con `voila mi_notebook.ipynb`
- No documentar los widgets y sus rangos de valores para usuarios no tecnicos

## Integracion con Voila Gallery

Para compartir dashboards publicos, contribuye a [Voila Gallery](https://voila-gallery.org):
1. Publica tu notebook en GitHub
2. Agregalo a la galeria via PR en `voila-gallery/gallery`
