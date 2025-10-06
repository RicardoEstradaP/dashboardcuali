# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from datetime import datetime
import re
from collections import Counter

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Dashboard Ética e Inteligencia Artificial",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dashboard de Análisis Categórico: Ética y uso de la IA en Psicología")
st.markdown("Explora aprendizajes y percepciones de los estudiantes sobre el uso ético de la inteligencia artificial.")

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

    # ---------------- SIDEBAR ----------------
    st.sidebar.markdown(f"**Total de respuestas:** {df.shape[0]}")
    st.sidebar.markdown(f"**Duración promedio:** {df['Tiempo de respuesta (min)'].mean():.2f} min")

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
    st.header("💬 Nubes de palabras por pregunta (filtradas en español)")

    # Stopwords en español personalizadas
    stopwords_es = set(STOPWORDS)
    stopwords_extra = {
        "que","de","la","el","en","y","a","los","las","del","se","por","con","una","un",
        "para","como","su","al","es","lo","más","ha","sus","o","le","ya","sin","sí",
        "esto","esa","ese","son","muy","me","mi","si","no","hay","fue","puede","ser","he","han","está"
    }
    stopwords_es.update(stopwords_extra)

    def limpiar_texto(texto):
        texto = re.sub(r"http\S+|www\S+", "", texto)
        texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", texto)
        return texto.lower()

    texto_p1 = " ".join(df[columnas[3]].astype(str).map(limpiar_texto))
    texto_p2 = " ".join(df[columnas[4]].astype(str).map(limpiar_texto))

    colN1, colN2 = st.columns(2)
    with colN1:
        st.subheader("🧠 Aprendizajes")
        wc1 = WordCloud(
            width=800, height=400, background_color="white",
            stopwords=stopwords_es, colormap="Blues"
        ).generate(texto_p1)
        figN1, axN1 = plt.subplots()
        axN1.imshow(wc1, interpolation="bilinear")
        axN1.axis("off")
        st.pyplot(figN1)

    with colN2:
        st.subheader("🚫 Usos poco éticos")
        wc2 = WordCloud(
            width=800, height=400, background_color="white",
            stopwords=stopwords_es, colormap="Reds"
        ).generate(texto_p2)
        figN2, axN2 = plt.subplots()
        axN2.imshow(wc2, interpolation="bilinear")
        axN2.axis("off")
        st.pyplot(figN2)

    # ---------------- TOP 20 PALABRAS ----------------
    st.header("📈 Palabras más frecuentes (sin stopwords)")

    def contar_palabras(texto):
        palabras = [p for p in texto.split() if p not in stopwords_es and len(p) > 2]
        return Counter(palabras)

    freq_p1_words = contar_palabras(texto_p1)
    freq_p2_words = contar_palabras(texto_p2)

    colW1, colW2 = st.columns(2)
    with colW1:
        st.subheader("🧠 Aprendizajes (Top 20)")
        top_p1 = pd.DataFrame(freq_p1_words.most_common(20), columns=["Palabra", "Frecuencia"])
        st.dataframe(top_p1, use_container_width=True)
    with colW2:
        st.subheader("🚫 Usos poco éticos (Top 20)")
        top_p2 = pd.DataFrame(freq_p2_words.most_common(20), columns=["Palabra", "Frecuencia"])
        st.dataframe(top_p2, use_container_width=True)

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
    st.caption("Dashboard desarrollado con Streamlit • Análisis categórico y léxico de percepciones sobre la IA • © 2025")

else:
    st.info("📤 Sube un archivo CSV o XLSX con tus respuestas para comenzar.")
