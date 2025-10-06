# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import StringIO

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Dashboard Ética e Inteligencia Artificial",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dashboard: Percepciones sobre el uso de la IA en Psicología")
st.markdown("Visualiza las respuestas de estudiantes sobre los aprendizajes y los usos poco éticos de la Inteligencia Artificial.")

# ---------------- CARGA DE DATOS ----------------
st.sidebar.header("📂 Cargar base de datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV o XLSX", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Leer CSV o Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip()
    columnas = list(df.columns)
    
    # Mostrar resumen general
    st.sidebar.markdown(f"**Registros cargados:** {df.shape[0]}")
    st.sidebar.markdown(f"**Columnas detectadas:** {', '.join(columnas)}")

    # ---------------- SELECCIÓN DE ESTUDIANTE ----------------
    st.sidebar.header("🎓 Selecciona un estudiante")
    estudiante = st.sidebar.selectbox("Estudiante:", df[columnas[2]].unique())

    datos = df[df[columnas[2]] == estudiante].iloc[0]

    # ---------------- SECCIÓN PRINCIPAL ----------------
    st.header(f"🧩 Resultados de {estudiante}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💭 Lo que le ha dejado la materia")
        st.write(datos[columnas[3]])

    with col2:
        st.subheader("⚠️ Uso poco ético observado")
        st.write(datos[columnas[4]])

    # ---------------- NUBE DE PALABRAS ----------------
    st.header("💬 Nube de palabras del estudiante")
    texto_total = str(datos[columnas[3]]) + " " + str(datos[columnas[4]])
    wc = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(texto_total)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # ---------------- ANÁLISIS GENERAL ----------------
    st.header("📊 Frecuencia de términos comunes (todos los estudiantes)")

    texto_global = " ".join(df[columnas[3]].astype(str)) + " " + " ".join(df[columnas[4]].astype(str))
    palabras_clave = ["ética", "IA", "ChatGPT", "copiar", "pegar", "leer", "investigación", "plagio", "crítico", "revisar", "verificar"]
    conteos = {pal: texto_global.lower().count(pal.lower()) for pal in palabras_clave}

    fig2, ax2 = plt.subplots()
    ax2.barh(list(conteos.keys()), list(conteos.values()), color="#29a632")
    ax2.set_xlabel("Frecuencia")
    ax2.set_ylabel("Palabras clave")
    st.pyplot(fig2)

    # ---------------- TABLA COMPLETA ----------------
    with st.expander("📋 Ver base de datos completa"):
        st.dataframe(df, use_container_width=True)

    # ---------------- PIE DE PÁGINA ----------------
    st.markdown("---")
    st.markdown("👩‍💻 **Autor:** Módulo Ética e IA | **Desarrollado con Streamlit** | © 2025")
else:
    st.info("📤 Sube un archivo CSV o XLSX con tus respuestas para comenzar.")
