# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Dashboard de entrevistas - Trabajo Social",
    page_icon="🗣️",
    layout="wide"
)

st.title("🗣️ Dashboard de análisis cualitativo")
st.markdown("Explora los hallazgos de la entrevista según el entrevistado seleccionado.")

# ---------------- DATOS DE LA ENTREVISTA ----------------
entrevistados = {
    "Mariel Jiménez Sánchez": {
        "Edad": 19,
        "Ocupación": "Estudiante",
        "Duración": "16 min 51 s",
        "Categorías": {
            "Motivación inicial": 5,
            "Cambio de percepción": 4,
            "Relevancia del TS": 3,
            "Proyección profesional": 3,
            "Factores personales": 1
        },
        "Extractos": {
            "Motivación inicial": [
                "“Mi primera opción era diseño gráfico y comunicación visual...”",
                "“Me motivó seguir adelante con respecto a temas medioambientales.”"
            ],
            "Cambio de percepción": [
                "“La maestra habla mucho del maíz y del trabajo en comunidades.”",
                "“Siguen habiendo cosas que me sorprenden e intrigan.”"
            ],
            "Relevancia del TS": [
                "“Nosotros somos guías y encaminamos a que la población se empodere.”",
                "“Juntos reactivamos ciertos tejidos sociales que se han ido rompiendo.”"
            ],
            "Proyección profesional": [
                "“Me gustaría enfocarme en el sector salud o en comunidades rurales.”",
                "“No me gusta estar en oficina, prefiero el trabajo al aire libre.”"
            ],
            "Factores personales": [
                "“Tengo familiares en el ámbito de la salud, eso también me inspira.”"
            ]
        },
        "Wordcloud_text": """
        medio ambiente comunidad salud social motivación carrera maestra maíz empoderamiento
        aprendizaje cambio personas campo sociedad retos interés derechos colectivos
        """
    },
    "Brian Jiménez Pacheco": {
        "Edad": 20,
        "Ocupación": "Estudiante",
        "Duración": "16 min 51 s",
        "Categorías": {
            "Motivación inicial": 4,
            "Cambio de percepción": 3,
            "Relevancia del TS": 4,
            "Proyección profesional": 3,
            "Factores personales": 2
        },
        "Extractos": {
            "Motivación inicial": [
                "“Quiero dejar mi granito de arena para mejorar la situación.”",
                "“Desde pequeño me gustaba ayudar a los animales y personas.”"
            ],
            "Cambio de percepción": [
                "“Ahora entiendo que TS tiene un gran papel en la sociedad.”",
                "“He aprendido que puedo aportar en diferentes sectores.”"
            ],
            "Relevancia del TS": [
                "“Sin los trabajadores sociales, muchas cosas seguirían estando mal.”",
                "“Nuestra intervención puede mejorar muchos aspectos de la sociedad.”"
            ],
            "Proyección profesional": [
                "“Me gustaría trabajar con niñas y niños.”",
                "“Podría especializarme en el sector salud o en el DIF.”"
            ],
            "Factores personales": [
                "“Mi papá siempre adopta animalitos, de él aprendí a ayudar.”"
            ]
        },
        "Wordcloud_text": """
        ayuda social comunidad niños familia sociedad cambio intervención empatía solidaridad
        aprendizaje salud dif animales vocación compromiso grupo personas mejorar
        """
    }
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("🎯 Selecciona el entrevistado")
selected = st.sidebar.selectbox("Entrevistado:", list(entrevistados.keys()))

datos = entrevistados[selected]

st.sidebar.markdown(f"**Edad:** {datos['Edad']} años")
st.sidebar.markdown(f"**Ocupación:** {datos['Ocupación']}")
st.sidebar.markdown(f"**Duración entrevista:** {datos['Duración']}")
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 **Entrevistadora:** JC")

# ---------------- CATEGORÍAS ----------------
st.header("📂 Categorías principales")
df_cats = pd.DataFrame(list(datos["Categorías"].items()), columns=["Categoría", "Frecuencia"])
st.dataframe(df_cats, use_container_width=True)

# ---------------- GRÁFICO DE BARRAS ----------------
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📊 Distribución de menciones")
    fig, ax = plt.subplots()
    ax.barh(df_cats["Categoría"], df_cats["Frecuencia"], color="#29A632")
    ax.set_xlabel("Frecuencia")
    plt.tight_layout()
    st.pyplot(fig)

# ---------------- NUBE DE PALABRAS ----------------
with col2:
    st.subheader("💬 Palabras más frecuentes")
    wordcloud = WordCloud(width=700, height=400, background_color="white").generate(datos["Wordcloud_text"])
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wordcloud, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)

# ---------------- EXTRACTOS ----------------
st.header("🧾 Extractos destacados")
for cat, frases in datos["Extractos"].items():
    with st.expander(cat):
        for f in frases:
            st.write(f)

# ---------------- PIE DE PÁGINA ----------------
st.markdown("---")
st.markdown(
    f"🕒 **Duración total:** {datos['Duración']} | 👩‍💻 **Entrevistadora:** JC | 📘 **Fuente:** Entrevista sobre elección de carrera"
)
st.caption("Dashboard interactivo desarrollado en Streamlit © 2025")
