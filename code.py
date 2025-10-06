import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, List

# =============== CONFIGURACIÓN ===============
st.set_page_config(
    page_title="Laboratorio de Codificación Cualitativa",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Laboratorio de Codificación Cualitativa (P1/P2)")
st.markdown("""
Este panel te ayuda a **codificar cualitativamente** respuestas abiertas:
- Carga tu CSV
- Mapea columnas (Estudiante, P1, P2, tiempos)
- Revisa **sugerencias de categorías** por palabras clave
- Marca categorías y selecciona **extractos**
- Exporta la codificación (largo y ancho)
""")

# =============== CATEGORÍAS (editable) ===============
st.sidebar.header("🧩 Diccionario de categorías (editable)")

# Categorías por defecto (puedes ajustar libremente)
default_categories = pd.DataFrame({
    "Categoria": [
        "Ética y responsabilidad",
        "Uso técnico o instrumental",
        "Pensamiento crítico",
        "Uso inapropiado o plagio",
        "Aprendizaje y descubrimiento",
        "Dependencia o abuso"
    ],
    "Palabras_clave": [
        "ética, responsable, honesto, crítico, citar",
        "herramienta, usar, aplicación, tecnología, ia, chatgpt",
        "analizar, reflexión, verificar, revisar, cuestionar, fuentes",
        "copiar, pegar, plagio, sin revisar, hacer tarea",
        "aprendido, descubierto, aprendizaje, comprendido, mejorar",
        "dependencia, abuso, automatizado, cerebro deja"
    ]
})

cat_df = st.sidebar.data_editor(
    default_categories,
    use_container_width=True,
    num_rows="dynamic",
    key="cat_editor",
    help="Edita o agrega categorías y lista de palabras clave (separa con comas)."
)

def build_category_dict(df: pd.DataFrame) -> Dict[str, List[str]]:
    cats = {}
    for _, row in df.iterrows():
        cat = str(row["Categoria"]).strip()
        if not cat or cat.lower() == "nan":
            continue
        kws = [w.strip().lower() for w in str(row["Palabras_clave"]).split(",") if w.strip()]
        cats[cat] = kws
    return cats

CATEGORIES = build_category_dict(cat_df)

# =============== CARGA DE DATOS ===============
st.sidebar.header("📂 Datos")
uploaded = st.sidebar.file_uploader("Sube CSV o XLSX con respuestas", type=["csv", "xlsx"])

if uploaded is None:
    st.info("Sube tu archivo para comenzar.")
    st.stop()

# Lectura
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
col_t0  = st.sidebar.selectbox("Hora de inicio (opcional)", options=["(ninguna)"] + all_cols, index=0)
col_t1  = st.sidebar.selectbox("Marca temporal (opcional)", options=["(ninguna)"] + all_cols, index=0)

df = df_raw.copy()
df = df.rename(columns={
    col_est: "Estudiante",
    col_p1: "P1",
    col_p2: "P2"
})
if col_t0 != "(ninguna)":
    df["Hora_inicio"] = pd.to_datetime(df_raw[col_t0], errors="coerce")
if col_t1 != "(ninguna)":
    df["Marca_temporal"] = pd.to_datetime(df_raw[col_t1], errors="coerce")

# Tiempo de respuesta
if "Hora_inicio" in df.columns and "Marca_temporal" in df.columns:
    df["Tiempo_respuesta_min"] = (df["Marca_temporal"] - df["Hora_inicio"]).dt.total_seconds() / 60
else:
    df["Tiempo_respuesta_min"] = None

# =============== ESTADO DE SESIÓN PARA CÓDIGOS ===============
# Estructura:
# session_state.codes[row_index] = {
#   "P1": {"cats": set([...]), "extracts": {cat: [str, ...]}},
#   "P2": {"cats": set([...]), "extracts": {cat: [str, ...]}}
# }
if "codes" not in st.session_state:
    st.session_state.codes = {}

# Navegación simple
if "row_idx" not in st.session_state:
    st.session_state.row_idx = 0

def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s.strip().lower())

def init_row_state(i: int):
    if i not in st.session_state.codes:
        st.session_state.codes[i] = {
            "P1": {"cats": set(), "extracts": {}},
            "P2": {"cats": set(), "extracts": {}}
        }

def suggest_sentences(text: str, keywords: List[str], max_len=280) -> List[str]:
    """
    Devuelve oraciones del texto que contengan alguna palabra clave.
    Fragmenta por puntos básicos y filtra por coincidencia.
    """
    if not isinstance(text, str):
        return []
    # Split básico por oraciones
    sentences = re.split(r"(?<=[\.\!\?])\s+", text.strip())
    out = []
    t_low = text.lower()
    for s in sentences:
        s_low = s.lower()
        if any(kw in s_low for kw in keywords):
            frag = s.strip()
            # recorte simple si fuese muy largo
            if len(frag) > max_len:
                frag = frag[:max_len].rstrip() + "…"
            if frag:
                out.append(frag)
    return list(dict.fromkeys(out))  # sin duplicados preservando orden

