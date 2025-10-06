# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Dashboard Ética e Inteligencia Artificial",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dashboard de Análisis Categórico: Ética y uso de la IA en Psicología")
st.markdown("Analiza los aprendizajes y percepciones de tus estudiantes, organizados por categorías temáticas.")

# ---------------- CARGA DE DATOS ----------------
st.sidebar.header("📂 Cargar base de datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV o XLSX", type=["csv", "xlsx"])

# ---------------- DEFINICIÓN DE CATEGORÍAS ----------------
categorias = {
    "Aprendizaje técnico": ["herramientas", "tecnologías", "tipos de ia", "funcionamiento", "uso correcto"],
    "Aplicación profesional": ["investigación", "proyecto", "trabajo académico", "psicología", "campo laboral"],
    "Conciencia ética": ["ético", "ética", "responsable", "honesto", "crítico"],
    "Uso irresponsable": ["copiar", "pegar", "plagio", "hacer tarea", "sin revisar"],
    "Pensamiento crítico": ["reflexión", "verificar", "revisar", "citar", "fuentes", "analizar"],
    "Aprovechamiento positivo": ["aprovechar", "beneficio", "herramienta", "facilitar", "eficiente"],
    "Dependencia excesiva": ["abuso", "dependencia", "cerebro deja", "usar sin pensar", "automatizado"]
}

def categorizar_texto(texto):
    texto = texto.lower()
    asignadas = []
    for cat, palabras in categorias.items():
        if any(p in texto for p in palabras):
            asignadas.append(cat)
    if not asignadas:
        asignadas.append("Sin categoría")
    return asignadas

# ---------------- PROCESAMIENTO ----------------
if uploaded_file is not None:
    # Leer CSV o Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()
    columnas = df.columns.tolist()

    if len(columnas) < 5:
        st.error("⚠️ Tu archivo debe tener al menos 5 columnas: Hora de inicio, Marca temporal, Estudiante, Pregunta 1 y Pregunta 2.")
        st.stop()

    # Calcular tiempo de respuesta
    df["Hora de inicio"] = pd.to_datetime(df[columnas[0]], errors="coerce")
    df["Marca temporal"] = pd.to_datetime(df[columnas[1]], errors="coerce")
    df["Tiempo de respuesta (min)"] = (df["Marca temporal"] - df["Hora de inicio"]).dt.total_seconds() / 60

    # Categorización
    df["Categorías_P1"] = df[columnas[3]].apply(categorizar_texto)
    df["Categorías_P2"] = df[columnas[4]].apply(categorizar_texto)

    st.sidebar.markdown(f"**Total de respuestas:** {df.shape[0]}")
    st.sidebar.markdown(f"**Duración promedio:** {df['Tiempo de respuesta (min)'].mean():.2f} min")

    # ---------------- SELECCIÓN DE ESTUDIANTE ----------------
    st.sidebar.header("🎓 Selecciona un estudiante")
    estudiante = st.sidebar.selectbox("Estudiante:", df[columnas[2]].unique())

    datos = df[df[columnas[2]] == estudiante].iloc[0]

    # ---------------- PANEL INDIVIDUAL ----------------
    st.header(f"🧩 Respuestas de {estudiante}")

    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.metric("⏱️ Tiempo de respuesta (min)", f"{datos['Tiempo de respuesta (min)']:.2f}")
    with col2:
        st.subheader("💭 Aprendizajes de la materia")
        st.write(datos[columnas[3]])
        st.markdown(f"**Categorías detectadas:** {', '.join(datos['Categorías_P1'])}")
    with col3:
        st.subheader("⚠️ Uso poco ético observado")
        st.write(datos[columnas[4]])
        st.markdown(f"**Categorías detectadas:** {', '.join(datos['Categorías_P2'])}")

    # ---------------- FRECUENCIA DE CATEGORÍAS ----------------
    st.header("📊 Frecuencia de categorías por pregunta")

    # Contar frecuencia global
    freq_p1 = pd.Series([c for sublist in df["Categorías_P1"] for c in sublist]).value_counts()
    freq_p2 = pd.Series([c for sublist in df["Categorías_P2"] for c in sublist]).value_counts()

    colG1, colG2 = st.columns(2)
    with colG1:
        st.subheader("🧠 Aprendizajes (Pregunta 1)")
        fig1, ax1 = plt.subplots()
        ax1.barh(freq_p1.index, freq_p1.values, color="#2563eb")
        ax1.set_xlabel("Frecuencia")
        ax1.set_ylabel("Categoría")
        st.pyplot(fig1)

    with colG2:
        st.subheader("🚫 Usos poco éticos (Pregunta 2)")
        fig2, ax2 = plt.subplots()
        ax2.barh(freq_p2.index, freq_p2.values, color="#dc2626")
        ax2.set_xlabel("Frecuencia")
        ax2.set_ylabel("Categoría")
        st.pyplot(fig2)

    # ---------------- NUBES DE PALABRAS ----------------
    st.header("💬 Nubes de palabras por pregunta (general)")
    colN1, colN2 = st.columns(2)
    with colN1:
        wc1 = WordCloud(width=800, height=400, background_color="white").generate(" ".join(df[columnas[3]].astype(str)))
        figN1, axN1 = plt.subplots()
        axN1.imshow(wc1, interpolation="bilinear")
        axN1.axis("off")
        st.pyplot(figN1)
    with colN2:
        wc2 = WordCloud(width=800, height=400, background_color="white", colormap="Reds").generate(" ".join(df[columnas[4]].astype(str)))
        figN2, axN2 = plt.subplots()
        axN2.imshow(wc2, interpolation="bilinear")
        axN2.axis("off")
        st.pyplot(figN2)

    # ---------------- DESCARGA ----------------
    with st.expander("📋 Ver base de datos con categorías"):
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Descargar base enriquecida con categorías",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="respuestas_categorizadas.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.caption("Dashboard desarrollado con Streamlit • Análisis categórico de percepciones sobre la IA • © 2025")

else:
    st.info("📤 Sube un archivo CSV o XLSX con tus respuestas para comenzar.")
