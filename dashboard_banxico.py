# Tablero del SIE de Banxico, con token
# Herramientas de Visualización · IDIA224 · Unidad III
#
#     pip install -r requirements.txt
#     streamlit run dashboard_banxico.py
#
# EL TOKEN NO VA EN ESTE ARCHIVO.
# En tu equipo: crea la carpeta .streamlit y dentro un archivo secrets.toml
# con una sola línea:
#     banxico_token = "pega-aqui-tu-token"
# Al publicar: pega esa misma línea en la sección de secretos de la app.
# El archivo secrets.toml nunca se sube al repositorio.

import os
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

# ─── Paleta del curso ──────────────────────────────────────────────────
GRIS = "#B9C3D1"
AZUL = "#1C4C9A"
ROJO = "#B2182B"
AZUL_POS = "#2166AC"
CUALI = ["#E69F00", "#56B4E9", "#009E73", "#0072B2"]
sns.set_theme(style="whitegrid")

SIE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

st.set_page_config(page_title="Tablero del SIE", layout="wide")


