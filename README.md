# ED.03.02 — Tablero del SIE de Banxico (SF43718)

**Materia:** Herramientas de Visualización — IDIA223-4
**Profesor:** Jairo Pacindo Piña
**Estudiante:** Marco Alexander Banda Pérez — Matrícula: 125054766
**Fecha de entrega:** 22 de noviembre de 2026, 23:59
**Base:** [BOWadapter/HerramientasVisualizacion](https://github.com/BOWadapter/HerramientasVisualizacion) (repositorio del docente)

## Qué pide la actividad

1. Realizar la prueba de implementación del dashboard compartido en el
   repositorio Base del docente.
2. Quitar una de las gráficas que no sean necesarias para el muestreo de
   la información.
3. Añadir una gráfica que, bajo criterio propio, pueda ser de utilidad.

## Cambios ED.03.02 (en `dashboard_banxico.py`)

### Quitada: "Promedio por mes y año" (mapa de calor)

- Repetía el nivel del tipo de cambio que ya muestra la gráfica de
  tendencia (valor diario + media móvil), pero en promedio mensual.
- Al promediar escondía la volatilidad dentro de cada mes, que es justo
  lo que muestra el boxplot por año.
- Se leía mal por color: no daba valores exactos y comparar años en
  una cuadrícula era más difícil que leer la línea de tendencia.
- No apoyaba ninguna decisión que las otras gráficas no apoyaran ya.

### Añadida: "Cambio anual (cierre de año)"

- Barras del cambio porcentual del cierre de diciembre contra el cierre
  de diciembre del año anterior, con la misma convención de color del
  tablero: rojo si el valor subió (el peso se debilitó), azul si bajó
  (el peso se fortaleció).
- Responde una pregunta que ninguna gráfica del Base respondía de forma
  directa: ¿en qué año se depreció o apreció más el peso en el periodo?
  La tendencia muestra el nivel pero no el % por año, el cambio mensual
  tiene unas 60 barras y es ruidoso, y el boxplot muestra volatilidad,
  no dirección ni magnitud anual.
- Se calcula con el cierre de cada año, no con el promedio, igual que
  el cambio mensual del tablero Base. Si el rango tiene un solo año,
  muestra un aviso en lugar de una gráfica vacía.

Las otras tres gráficas del Base se conservan sin cambios:
tendencia con media móvil, cambio de un mes a otro, y boxplot de la
variación diaria por año. También se conservan los indicadores
superiores, los controles laterales y la descarga de CSV.

## Prueba de implementación (resultados reales del SIE)

Consulta al SIE el 22 de noviembre de 2026, serie SF43718,
1 de enero de 2021 a 31 de diciembre de 2025:

- `python3 -m py_compile dashboard_banxico.py` — sintaxis correcta.
- Registros brutos: 1258, días N/E: 0, registros utilizables: 1258.
- Rango con dato: 4 de enero de 2021 a 31 de diciembre de 2025.
- Primero: 19.8457; último: 18.0012; cambio total: -9.29%.
- Mínimo: 16.3357 (8 de abril de 2024); máximo: 21.8185
  (26 de noviembre de 2021).
- Cambio anual: 2022 -4.86%, 2023 -13.11%, 2024 +22.86%,
  2025 -13.40%.
- El mapa de calor quedó eliminado del código: ya no hay `imshow`,
  `pivot_table` ni `YlGnBu` en el archivo.
- Los datos descargados están en `datos_sie_SF43718.csv` y las
  figuras del reporte en `figuras/`.

El token usado para esta consulta no se guarda en ningún archivo
del repo (ni en `secrets.toml`, ni en el CSV, ni en el reporte).

## Cómo correrlo en tu equipo

```bash
pip install -r requirements.txt
streamlit run dashboard_banxico.py
```

El token es gratis, se pide en
https://www.banxico.org.mx/SieAPIRest/service/v1/token

Crea la carpeta `.streamlit` junto a `dashboard_banxico.py` y dentro
un archivo `secrets.toml` con una sola línea:

```toml
banxico_token = "pega-aqui-tu-token"
```

Copia el ejemplo de `.streamlit/secrets.toml.example` y cambia el valor.
**El archivo `secrets.toml` nunca se sube al repositorio** (está en
`.gitignore`).

## Cómo subirlo a tu GitHub y verlo en Streamlit

1. En GitHub, haz Fork de
   `BOWadapter/HerramientasVisualizacion` a tu cuenta.
2. Sube estos archivos a tu fork (reemplazando `dashboard_banxico.py`
   y añadiendo este README y `reporte_ED0302.tex`).
3. En [Streamlit Cloud](https://share.streamlit.io/), crea una app
   nueva desde tu fork, con archivo principal `dashboard_banxico.py`.
4. En la app, en Secrets, pega la misma línea:
   `banxico_token = "tu-token"`.
5. Despliega. La página pública es la app de Streamlit, no GitHub
   Pages: GitHub solo guarda el código.

## Archivos

- `dashboard_banxico.py` — tablero modificado ED.03.02.
- `requirements.txt` — streamlit, requests, pandas, matplotlib, seaborn.
- `reporte_ED0302.tex` — reporte final en LaTeX (estructura del
  reporte ejemplo de la práctica 12), ya con valores y figuras
  reales del SIE.
- `datos_sie_SF43718.csv` — datos descargados del SIE.
- `figuras/` — las 4 gráficas del reporte en PNG.
- `.streamlit/secrets.toml.example` — ejemplo del archivo de secretos.
- `.gitignore` — excluye `secrets.toml` y archivos temporales.
