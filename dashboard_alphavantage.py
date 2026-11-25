# Tablero de Alpha Vantage (AAPL semanal) en Streamlit
# Herramientas de Visualización · IDIA223 · Tercer Parcial
# EP.03.01 — Evidencia de Producto · Jairo Pacindo Piña
# Estudiante: Marco Alexander Banda Pérez (125054766)
# Base: BOWadapter/HerramientasVisualizacion (repositorio del docente).
# API: la de la evaluación EC.02.02 ("Tu API"): Alpha Vantage,
# TIME_SERIES_WEEKLY, símbolo AAPL. NO es la API de Banxico.
#
#     pip install -r requirements.txt
#     streamlit run dashboard_alphavantage.py
#
# LA LLAVE NO VA EN ESTE ARCHIVO.
# En tu equipo: crea la carpeta .streamlit y dentro un archivo secrets.toml
# con una sola línea:
#     alphavantage_key = "pega-aqui-tu-llave"
# Al publicar en Streamlit Community Cloud: pega esa misma línea en la
# sección de secretos de la app. El archivo secrets.toml nunca se sube
# al repositorio. Sin llave, el tablero corre con los datos de ejemplo
# de aapl_semanal_ejemplo.csv (precios semanales reales de AAPL
# 2021-2025) y lo dice con un aviso.
#
# Límites del plan gratuito de Alpha Vantage: 25 peticiones por día,
# máximo 5 por minuto. Por eso la respuesta se guarda en respuesta.json
# y se reutiliza.

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

# ─── Paleta del curso ──────────────────────────────────────────────────
GRIS = "#B9C3D1"
AZUL = "#1C4C9A"
ROJO = "#B2182B"
CUALI = ["#E69F00", "#56B4E9", "#009E73", "#0072B2"]
sns.set_theme(style="whitegrid")

BASE_DIR = Path(__file__).parent
API_URL = "https://www.alphavantage.co/query"
MUESTRA_CSV = BASE_DIR / "aapl_semanal_ejemplo.csv"
RESPUESTA_JSON = BASE_DIR / "respuesta.json"

st.set_page_config(page_title="Tablero Alpha Vantage · AAPL", layout="wide")


# ─── La llave ──────────────────────────────────────────────────────────
def leer_llave():
    try:
        if "alphavantage_key" in st.secrets:
            return str(st.secrets["alphavantage_key"]).strip()
    except Exception:
        pass  # todavía no existe el archivo de secretos
    if os.environ.get("ALPHAVANTAGE_API_KEY"):
        return os.environ["ALPHAVANTAGE_API_KEY"].strip()
    return None


LLAVE = leer_llave()


# ─── La consulta ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def consultar(symbol="AAPL", llave=None):
    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": symbol,
        "apikey": llave,
    }
    respuesta = requests.get(API_URL, params=params, timeout=60)

    if respuesta.status_code == 401:
        raise PermissionError("La llave no fue aceptada (401).")
    if respuesta.status_code == 400:
        raise ValueError("Petición mal hecha (400). Revisa los parámetros.")
    if respuesta.status_code == 429:
        raise PermissionError("Límite de peticiones excedido (429). Espera un momento.")
    respuesta.raise_for_status()

    # Un 200 no garantiza JSON: el servidor puede contestar otra cosa.
    tipo = respuesta.headers.get("Content-Type") or ""
    if "json" not in tipo:
        raise ValueError(f"El servidor no devolvió JSON sino {tipo}.")

    datos_json = respuesta.json()
    if "Note" in datos_json:
        raise PermissionError("Límite de peticiones de Alpha Vantage: " + str(datos_json["Note"]))
    if "Error Message" in datos_json:
        raise ValueError("Alpha Vantage devolvió un error: " + str(datos_json["Error Message"]))
    if "Weekly Time Series" not in datos_json:
        raise ValueError("La respuesta no trae 'Weekly Time Series'.")

    # Guardar la respuesta y reutilizarla, como pide la práctica.
    try:
        with open(RESPUESTA_JSON, "w", encoding="utf-8") as f:
            json.dump(datos_json, f)
    except OSError:
        pass

    series = datos_json["Weekly Time Series"]
    filas = []
    for fecha, v in series.items():
        filas.append(
            {
                "fecha": fecha,
                "apertura": float(v["1. open"]),
                "maximo": float(v["2. high"]),
                "minimo": float(v["3. low"]),
                "cierre": float(v["4. close"]),
                "volumen": float(v["5. volume"]),
            }
        )
    df = pd.DataFrame(filas)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def cargar_muestra():
    df = pd.read_csv(MUESTRA_CSV, parse_dates=["fecha"])
    return df


def preparar(df):
    df = df.sort_values("fecha").reset_index(drop=True)
    df["rango_semanal"] = df["maximo"] - df["minimo"]
    df["anio"] = df["fecha"].dt.year
    return df


