# AGENTS.md

## Tipo de Proyecto

Proyecto académico de ciencia de datos (Trabajo Práctico Final - Métodos Cuantitativos Aplicados a la Gestión). Contenido principalmente en español.

## Stack

- Python 3.x con pandas, numpy, matplotlib, seaborn, scikit-learn
- Sin infraestructura de build/test/lint

## Documentación Clave

- `README.md` define el pipeline obligatorio: Carga e Inspección → Limpieza de Nulos/Duplicados → Transformación/Merge → EDA
- La carpeta `.opencode/skills/` contiene archivos SKILL.md para limpieza de datos, transformación, visualización, regresión y flujos de notebooks

## Convenciones de Trabajo

- El pipeline sigue la metodología del README (Left Join para merges, máximo 2 tablas, reindexar después de eliminaciones)
- Nomenclatura de columnas en español descriptivo
- Visualizaciones con paletas de colores armónicas (sin efectos arcoíris)
- LinearRegression de sklearn para modelado predictivo, evaluado con R²

## Skills Disponibles

La carpeta `.opencode/skills/` contiene archivos SKILL.md para las siguientes tareas:

| Skill | Descripción |
|-------|-------------|
| `colab-notebook-optimizer` | Optimización de notebooks para Google Colab |
| `data-cleaning-automation` | Automatización de limpieza de datos |
| `data-profiling-automation` | Automatización de perfilado de datos |
| `data-transformation-pipeline` | Pipeline de transformación de datos |
| `data-visualization-best-practices` | Mejores prácticas de visualización |
| `notebook-dashboarding` | Creación de dashboards en notebooks |
| `notebook-git-versioner` | Versionado de notebooks con Git |
| `notebook-parameterization` | Parametrización de notebooks |
| `regression-modeling` | Modelado de regresión lineal |
