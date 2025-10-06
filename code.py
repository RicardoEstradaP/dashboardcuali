import streamlit as st
import pandas as pd
import re
from datetime import datetime

# =============== CONFIGURACIÓN ===============
st.set_page_config(
    page_title="Laboratorio de Codificación Cualitativa",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Laboratorio de Codificación Cualitativa")
st.markdown("""
Este panel te ayuda a **codificar cualitativamente** respuestas abiertas.
1. Carga tu CSV  
2. Define tus **categorías y palabras clave**  
3. Revisa las respuestas  
4. Marca categorías y elige extractos  
5. Exporta los resultados en formato largo o matriz  
""")

# =============== CATEGORÍAS ===============
st.sidebar.header("🧩 Diccionario de categorías")
st.sidebar.markdown("Edita las categorías y sus palabras clave (una por línea, separadas por dos puntos y comas):")

default_text = """\
Ética y responsabilidad: ética, responsable, honesto, crítico, citar
Uso técnico o instrumental: herramienta, usar, aplicación, tecnología, ia, chatgpt
Pensamiento crítico: analizar, reflexión, verificar, revisar, cuestionar, fuentes
Uso inapropiado o plagio: copiar, pegar, plagio, sin revisar, hacer tarea
Aprendizaje y descubrimiento: aprendido, descubierto, aprendizaje, comprendido, mejorar
Dependencia o abuso: dependencia, abuso, automatizado, cerebro deja
"""

text_input = st.sidebar.text_area("Diccionario de categorías", value=default_text, height=220)

def parse_categorias(txt):
    categorias = {}
    for line in txt.strip().split("\n"):
        if ":" in line:
            cat, kws = line.split(":", 1)
            categorias[cat.strip()] = [w.strip().lower() for w in kws.split(",") if w.strip()]
    return categorias

CATEGORIES = parse_categorias(text_input)

# =============== CARGA DE DATOS ===============
st.sidebar.header("📂 Datos")
uploaded = st.sidebar.file_uploader("Sube CSV o XLSX con respuestas", type=["csv", "xlsx"])

if uploaded is None:
    st.info("Sube tu archivo para comenzar.")
    st.stop()

if uploaded.name.endswith(".csv"):
    df_raw = pd.read_csv(uploaded)
else:
    df_raw = pd.read_excel(uploaded)

df_raw.columns = df_raw.columns.str.strip()
all_cols = df_raw.columns.tolist()

st.sidebar.markdown("**Columnas detectadas:**")
st.sidebar.caption(", ".join(all_cols))

# =============== MAPEADOR DE COLUMNAS ===============
st.sidebar.header("🧭 Mapea columnas")
col_est = st.sidebar.selectbox("Estudiante", options=all_cols, index=min(2, len(all_cols)-1))
col_p1  = st.sidebar.selectbox("Pregunta 1 (Aprendizajes)", options=all_cols, index=min(3, len(all_cols)-1))
col_p2  = st.sidebar.selectbox("Pregunta 2 (Uso poco ético)", options=all_cols, index=min(4, len(all_cols)-1))

df = df_raw.copy()
df = df.rename(columns={col_est: "Estudiante", col_p1: "P1", col_p2: "P2"})

# =============== ESTADO DE SESIÓN ===============
if "codes" not in st.session_state:
    st.session_state.codes = {}
if "row_idx" not in st.session_state:
    st.session_state.row_idx = 0

def init_row_state(i):
    if i not in st.session_state.codes:
        st.session_state.codes[i] = {"P1": {"cats": set(), "extracts": {}}, "P2": {"cats": set(), "extracts": {}}}

def slugify(s: str):
    return re.sub(r"[^a-zA-Z0-9]+", "_", s.strip().lower())

def suggest_sentences(text, keywords):
    """Devuelve oraciones con coincidencias de palabras clave."""
    if not isinstance(text, str):
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if any(k in s.lower() for k in keywords)]

# =============== FILTROS ===============
st.sidebar.header("🔎 Filtros")
students = ["(Todos)"] + sorted(df["Estudiante"].dropna().astype(str).unique().tolist())
student_filter = st.sidebar.selectbox("Filtrar por estudiante", students, index=0)
kw_query = st.sidebar.text_input("Buscar palabra en respuestas", "")

df_filtered = df.copy()
if student_filter != "(Todos)":
    df_filtered = df_filtered[df_filtered["Estudiante"].astype(str) == student_filter]
if kw_query.strip():
    mask = df_filtered["P1"].astype(str).str.contains(kw_query, case=False, na=False) | \
           df_filtered["P2"].astype(str).str.contains(kw_query, case=False, na=False)
    df_filtered = df_filtered[mask]

st.success(f"📄 {len(df_filtered)} respuestas filtradas.")

if len(df_filtered) == 0:
    st.stop()

row_idx = df_filtered.index.tolist()[st.session_state.row_idx % len(df_filtered)]
init_row_state(row_idx)

# =============== VISOR DE RESPUESTAS ===============
row = df.loc[row_idx]
st.subheader(f"🎓 {row['Estudiante']}")

col1, col2 = st.columns(2)

for q, title, col in [("P1", "💭 Aprendizajes", col1), ("P2", "🚫 Uso poco ético", col2)]:
    with col:
        st.markdown(f"### {title}")
        st.write(row[q])

        for cat, kws in CATEGORIES.items():
            suggestions = suggest_sentences(row[q], kws)
            cat_key = f"{q}_{slugify(cat)}_{row_idx}"
            checked = cat in st.session_state.codes[row_idx][q]["cats"]
            sel = st.checkbox(cat, value=checked, key=cat_key)
            if sel:
                st.session_state.codes[row_idx][q]["cats"].add(cat)
            else:
                st.session_state.codes[row_idx][q]["cats"].discard(cat)

            if suggestions:
                st.caption("Extractos sugeridos:")
                chosen = []
                for j, s in enumerate(suggestions):
                    ck_key = f"{q}_{slugify(cat)}_{row_idx}_{j}"
                    is_sel = s in st.session_state.codes[row_idx][q]["extracts"].get(cat, [])
                    if st.checkbox(f"“{s.strip()}”", value=is_sel, key=ck_key):
                        chosen.append(s.strip())
                st.session_state.codes[row_idx][q]["extracts"][cat] = chosen

# =============== NAVEGACIÓN ===============
prev, next = st.columns(2)
if prev.button("⟵ Anterior"):
    st.session_state.row_idx = (st.session_state.row_idx - 1) % len(df_filtered)
    st.experimental_rerun()
if next.button("Siguiente ⟶"):
    st.session_state.row_idx = (st.session_state.row_idx + 1) % len(df_filtered)
    st.experimental_rerun()

# =============== EXPORTACIÓN ===============
st.header("📦 Exportar codificación")

rows = []
for i, data in st.session_state.codes.items():
    est = df.loc[i, "Estudiante"]
    for q in ["P1", "P2"]:
        for cat in data[q]["cats"]:
            extracts = " || ".join(data[q]["extracts"].get(cat, []))
            rows.append({"Estudiante": est, "Pregunta": q, "Categoría": cat, "Extractos": extracts})

df_out = pd.DataFrame(rows)
st.dataframe(df_out, use_container_width=True)
st.download_button(
    "⬇️ Descargar codificación",
    data=df_out.to_csv(index=False).encode("utf-8-sig"),
    file_name="codificacion_cualitativa.csv",
    mime="text/csv"
)
