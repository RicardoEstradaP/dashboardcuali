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

st.title("🤖 Dashboard de Análisis: Ética y uso de la IA en Psicología")
st.markdown("Explora respuestas por estudiante y analiza la frecuencia de conceptos en cada pregunta.")

# ---------------- CARGA DE DATOS ----------------
st.sidebar.header("📂 Cargar base de datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV o XLSX", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Leer CSV o Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()  # limpiar espacios
    columnas = df.columns.tolist()

    # Verificación de columnas mínimas
    if len(columnas) < 5:
        st.error("⚠️ Tu archivo debe tener al menos 5 columnas: Hora de inicio, Marca temporal, Estudiante, Pregunta 1 y Pregunta 2.")
        st.stop()

    # Calcular tiempo de respuesta
    df["Hora de inicio"] = pd.to_datetime(df[columnas[0]], errors="coerce")
    df["Marca temporal"] = pd.to_datetime(df[columnas[1]], errors="coerce")
    df["Tiempo de respuesta (min)"] = (df["Marca temporal"] - df["Hora de inicio"]).dt.total_seconds() / 60

    # Mostrar resumen en sidebar
    st.sidebar.markdown(f"**Total de respuestas:** {df.shape[0]}")
    st.sidebar.markdown(f"**Duración promedio:** {df['Tiempo de respuesta (min)'].mean():.2f} min")

    # ---------------- SELECCIÓN DE ESTUDIANTE ----------------
    st.sidebar.header("🎓 Selecciona un estudiante")
    estudiante = st.sidebar.selectbox("Estudiante:", df[columnas[2]].unique())

    datos = df[df[columnas[2]] == estudiante].iloc[0]

    # ---------------- RESULTADOS INDIVIDUALES ----------------
    st.header(f"🧩 Respuestas de {estudiante}")

    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.metric("⏱️ Tiempo de respuesta (min)", f"{datos['Tiempo de respuesta (min)']:.2f}")
    with col2:
        st.subheader("💭 Aprendizajes de la materia")
        st.write(datos[columnas[3]])
    with col3:
        st.subheader("⚠️ Uso poco ético observado")
        st.write(datos[columnas[4]])

    # ---------------- NUBES DE PALABRAS ----------------
    st.header("💬 Nubes de palabras por pregunta")
    colA, colB = st.columns(2)

    with colA:
        st.subheader("🧠 Aprendizajes")
        wc1 = WordCloud(width=800, height=400, background_color="white").generate(" ".join(df[columnas[3]].astype(str)))
        fig1, ax1 = plt.subplots()
        ax1.imshow(wc1, interpolation="bilinear")
        ax1.axis("off")
        st.pyplot(fig1)

    with colB:
        st.subheader("🚫 Usos poco éticos")
        wc2 = WordCloud(width=800, height=400, background_color="white", colormap="Reds").generate(" ".join(df[columnas[4]].astype(str)))
        fig2, ax2 = plt.subplots()
        ax2.imshow(wc2, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2)

    # ---------------- ANÁLISIS DE FRECUENCIA ----------------
    st.header("📊 Frecuencia de conceptos por pregunta")

    palabras_clave = ["ética", "plagio", "ChatGPT", "copiar", "pegar", "leer", "revisar", "verificar", 
                      "investigación", "crítico", "responsable", "IA", "inteligencia artificial"]

    def contar_palabras(textos):
        texto = " ".join(textos).lower()
        return {pal: texto.count(pal.lower()) for pal in palabras_clave}

    freq_aprendizaje = contar_palabras(df[columnas[3]].astype(str))
    freq_etica = contar_palabras(df[columnas[4]].astype(str))

    colG1, colG2 = st.columns(2)

    with colG1:
        st.subheader("🧠 Conceptos frecuentes - Aprendizajes")
        fig3, ax3 = plt.subplots()
        ax3.barh(list(freq_aprendizaje.keys()), list(freq_aprendizaje.values()), color="#1d4ed8")
        ax3.set_xlabel("Frecuencia")
        ax3.set_ylabel("Concepto")
        plt.tight_layout()
        st.pyplot(fig3)

    with colG2:
        st.subheader("🚫 Conceptos frecuentes - Usos poco éticos")
        fig4, ax4 = plt.subplots()
        ax4.barh(list(freq_etica.keys()), list(freq_etica.values()), color="#dc2626")
        ax4.set_xlabel("Frecuencia")
        ax4.set_ylabel("Concepto")
        plt.tight_layout()
        st.pyplot(fig4)

    # ---------------- TABLA Y DESCARGA ----------------
    with st.expander("📋 Ver base completa"):
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Descargar base enriquecida (con tiempo de respuesta)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="respuestas_enriquecidas.csv",
            mime="text/csv"
        )

    # ---------------- PIE ----------------
    st.markdown("---")
    st.caption("Dashboard desarrollado en Streamlit • Análisis de percepciones sobre el uso ético de la IA • © 2025")
else:
    st.info("📤 Sube un archivo CSV o XLSX con tus respuestas para comenzar.")
