import streamlit as st
import pandas as pd
import re
import io
from typing import List, Dict
import matplotlib.pyplot as plt

# ------- Config -------
st.set_page_config(page_title="Dashboard cualitativo de entrevistas", page_icon="🗣️", layout="wide")
st.title("🗣️ Dashboard cualitativo de entrevistas (codificación por turnos)")
st.markdown("""
1) Sube tu PDF **o** pega el texto de la transcripción.  
2) Define categorías y palabras clave (en la barra lateral).  
3) Explora turno por turno, marca categorías y añade extractos.  
4) Filtra por hablante / palabra clave y exporta resultados.
""")

# ------- Sidebar: categorías (editor robusto) -------
st.sidebar.header("🧩 Diccionario de categorías")
st.sidebar.markdown("Una por línea con el formato: `Categoría: palabra1, palabra2, ...`")

default_cats = """\
Motivación personal: motivó, motivación, vocación, aportar, granito de arena
Intereses académicos: materia, lecturas, plan de estudios, teoría, estadística
Trabajo comunitario: comunidad, maíz, derechos, traductores, tejido social
Sector salud: hospital, salud, pacientes, sector salud
Proyección profesional: especializarme, proyección, futuro, DIF, niños, niñas
Dificultades/retos: complejo, difícil, adaptarme, reto
Valores prosociales: ayudar, apoyo, adoptar, buscar hogar, solidaridad
Relevancia TS: importancia, papel, guiar, empoderarse, intervenir
"""

cats_text = st.sidebar.text_area("Categorías y palabras clave", value=default_cats, height=220)

def parse_categories(txt: str) -> Dict[str, List[str]]:
    cats = {}
    for line in txt.strip().split("\n"):
        if ":" in line:
            cat, kws = line.split(":", 1)
            kw_list = [w.strip().lower() for w in kws.split(",") if w.strip()]
            if cat.strip():
                cats[cat.strip()] = kw_list
    return cats

CATS = parse_categories(cats_text)

# ------- Carga de archivo / texto -------
st.sidebar.header("📂 Transcripción")
uploaded = st.sidebar.file_uploader("Sube PDF (texto seleccionable) o TXT", type=["pdf", "txt"])
raw_text = st.text_area("…o pega aquí el texto de la entrevista", height=180, placeholder="Pega la transcripción completa aquí si no vas a subir archivo.")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber
    except ModuleNotFoundError:
        st.error("Falta pdfplumber. Agrega `pdfplumber` a requirements.txt")
        return ""
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text

full_text = ""
if uploaded is not None:
    if uploaded.name.lower().endswith(".pdf"):
        full_text = extract_text_from_pdf(uploaded.read())
    else:
        full_text = uploaded.read().decode("utf-8", errors="ignore")
elif raw_text.strip():
    full_text = raw_text.strip()

if not full_text.strip():
    st.info("Sube un PDF/TXT o pega el texto para iniciar.")
    st.stop()

# ------- Limpieza y segmentación por turnos -------
st.header("🔎 Segmentación por turnos")

# Intenta detectar hablantes: líneas tipo "JC: ...", "MJS: ...", "BJP: ..."
# Ajustable: agrega iniciales adicionales si tu entrevista usa otros códigos
speaker_pattern = r"^([A-ZÁÉÍÓÚÑ]{1,5}):\s*(.+)$"

turnos = []
for line in full_text.splitlines():
    line = line.strip()
    if not line:
        continue
    m = re.match(speaker_pattern, line)
    if m:
        spk = m.group(1).strip()
        utt = m.group(2).strip()
        turnos.append({"Hablante": spk, "Texto": utt})
    else:
        # línea continua del turno anterior (párrafo multilinea)
        if turnos:
            turnos[-1]["Texto"] += " " + line

df = pd.DataFrame(turnos)
if df.empty:
    st.warning("No se detectaron turnos con el patrón `INICIALES: texto`. Revisa el formato del documento.")
    st.stop()

st.caption(f"Turnos detectados: {len(df)}  •  Hablantes: {', '.join(sorted(df['Hablante'].unique().tolist()))}")

# ------- Estado de sesión: codificación -------
if "codes" not in st.session_state:
    st.session_state.codes = {}  # idx -> {"cats": set(), "extracts": {cat: [..]}}

def init_row_state(i: int):
    if i not in st.session_state.codes:
        st.session_state.codes[i] = {"cats": set(), "extracts": {}}

def suggest_sentences(text: str, keywords: List[str], max_len=280) -> List[str]:
    # devuelve oraciones que contengan alguna kw
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    outs = []
    for s in sents:
        s_low = s.lower()
        if any(kw in s_low for kw in keywords):
            frag = s.strip()
            if len(frag) > max_len:
                frag = frag[:max_len].rstrip() + "…"
            if frag and frag not in outs:
                outs.append(frag)
    return outs

# ------- Filtros -------
st.header("🎚️ Filtros y navegación")
colf1, colf2, colf3 = st.columns([1,1,2])
with colf1:
    hablantes = ["(Todos)"] + sorted(df["Hablante"].unique().tolist())
    f_spk = st.selectbox("Hablante", hablantes)
with colf2:
    f_kw = st.text_input("Palabra clave", "")
with colf3:
    st.caption("Tip: filtra por 'MJS' o 'BJP' para ver solo sus intervenciones.")

filtered = df.copy()
if f_spk != "(Todos)":
    filtered = filtered[filtered["Hablante"] == f_spk]
if f_kw.strip():
    mask = filtered["Texto"].str.contains(f_kw, case=False, na=False)
    filtered = filtered[mask]

