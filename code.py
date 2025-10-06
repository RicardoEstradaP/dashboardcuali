# app.py
import streamlit as st
import pandas as pd
import re
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Laboratorio de Análisis Cualitativo - Ética e IA",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Laboratorio de Análisis Cualitativo")
st.markdown("""
Este dashboard te permite **explorar, comparar y analizar cualitativamente** las respuestas de los estudiantes.  
Carga tu base de datos, filtra, revisa las respuestas y reflexiona sobre las **categorías temáticas** que emergen.
""")

# ---------------- CARGA DE DATOS ----------------
st.sidebar.header("📂 Cargar base de datos")
archivo = st.sidebar.file_uploader("Sube un archivo CSV o XLSX con respuestas", type=["csv", "xlsx"])

if archivo is not None:
    # Leer CSV o Excel
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)

    df.columns = df.columns.str.strip()
    columnas = df.columns.tolist()

    if len(columnas) < 5:
        st.error("⚠️ El archivo debe tener al menos 5 columnas: Hora de inicio, Marca temporal, Estudiante, Pregunta 1 y Pregunta 2.")
        st.stop()

    # Renombrar columnas relevantes
    df = df.rename(columns={
        columnas[2]: "Estudiante",
        columnas[3]: "Aprendizaje",
        columnas[4]: "Uso_poco_ético"
    })

    # ---------------- CATEGORÍAS SUGERIDAS ----------------
    categorias = {
        "Ética y responsabilidad": ["ética", "responsable", "honesto", "crítico", "citar"],
        "Uso técnico o instrumental": ["herramienta", "usar", "aplicación", "tecnología", "IA", "ChatGPT"],
        "Pensamiento crítico": ["analizar", "reflexión", "verificar", "revisar", "cuestionar"],
        "Uso inapropiado o plagio": ["copiar", "pegar", "plagio", "sin revisar", "hacer tarea"],
        "Aprendizaje y descubrimiento": ["aprendido", "descubierto", "aprendizaje", "comprendido", "mejorar"],
        "Dependencia o abuso": ["dependencia", "abuso", "automatizado", "cerebro deja"]
    }

    def sugerir_categorias(texto):
        texto = texto.lower()
        return [cat for cat, palabras in categorias.items() if any(p in texto for p in palabras)]

    df["Categorías sugeridas (P1)"] = df["Aprendizaje"].apply(sugerir_categorias)
    df["Categorías sugeridas (P2)"] = df["Uso_poco_ético"].apply(sugerir_categorias)

    # ---------------- FILTROS ----------------
    st.sidebar.header("🔍 Filtros de análisis")
    estudiante_sel = st.sidebar.selectbox("Filtrar por estudiante", ["Todos"] + sorted(df["Estudiante"].unique().tolist()))
    palabra_clave = st.sidebar.text_input("Buscar palabra clave en respuestas", "")

    df_filtrado = df.copy()
    if estudiante_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estudiante"] == estudiante_sel]
    if palabra_clave:
        df_filtrado = df_filtrado[
            df_filtrado["Aprendizaje"].str.contains(palabra_clave, case=False, na=False) |
            df_filtrado["Uso_poco_ético"].str.contains(palabra_clave, case=False, na=False)
        ]

    st.success(f"📄 Mostrando {len(df_filtrado)} respuestas filtradas.")

    # ---------------- VISOR DE RESPUESTAS ----------------
    st.header("💬 Exploración de respuestas")

    for i, row in df_filtrado.iterrows():
        with st.expander(f"🎓 {row['Estudiante']} — Análisis cualitativo"):
            st.markdown(f"**Pregunta 1 – Aprendizajes:** {row['Aprendizaje']}")
            st.markdown(f"**Sugerencia de categorías:** {', '.join(row['Categorías sugeridas (P1)']) or '—'}")
            st.markdown("---")
            st.markdown(f"**Pregunta 2 – Uso poco ético:** {row['Uso_poco_ético']}")
            st.markdown(f"**Sugerencia de categorías:** {', '.join(row['Categorías sugeridas (P2)']) or '—'}")

    # ---------------- NUBE DE PALABRAS ----------------
    st.header("☁️ Nube de palabras (respuestas filtradas)")

    stopwords_es = set(STOPWORDS)
    stopwords_extra = {
        "que","de","la","el","en","y","a","los","las","del","se","por","con","una","un",
        "para","como","su","al","es","lo","más","ha","sus","o","le","ya","sin","sí",
        "esto","esa","ese","son","muy","me","mi","si","no","hay","fue","puede","ser","he","han","está"
    }
    stopwords_es.update(stopwords_extra)

    def limpiar_texto(texto):
        texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", str(texto))
        return texto.lower()

    texto_completo = " ".join(df_filtrado["Aprendizaje"].astype(str)) + " " + " ".join(df_filtrado["Uso_poco_ético"].astype(str))
    texto_completo = limpiar_texto(texto_completo)

    if len(texto_completo.strip()) > 0:
        wc = WordCloud(width=1000, height=400, background_color="white",
                       stopwords=stopwords_es, colormap="viridis").generate(texto_completo)
        st.image(wc.to_array(), use_container_width=True)
    else:
        st.info("No hay texto suficiente para generar la nube de palabras.")

    # ---------------- CONTADOR DE CATEGORÍAS ----------------
    st.header("📊 Distribución de categorías sugeridas")

    todas = df_filtrado["Categorías sugeridas (P1)"].explode().tolist() + df_filtrado["Categorías sugeridas (P2)"].explode().tolist()
    conteo = pd.Series(todas).value_counts().reset_index()
    conteo.columns = ["Categoría", "Frecuencia"]

    fig, ax = plt.subplots()
    ax.barh(conteo["Categoría"], conteo["Frecuencia"], color="#3b82f6")
    ax.set_xlabel("Frecuencia")
    ax.set_ylabel("Categoría")
    ax.invert_yaxis()
    st.pyplot(fig)

    # ---------------- DESCARGA ----------------
    with st.expander("📥 Descargar base con sugerencias"):
        st.dataframe(df_filtrado, use_container_width=True)
        st.download_button(
            "⬇️ Descargar CSV enriquecido",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="respuestas_analisis_cualitativo.csv",
            mime="text/csv"
        )

else:
    st.info("📤 Sube un archivo CSV o XLSX para comenzar tu análisis.")
