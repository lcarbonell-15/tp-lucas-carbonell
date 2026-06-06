---
name: notebook-git-versioner
description: Usa cuando inicializas un repositorio de ciencia de datos, cuando ocurren conflictos de fusion en cuadernos Jupyter, o cuando necesitas configurar gates de calidad pre-commit para codigo analitico.
compatibility: Entorno Git local, Python 3.10+, gestor de paquetes uv
metadata:
  author: dataops-standard-initiative
  version: "2.1.0"
---

# Notebook Git Versioner

## Descripcion General

Configura filtros Git (nbstripout, nb-clean) y pre-commit hooks con Jupytext para control de versiones limpio de cuadernos Jupyter libres de metadatos y salidas binarias.

## Cuando Usar

- Inicializar un nuevo repositorio de ciencia de datos
- Conflictos de fusion en cuadernos Jupyter reportados
- Estructurar gates de calidad pre-commit para codigo analitico
- Configurar tuberias CI/CD para proyectos de cuadernos

## Patron Principal

### 1. Instalar nbstripout con uv

```bash
uv pip install nbstripout
nbstripout --install
```

Configurar claves extendidas para eliminacion profunda de metadatos:

```bash
git config filter.nbstripout.extrakeys "metadata.kernelspec metadata.language_info.version metadata.celltoolbar cell.metadata.heading_collapsed cell.metadata.hidden"
```

### 2. Alternativa: nb-clean para CI/CD

```bash
uvx nb-clean check --remove-empty-cells --remove-all-notebook-metadata notebook.ipynb
uvx nb-clean clean --remove-empty-cells notebook.ipynb
```

Configurar en `.gitattributes`:

```text
*.ipynb filter=nbclean-filter
```

En `.git/config`:

```ini
[filter "nbclean-filter"]
clean = "nb-clean clean"
smudge = "cat"
```

### 3. Sincronizacion Bidireccional con Jupytext

Crear `jupytext.toml` en la raiz del proyecto:

```toml
formats = "ipynb,py:percent"
```

**IMPORTANTE:** La sincronizacion `--sync` es OBLIGATORIA en los hooks pre-commit. No es opcional.

Sincronizar cuaderno con script paired:

```bash
jupytext --sync notebook.ipynb
```

### 4. Configuracion de Pre-commit

Crear `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: 0.6.1
    hooks:
      - id: nbstripout
        name: Saneamiento de Salidas Jupyter (nbstripout)

  - repo: https://github.com/mwouts/jupytext
    rev: v1.16.2
    hooks:
      - id: jupytext
        name: Sincronizacion de Formatos (Jupytext)
        args: [--sync]
```

**Nota:** Usar `kynan/nbstripout` (no `kynta`).

Instalar hooks:

```bash
pre-commit install
```

## Referencia Rapida

| Comando | Proposito |
|---------|-----------|
| `nbstripout --install` | Instalar filtro Git |
| `uvx nb-clean check` | Detectar cuadernos sucios (CI/CD) |
| `jupytext --sync` | Sincronizar cuaderno con script paired |
| `pre-commit install` | Instalar hooks pre-commit |

## Gestion de Dependencias para Proyectos de Ciencia de Datos

Para proyectos de analisis cuantitativo, incluye un archivo `requirements.txt` o `pyproject.toml` en la raiz del repositorio:

```txt
# requirements.txt para analisis cuantitativo
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
sympy>=1.12
numpy_financial>=1.8.0
yfinance>=0.2.0
pulp>=2.7.0
```

## Estructura Recomendada para Proyectos de Analisis

```
proyecto/
├── .gitignore
├── .pre-commit-config.yaml
├── jupytext.toml
├── requirements.txt
├── README.md
├── datos/
│   └── .gitkeep
├── imagenes/
│   └── .gitkeep
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_analisis.ipynb
│   └── 03_modelos.ipynb
└── src/
    ├── __init__.py
    └── funciones.py
```

## Errores Comunes

- **Usar solo `.gitignore`** → No elimina salidas, solo ignora archivos
- **Falta configuracion `extrakeys`** → Algunos metadatos permanecen (celltoolbar, heading_collapsed)
- **Sin hooks pre-commit** → Olvidar ejecutar el filtro manualmente antes del commit
- **No sincronizar con Jupytext** → Los archivos paired se desincronizan
- **No incluir requirements.txt** → Dependencias no documentadas
- **Tratar Jupytext --sync como opcional** → Los archivos paired se desincronizan en equipo

## Banderas Rojas - DETENER

- Sugerir solo `.gitignore` para control de versiones de cuadernos
- No mencionar nbstripout/nb-clean al configurar repos de cuadernos
- Sin configuracion pre-commit para proyectos de cuadernos
- Jupytext sin `--sync` en hooks pre-commit
- Repositorio de ciencia de datos sin archivo de dependencias
- Decir que Jupytext --sync es "opcional" o "por preferencia" → **DEBE ser obligatorio en pre-commit hooks**
