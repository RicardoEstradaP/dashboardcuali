# app.py
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Análisis de entrevista - Trabajo Social", layout="wide")
st.title("🗣️ Dashboard de hallazgos - Entrevista sobre elección de carrera")

# ---------- DATOS ----------
st.sidebar.header("📁 Datos de la entrevista")
st.sidebar.markdown("**Archivo:** Ejemplo transcripción de entrevista")
st.sidebar.markdown("**Duración:** 16 min 51 s")
st.sidebar.markdown("**Entrevistadora:** JC")
st.sidebar.markdown("**Entrevistados:** Mariel (19 años) y Brian (20 años)")

# ---------- CATEGORÍAS ----------
st.header("📂 Categorías principales")
categorias = pd.DataFrame({
    "Categoría": [
        "Motivación inicial",
        "Cambio de percepción",
        "Relevancia del TS",
        "Proyección profesional",
        "Factores personales"
    ],
    "Descripción": [
        "Razones iniciales de elección de carrera, vocación o planes alternos",
        "Transformación en la visión de la carrera con el paso del tiempo",
        "Valor social y función del trabajador/a social en la comunidad",
        "Intereses y áreas donde desean especializarse o contribuir",
        "Elementos biográficos, familiares o de valores prosociales"
    ]
})
st.dataframe(categorias, use_container_width=True)

# ---------- GRÁFICO ----------
st.header("📊 Distribución de menciones por categoría")
data = {
    "Motivación inicial": 5,
    "Cambio de percepción": 4,
    "Relevancia del TS": 3,
    "Proyección profesional": 3,
    "Factores personales": 2
}
fig, ax = plt.subplots()
ax.bar(data.keys(), data.values())
plt.xticks(rotation=30, ha="right")
st.pyplot(fig)

# ---------- NUBE DE PALABRAS ----------
st.header("💬 Palabras más frecuentes")
texto = """
motivación carrera social comunidad ayudar personas trabajo salud sociedad
campo maestra maíz medio ambiente interés aportar empoderamiento niños niñas
"""
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(texto)
fig_wc, ax_wc = plt.subplots()
ax_wc.imshow(wordcloud, interpolation="bilinear")
ax_wc.axis("off")
st.pyplot(fig_wc)

# ---------- EXTRACTOS DESTACADOS ----------
st.header("🧾 Extractos destacados por categoría")
with st.expander("Motivación inicial"):
    st.write("“Mi primera opción era diseño gráfico y comunicación visual…”")
    st.write("“Dejar mi granito de arena para mejorar la situación…”")

with st.expander("Cambio de percepción"):
    st.write("“La maestra habla mucho del maíz y del trabajo en comunidades…”")

with st.expander("Relevancia del TS"):
    st.write("“Nosotros somos guías y encaminamos a la población a empoderarse…”")

with st.expander("Proyección profesional"):
    st.write("“Me gustaría especializarme en trabajo con niñas y niños…”")

with st.expander("Factores personales"):
    st.write("“Esto de los animalitos se lo aprendí a mi papá…”")

# ---------- PIE ----------
st.markdown("---")
st.markdown("👩‍💻 **Autor:** JC  |  🕒 Duración: 16:51  |  📘 Fuente: Entrevista 1")
