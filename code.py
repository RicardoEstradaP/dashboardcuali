# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import re
from wordcloud import WordCloud, STOPWORDS

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Dashboard Ética e Inteligencia Artificial",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dashboard de Análisis Categórico: Ética y uso de la IA en Psicología")
st.markdown("Visualiza respuestas categorizadas y sus extractos temáticos de forma interactiva.")

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
    estudiantes = ["Todos los estudiantes"] + list(df[columnas[2]].unique())
    estudiante = st.sidebar.selectbox("Estudiante:", estudiantes)

    # Filtrado
    if estudiante == "Todos los estudiantes":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df[columnas[2]] == estudiante]

    # ---------------- PANEL INDIVIDUAL ----------------
    if estudiante != "Todos los estudiantes":
        datos = df_filtrado.iloc[0]
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
    else:
        st.header("📊 Resultados globales de todos los estudiantes")

    # ---------------- EXTRACTOS POR CATEGORÍA ----------------
    st.header("🧠 Extractos por categoría")

    # Reunir extractos categorizados
    resultados = {}
    for cat in categorias.keys():
        textos = []
        for _, row in df_filtrado.iterrows():
            # Combinar respuestas de ambas preguntas
            for col, campo in zip(["Categorías_P1", "Categorías_P2"], [columnas[3], columnas[4]]):
                if cat in row[col]:
                    texto = row[campo].strip()
                    textos.append(f"**{row[columnas[2]]}:** {texto}")
        if textos:
            resultados[cat] = textos

    if not resultados:
        st.warning("No se detectaron categorías en las respuestas filtradas.")
    else:
        for cat, ejemplos in resultados.items():
            with st.expander(f"📂 {cat}  ({len(ejemplos)} coincidencias)"):
                for t in ejemplos:
                    st.markdown(f"- {t}")

    # ---------------- NUBE DE PALABRAS ----------------
    st.header("💬 Nubes de palabras por pregunta (limpias en español)")

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

    texto_p1 = " ".join(df_filtrado[columnas[3]].astype(str).map(limpiar_texto))
    texto_p2 = " ".join(df_filtrado[columnas[4]].astype(str).map(limpiar_texto))

    colN1, colN2 = st.columns(2)
    with colN1:
        st.subheader("🧠 Aprendizajes")
        wc1 = WordCloud(width=800, height=400, background_color="white",
                        stopwords=stopwords_es, colormap="Blues").generate(texto_p1)
        st.image(wc1.to_array(), use_container_width=True)

    with colN2:
        st.subheader("🚫 Usos poco éticos")
        wc2 = WordCloud(width=800, height=400, background_color="white",
                        stopwords=stopwords_es, colormap="Reds").generate(texto_p2)
        st.image(wc2.to_array(), use_container_width=True)

    # ---------------- DESCARGA ----------------
    with st.expander("📋 Ver base de datos con categorías"):
        st.dataframe(df_filtrado, use_container_width=True)
        st.download_button(
            "⬇️ Descargar base enriquecida (filtrada)",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="respuestas_filtradas.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.caption("Dashboard desarrollado con Streamlit • Extractos temáticos categorizados • © 2025")

else:
    st.info("📤 Sube un archivo CSV o XLSX con tus respuestas para comenzar.")