st.success(f"Mostrando {len(filtered)} turnos")

if "row_ptr" not in st.session_state:
    st.session_state.row_ptr = 0
if len(filtered) == 0:
    st.stop()

# Corrige puntero si queda fuera de rango tras filtrar
st.session_state.row_ptr = min(st.session_state.row_ptr, len(filtered)-1)
row_idx = filtered.index.tolist()[st.session_state.row_ptr]
init_row_state(row_idx)

# ------- Panel del turno actual -------
st.subheader("🧩 Turno actual")
turn = df.loc[row_idx]
st.markdown(f"**Hablante:** `{turn['Hablante']}`")
st.write(turn["Texto"])

st.markdown("**Sugerencias de categorías (marca las que apliquen y selecciona extractos):**")
for cat, kws in CATS.items():
    sug = suggest_sentences(turn["Texto"], kws)
    key_cat = f"cat_{row_idx}_{re.sub(r'[^a-zA-Z0-9]+','_',cat.lower())}"
    checked = cat in st.session_state.codes[row_idx]["cats"]
    new_checked = st.checkbox(cat, value=checked, key=key_cat)
    if new_checked:
        st.session_state.codes[row_idx]["cats"].add(cat)
    else:
        st.session_state.codes[row_idx]["cats"].discard(cat)

    # extractos sugeridos por categoría
    pickeds = []
    for j, s in enumerate(sug):
        key_ext = f"ext_{row_idx}_{re.sub(r'[^a-zA-Z0-9]+','_',cat.lower())}_{j}"
        already = s in st.session_state.codes[row_idx]["extracts"].get(cat, [])
        if st.checkbox(f"“{s}”", value=already, key=key_ext):
            pickeds.append(s)

    # caja para extracto manual
    man_key = f"man_{row_idx}_{re.sub(r'[^a-zA-Z0-9]+','_',cat.lower())}"
    manual = st.text_area("Agregar extracto manual (opcional)", key=man_key, height=70, placeholder="Pega/Escribe un fragmento representativo…")
    if manual.strip():
        pickeds.append(manual.strip())

    if pickeds:
        st.session_state.codes[row_idx]["extracts"][cat] = pickeds
    elif cat in st.session_state.codes[row_idx]["extracts"]:
        # deja vacío si desmarcaron todo
        st.session_state.codes[row_idx]["extracts"][cat] = [e for e in st.session_state.codes[row_idx]["extracts"][cat] if e]

st.markdown("---")
cnav1, cnav2, cnav3 = st.columns([1,1,6])
with cnav1:
    if st.button("⟵ Anterior"):
        st.session_state.row_ptr = (st.session_state.row_ptr - 1) % len(filtered)
        st.experimental_rerun()
with cnav2:
    if st.button("Siguiente ⟶"):
        st.session_state.row_ptr = (st.session_state.row_ptr + 1) % len(filtered)
        st.experimental_rerun()

# ------- Resumen rápido (opcional) -------
st.header("📊 Resumen (conteo simple por categoría en lo filtrado)")
# Construir conteos en base a lo que ya se marcó
cat_counts = {c: 0 for c in CATS.keys()}
for i in filtered.index:
    if i in st.session_state.codes:
        for c in st.session_state.codes[i]["cats"]:
            if c in cat_counts:
                cat_counts[c] += 1

summary = pd.DataFrame([{"Categoría": k, "Frecuencia": v} for k, v in cat_counts.items()]).sort_values("Frecuencia", ascending=False)
fig, ax = plt.subplots()
ax.barh(summary["Categoría"], summary["Frecuencia"])
ax.set_xlabel("Frecuencia (turnos codificados)")
ax.invert_yaxis()
st.pyplot(fig)

# ------- Exportación -------
st.header("📦 Exportar codificación")

# Formato largo: una fila por (turno, hablante, categoría) con extractos concatenados
rows_long = []
for i, code in st.session_state.codes.items():
    spk = df.loc[i, "Hablante"]
    txt = df.loc[i, "Texto"]
    for cat in code["cats"]:
        extracts = " || ".join(code["extracts"].get(cat, []))
        rows_long.append({
            "TurnoIndex": i,
            "Hablante": spk,
            "Categoría": cat,
            "Extractos": extracts,
            "TextoCompleto": txt
        })
df_long = pd.DataFrame(rows_long)

# Matriz (ancha): columnas 0/1 por categoría y columnas con extractos
wide_rows = []
for i in df.index:
    spk = df.loc[i, "Hablante"]
    txt = df.loc[i, "Texto"]
    row_out = {"TurnoIndex": i, "Hablante": spk, "TextoCompleto": txt}
    for cat in CATS.keys():
        row_out[f"{cat}_flag"] = 1 if (i in st.session_state.codes and cat in st.session_state.codes[i]["cats"]) else 0
        exts = (st.session_state.codes.get(i, {}).get("extracts", {}).get(cat, [])) or []
        row_out[f"{cat}_extractos"] = " || ".join(exts)
    wide_rows.append(row_out)
df_wide = pd.DataFrame(wide_rows)

colx1, colx2 = st.columns(2)
with colx1:
    st.subheader("Formato largo")
    st.dataframe(df_long, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (largo)",
        data=df_long.to_csv(index=False).encode("utf-8-sig"),
        file_name="codificacion_largo.csv",
        mime="text/csv"
    )
with colx2:
    st.subheader("Formato ancho (matriz + extractos)")
    st.dataframe(df_wide, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (ancho)",
        data=df_wide.to_csv(index=False).encode("utf-8-sig"),
        file_name="codificacion_matriz.csv",
        mime="text/csv"
    )