def ensure_extract_list(i: int, q: str, cat: str):
    if cat not in st.session_state.codes[i][q]["extracts"]:
        st.session_state.codes[i][q]["extracts"][cat] = []

# =============== FILTROS ===============
st.sidebar.header("🔎 Filtros")
students = ["(Todos)"] + sorted(df["Estudiante"].dropna().astype(str).unique().tolist())
student_filter = st.sidebar.selectbox("Filtrar por estudiante", students, index=0)

kw_query = st.sidebar.text_input("Buscar palabra/fras en P1/P2", "")
filtered_df = df.copy()
if student_filter != "(Todos)":
    filtered_df = filtered_df[filtered_df["Estudiante"].astype(str) == student_filter]
if kw_query.strip():
    mask = filtered_df["P1"].astype(str).str.contains(kw_query, case=False, na=False) | \
           filtered_df["P2"].astype(str).str.contains(kw_query, case=False, na=False)
    filtered_df = filtered_df[mask]

st.success(f"Mostrando {len(filtered_df)} registros filtrados.")

# =============== PANELES: RESPUESTA ACTUAL + CODIFICACIÓN ===============
if len(filtered_df) == 0:
    st.info("No hay registros con los filtros actuales.")
    st.stop()

# Ajustar índice actual si se sale del rango del df filtrado
valid_indices = filtered_df.index.tolist()
if st.session_state.row_idx not in valid_indices:
    st.session_state.row_idx = valid_indices[0]

row_idx = st.session_state.row_idx
init_row_state(row_idx)

current = df.loc[row_idx]
st.subheader(f"🎓 {current['Estudiante']}")
if pd.notna(current.get("Tiempo_respuesta_min")):
    st.caption(f"⏱️ Tiempo de respuesta: {current['Tiempo_respuesta_min']:.2f} min")

# === Dos columnas: P1 y P2 ===
c1, c2 = st.columns(2)

# ---------- P1 ----------
with c1:
    st.markdown("### 💭 Pregunta 1 (Aprendizajes)")
    st.write(current["P1"])

    st.markdown("**Sugerencias de categorías** (marca las que apliquen y elige extractos):")
    for cat, keywords in CATEGORIES.items():
        # Sugerencias de extractos por categoría
        suggestions = suggest_sentences(str(current["P1"]), keywords)
        cat_key = f"p1_cat_{slugify(cat)}_{row_idx}"
        checked = cat in st.session_state.codes[row_idx]["P1"]["cats"]
        new_checked = st.checkbox(cat, value=checked, key=cat_key)
        # actualizar set de cats al vuelo
        if new_checked:
            st.session_state.codes[row_idx]["P1"]["cats"].add(cat)
        else:
            st.session_state.codes[row_idx]["P1"]["cats"].discard(cat)

        # Extractos sugeridos
        if suggestions:
            st.caption("Extractos sugeridos (puedes seleccionar varios):")
            ensure_extract_list(row_idx, "P1", cat)
            chosen = []
            for j, s in enumerate(suggestions):
                ck_key = f"p1_ext_{slugify(cat)}_{row_idx}_{j}"
                is_sel = s in st.session_state.codes[row_idx]["P1"]["extracts"].get(cat, [])
                sel = st.checkbox(f"“{s}”", value=is_sel, key=ck_key)
                if sel:
                    chosen.append(s)
            # Campo para agregar extractos manuales
            man_key = f"p1_manual_{slugify(cat)}_{row_idx}"
            manual = st.text_area("Agregar extracto manual (opcional)", key=man_key, height=80, placeholder="Pega aquí un fragmento relevante…")
            if manual.strip():
                chosen.append(manual.strip())

            # Actualizar extractos guardados
            st.session_state.codes[row_idx]["P1"]["extracts"][cat] = chosen
        else:
            st.caption("_Sin sugerencias automáticas para esta categoría (puedes marcarla igual si aplica)._")
            ensure_extract_list(row_idx, "P1", cat)
            man_key = f"p1_manual_only_{slugify(cat)}_{row_idx}"
            manual = st.text_area("Agregar extracto manual (opcional)", key=man_key, height=80, placeholder="Pega aquí un fragmento relevante…")
            if manual.strip():
                st.session_state.codes[row_idx]["P1"]["extracts"][cat] = [manual.strip()]