# ─── Datos: en vivo con llave, o de ejemplo sin llave ──────────────────
usando_muestra = False
if LLAVE:
    if len(LLAVE) != 16:
        st.error(
            f"La llave tiene {len(LLAVE)} caracteres y debería tener 16. "
            "Revisa que esté completa y sin comillas."
        )
        st.stop()
    try:
        datos = preparar(consultar(llave=LLAVE))
        origen = "Alpha Vantage en vivo (TIME_SERIES_WEEKLY, AAPL)"
    except Exception as e:
        st.warning(f"No se pudo consultar Alpha Vantage ({e}). Se muestran datos de ejemplo.")
        datos = preparar(cargar_muestra())
        usando_muestra = True
        origen = "Datos de ejemplo (aapl_semanal_ejemplo.csv)"
else:
    st.warning(
        "Sin llave de Alpha Vantage: se muestran datos de ejemplo. "
        "Consigue tu llave gratis en https://www.alphavantage.co/support/#api-key "
        "y ponla en `.streamlit/secrets.toml` como `alphavantage_key`."
    )
    datos = preparar(cargar_muestra())
    usando_muestra = True
    origen = "Datos de ejemplo (aapl_semanal_ejemplo.csv)"

# ─── Filtros ───────────────────────────────────────────────────────────
st.title("Apple (AAPL): precios semanales · Alpha Vantage")
st.caption(f"Fuente: {origen} · EP.03.01 · IDIA223 Herramientas de Visualización")
if usando_muestra:
    st.info("Estás viendo datos de ejemplo etiquetados, no la consulta en vivo.")

anios = sorted(datos["anio"].unique().tolist())
sel_anios = st.sidebar.multiselect("Años", anios, default=anios)
if not sel_anios:
    st.warning("Elige al menos un año en el menú de la izquierda.")
    st.stop()
df = datos[datos["anio"].isin(sel_anios)].copy()

ultimo = df.iloc[-1]
anterior = df.iloc[-2] if len(df) > 1 else None
variacion = (
    (ultimo["cierre"] / anterior["cierre"] - 1) * 100 if anterior is not None else 0.0
)

col1, col2, col3 = st.columns(3)
col1.metric("Último cierre (USD)", f"${ultimo['cierre']:.2f}")
col2.metric("Variación última semana", f"{variacion:+.2f}%")
col3.metric("Volumen semanal promedio", f"{df['volumen'].mean():,.0f} acciones")


# ─── Gráfica 1 · Evolución ─────────────────────────────────────────────
st.subheader("El cierre semanal de Apple subió de forma sostenida entre 2021 y 2025")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df["fecha"], df["cierre"], color=AZUL, linewidth=1.5)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Cierre (USD)")
ax1.grid(True, color=GRIS, alpha=0.5)
st.pyplot(fig1)
st.caption(
    "Pregunta: ¿cómo cambió el precio de cierre semanal de Apple y su tendencia "
    "entre 2021 y 2025? Lectura: el cierre pasó de unos $130 a principios de 2021 "
    "a más de $270 a finales de 2025, con caídas marcadas en 2022."
)

# ─── Gráfica 2 · Distribución ──────────────────────────────────────────
st.subheader("La mayoría de las semanas Apple se movió menos de $10")
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.hist(df["rango_semanal"], bins=25, color=AZUL, edgecolor="white")
ax2.set_xlabel("Rango semanal, máximo − mínimo (USD)")
ax2.set_ylabel("Semanas")
ax2.grid(True, color=GRIS, alpha=0.5)
st.pyplot(fig2)
st.caption(
    "Pregunta: ¿cómo se reparten las variaciones semanales de precio? "
    "Lectura: el rango semanal típico se concentra entre $4 y $10; "
    "las semanas con rangos de más de $15 son pocas y coinciden con "
    "movimientos fuertes del mercado."
)

# ─── Gráfica 3 · Relación ──────────────────────────────────────────────
st.subheader("Las semanas de mayor movimiento también son las de mayor volumen")
fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.scatter(df["volumen"], df["rango_semanal"], color=CUALI[1], s=18, alpha=0.7)
ax3.set_xlabel("Volumen (acciones)")
ax3.set_ylabel("Rango semanal (USD)")
ax3.grid(True, color=GRIS, alpha=0.5)
st.pyplot(fig3)
st.caption(
    "Pregunta: ¿hay relación entre la amplitud de la variación semanal en "
    "dólares y el volumen operado? Lectura: a mayor volumen, el rango "
    "semanal tiende a ser mayor; las semanas tranquilas operan poco volumen."
)

# ─── Gráfica 4 · Comparación ───────────────────────────────────────────
st.subheader("El volumen semanal promedio fue mayor en 2021 y 2022 que en 2023-2025")
comp = df[df["anio"].between(2022, 2025)].groupby("anio")["volumen"].mean()
fig4, ax4 = plt.subplots(figsize=(10, 4))
ax4.bar(comp.index.astype(str), comp.values, color=CUALI)
ax4.set_xlabel("Año")
ax4.set_ylabel("Volumen semanal promedio (acciones)")
ax4.grid(True, color=GRIS, alpha=0.5, axis="y")
st.pyplot(fig4)
st.caption(
    "Pregunta: ¿en qué año entre 2022 y 2025 se registró el mayor y menor "
    "volumen semanal promedio? Lectura: el mayor fue 2022 y el menor 2025."
)

st.caption(
    "Tablero EP.03.01 · API: Alpha Vantage, TIME_SERIES_WEEKLY, AAPL · "
    "Repositorio: https://github.com/alexanderbandapm01-ops/HerramientasVisualizacionAlex"
)