# ---------- P2 ----------
with c2:
    st.markdown("### 🚫 Pregunta 2 (Uso poco ético observado)")
    st.write(current["P2"])

    st.markdown("**Sugerencias de categorías** (marca las que apliquen y elige extractos):")
    for cat, keywords in CATEGORIES.items():
        suggestions = suggest_sentences(str(current["P2"]), keywords)
        cat_key = f"p2_cat_{slugify(cat)}_{row_idx}"
        checked = cat in st.session_state.codes[row_idx]["P2"]["cats"]
        new_checked = st.checkbox(cat, value=checked, key=cat_key)
        if new_checked:
            st.session_state.codes[row_idx]["P2"]["cats"].add(cat)
        else:
            st.session_state.codes[row_idx]["P2"]["cats"].discard(cat)

        if suggestions:
            st.caption("Extractos sugeridos (puedes seleccionar varios):")
            ensure_extract_list(row_idx, "P2", cat)
            chosen = []
            for j, s in enumerate(suggestions):
                ck_key = f"p2_ext_{slugify(cat)}_{row_idx}_{j}"
                is_sel = s in st.session_state.codes[row_idx]["P2"]["extracts"].get(cat, [])
                sel = st.checkbox(f"“{s}”", value=is_sel, key=ck_key)
                if sel:
                    chosen.append(s)
            man_key = f"p2_manual_{slugify(cat)}_{row_idx}"
            manual = st.text_area("Agregar extracto manual (opcional)", key=man_key, height=80, placeholder="Pega aquí un fragmento relevante…")
            if manual.strip():
                chosen.append(manual.strip())
            st.session_state.codes[row_idx]["P2"]["extracts"][cat] = chosen
        else:
            st.caption("_Sin sugerencias automáticas para esta categoría (puedes marcarla igual si aplica)._")
            ensure_extract_list(row_idx, "P2", cat)
            man_key = f"p2_manual_only_{slugify(cat)}_{row_idx}"
            manual = st.text_area("Agregar extracto manual (opcional)", key=man_key, height=80, placeholder="Pega aquí un fragmento relevante…")
            if manual.strip():
                st.session_state.codes[row_idx]["P2"]["extracts"][cat] = [manual.strip()]

# =============== NAVEGACIÓN ===============
nav_col1, nav_col2, nav_col3 = st.columns([1,1,6])
with nav_col1:
    if st.button("⟵ Anterior"):
        # buscar índice anterior dentro del filtrado actual
        pos = valid_indices.index(row_idx)
        if pos > 0:
            st.session_state.row_idx = valid_indices[pos - 1]
        st.experimental_rerun()
with nav_col2:
    if st.button("Siguiente ⟶"):
        pos = valid_indices.index(row_idx)
        if pos < len(valid_indices) - 1:
            st.session_state.row_idx = valid_indices[pos + 1]
        st.experimental_rerun()

st.markdown("---")

# =============== RESÚMENES Y EXPORTACIÓN ===============
st.header("📦 Exportar codificación")

# Construir formato largo
rows_long = []
for i in filtered_df.index.tolist():
    est = df.loc[i, "Estudiante"]
    tmin = df.loc[i, "Tiempo_respuesta_min"]
    for q in ["P1", "P2"]:
        coded_cats = list(st.session_state.codes.get(i, {}).get(q, {}).get("cats", set()))
        extracts_map = st.session_state.codes.get(i, {}).get(q, {}).get("extracts", {})
        # Para cada categoría marcada, guardar extractos (si existen)
        for cat in coded_cats:
            exts = extracts_map.get(cat, [])
            rows_long.append({
                "RowIndex": i,
                "Estudiante": est,
                "Pregunta": q,
                "Categoria": cat,
                "Extractos": " || ".join(exts) if exts else "",
                "Tiempo_respuesta_min": tmin
            })

df_long = pd.DataFrame(rows_long)

# Construir formato ancho (matriz 0/1 + extractos)
def all_categories_list(cats_dict: Dict[str, List[str]]) -> List[str]:
    return list(cats_dict.keys())

all_cats = all_categories_list(CATEGORIES)

wide_rows = []
for i in filtered_df.index.tolist():
    est = df.loc[i, "Estudiante"]
    tmin = df.loc[i, "Tiempo_respuesta_min"]
    row_out = {"RowIndex": i, "Estudiante": est, "Tiempo_respuesta_min": tmin}
    # Inicializar 0/1 y extractos para P1/P2
    for cat in all_cats:
        row_out[f"P1_{cat}"] = 1 if cat in st.session_state.codes.get(i, {}).get("P1", {}).get("cats", set()) else 0
        row_out[f"P2_{cat}"] = 1 if cat in st.session_state.codes.get(i, {}).get("P2", {}).get("cats", set()) else 0
        ex1 = st.session_state.codes.get(i, {}).get("P1", {}).get("extracts", {}).get(cat, [])
        ex2 = st.session_state.codes.get(i, {}).get("P2", {}).get("extracts", {}).get(cat, [])
        row_out[f"P1_{cat}_extractos"] = " || ".join(ex1) if ex1 else ""
        row_out[f"P2_{cat}_extractos"] = " || ".join(ex2) if ex2 else ""
    wide_rows.append(row_out)

df_wide = pd.DataFrame(wide_rows)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.subheader("📄 Codificación (formato largo)")
    st.dataframe(df_long, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (largo)",
        data=df_long.to_csv(index=False).encode("utf-8-sig"),
        file_name="codificacion_largo.csv",
        mime="text/csv"
    )

with col_dl2:
    st.subheader("🧮 Matriz (formato ancho 0/1 + extractos)")
    st.dataframe(df_wide, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (ancho)",
        data=df_wide.to_csv(index=False).encode("utf-8-sig"),
        file_name="codificacion_matriz.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Plantilla didáctica y replicable para análisis cualitativo con P1/P2. Edita el diccionario de categorías y codifica con extractos.")
