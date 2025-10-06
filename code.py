import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

# ===================== CONFIG =====================
st.set_page_config(page_title="Dashboard cualitativo (entrevista embebida)", page_icon="🗣️", layout="wide")
st.title("🗣️ Dashboard cualitativo – Entrevista embebida (sin subir archivo)")
st.caption("Explora categorías temáticas y extractos por hablante. El análisis ya viene integrado en el código.")

# ===================== ENTREVISTA (EMBEBIDA) =====================
TRANSCRIPCION = """
JC: Agradezco totalmente el tiempo que le están dedicando a estas entrevistas. Para comenzar, ¿me
podría decir cada uno su nombre, edad y a qué se dedican?
MJS: Yo me llamo Mariel Jiménez Sánchez, tengo 19 años y soy estudiante
BJP: Yo me llamo Brian Jiménez Pacheco, tengo 20 años y actualmente solo soy estudiante.
JC: Mariel, ¿qué te motivo a elegir TS como carrera?
MJS: Yo no soy de pase directo, entonces tuve que hacer examen, en el primer examen yo iba para otra
carrera y me faltaron como 10 aciertos más o menos, entonces mi plan era meter una carrera de
poquitos aciertos, cursar unos semestres y pedir un cambio de carrera, pero al parecer solo es dentro de
la misma escuela o facultad que tenga varias carreras, pero ya después creo que en estos semestres que
he tenido, me motivó un poquito más el seguir adelante la carrera con respecto a temas medio
ambientales, así como la alimentación, eso ha sido últimamente como mi motivación.
JC: Brian, ¿a ti qué te motivó a elegir TS como carrera?
BJP: Antes lo tenía con otro concepto, pero ahora que ya estamos en tercer semestre, lo pondría así: me
motivó a querer dejar mi granito de arena y hacer algunas intervenciones, lo que se pueda para poder
mejorar la situación, ya sea, como decía Mariel, algo así como de comunidades, etc. Dejar ahora sí que
mi aporte a la sociedad.
JC: Mariel, ya que mencionas que TS no era tu primer opción, ¿cuál sí era tu primera opción y por qué?
MJS: mi primera opción era diseño gráfico y comunicación visual y la había escogido porque a mí me
gusta mucho dibujar, y pues no sé, quería como experimentar otras cosas. Salirme de lo común de lo que
ya había llevado y además porque ya tenía un poquito de experiencia en arte, pues tuve desde
arquitectura y en la prepa llevé diseño gráfico, pero pues no fue tan a fondo y me interesaba profundizar
en diseño gráfico.
JC: Y ahora, ¿podrías compartirme qué te está motivando a continuar con la carrera de TS?
MJS: En este semestre llevamos una materia que se llama población y medio ambiente, y la forma en
cómo la maestra da su clase y como habla. Ella habla mucho del maíz y de trabajo de comunidades. Las
lecturas que ha compartido me llaman mucho la atención, desde qué enfoque podemos dar a las
comunidades, como dijo Brian, poner nuestro granito de arena, y en verdad que ellos puedan exigir sus
derechos, porque muchas veces se les viola, por falta de traductores [inaudible]
JC: Brian, ¿hay algo algún acontecimiento de tu vida que recuerdes que te haya motivado a elegir TS?
BJP: Pues sí, creo que sí, de chiquito, más con los animalitos como que tendía a ayudarlos, por decir a los
animalitos de la calle, gatos, perros, o hasta incluso, a aves llegué a cuidar, por lo mismo de eso, me di
cuenta de que, a lo mejor lo mío era, en algún punto en alguna carrera en intervenir y poner mi granito
de arena. De hecho, también hice examen para la UAM porque tampoco tengo pase directo y en la UAM
había escogido sociología, pero pues ya, teniendo también el aspirante seleccionado en la UNAM, pues
decidí mejor por la UNAM por TS.
JC: Mariel, ¿cuáles eran tus expectativas de la carrera cuando iniciaste?
MJS: Sinceramente, como que se me hacía una carrera muy compleja, o sea, antes de meter las carreras
para el examen había visto más o menos el plan de estudios. A mí me llamó mucho la atención de ver
esto como de teoría social, teoría económica o estadística, fue lo que jamás me imaginé, y entonces se
me hizo como un reto, más que verlo como una expectativa, fue como un reto para aprender cosas
nuevas. Yo venía más como de área 4 y no de área 3, no venía tan familiarizada con conceptos como de
área 3, entonces, en ese aspecto mis expectativas podía decir que eran más como un reto, como alto de
cierto modo, para mí.
JC: Brian, ¿cuáles eran tus expectativas cuando iniciaste la carrera?
BJP: Pues, no estoy seguro, pero sí venía como, vengo de ganas, de hecho, de quererme superar, es una
difícil pregunta, no tengo como una respuesta.
JC: Brian, ¿qué opinión tienes ahorita de la carrera?
BJP: pues que es una increíble carrera, sin duda alguna, es una carrera que necesita que el mundo la
voltee a ver más, que tiene un gran papel. Pues ahorita yo, totalmente encantado de la carrera, eso sí,
me ha costado trabajo, porque yo en la preparatoria llevé, bueno desde chico, se me da mucho la
programación, entonces, el haber cambiado así, drásticamente, pues sí me ha costado trabajo
adaptarme, pero sin duda alguna, me encuentro encantado con la carrera, y a seguir
JC: Mariel, ¿tú qué opinión tienes en este momento de la carrera?
MJS: retomo un poco de lo que dijo Brian, se me sigue haciendo una carrera muy compleja, igual ha sido
como difícil, pero se me hace muy interesante, siguen habiendo cosas que no me dejan de sorprender,
entonces como que me siguen intrigando de cierto modo, porque por ejemplo, yo tengo primos que
trabajan en un hospital, son enfermeros y cuando fue todo lo de la pandemia, me contaban lo que
hacían los TS en el hospital donde ellos trabajan. Entonces, cuando empezábamos a leer o lo
relacionábamos o yo relacionaba las lecturas con lo que los TS hacían allá en ese hospital, pues se me
hizo como que, como el poder que tiene una persona para guiar a otras personas en momentos difíciles
o para que puedan como ver diferentes perspectivas, entonces, creo que ahorita mi visión de TS ha
cambiado de cuando entré a ahorita, siento que lo veo más como oportunidades.
JC: Brian, ¿cuál piensas que es la relevancia de un TS en la sociedad?
BJP: tiene una gran importancia, sin duda alguna, tiene un papel muy muy importante porque, uno debe
de voltear ver más a los trabajadores, bueno, a las trabajadoras y trabajadores, ya que la carrera tiene,
no sé cómo explicarlo, un gran papel, sin duda alguna, es que no sé cómo explicarlo, ahora sí que, sin
nosotras sin nosotros, pues habría cosas que seguirían estando mal, y por esas mismas intervenciones,
en algunos aspectos hemos podido mejorar.
JC: Mariel, ¿cuál consideras tú que es la relevancia del TS para la sociedad?
MJS: pues es que nosotros somos de cierto modo, unas guías y de cierto modo encaminamos a que la
población se empodere y vele por sus intereses y necesidades para que se les pueda dar una solución y
puedan ser escuchados a partir de los recursos que ellos tengan disponibles o que se les puedan brindar
de algún otro modo. Y nosotros, el estarlos guiando como que les da un apoyo porque ven que nos
estamos interesando en ellos, en que también tenemos interés, pues ellos también, está en sus manos el
hacer el cambio. Porque, ya ve que uno empieza a hacer una cosa, y el otro ya lo copia, juntos, pues
salen adelante, entonces yo creo que sí es como nuestra importancia como TS, que juntos vamos como
reactivando ciertos tejidos sociales que se han ido rompiendo, por falta de cultura, muchas veces se va
perdiendo o por este sentido de desarraigo, entonces creo que también en ese aspecto influimos, de
cierto modo.
JC: Brian, ¿qué te gustaría hacer como TS?
BJP: ¿Especializarme?... Sin duda alguna, más en este semestre me he abierto los ojos, en ya trabajar con
niñas y niños, me gustaría poder ayudar mucho en esa cuestión
JC: ¿Cuál sería tu aportación? ¿Cómo te proyectas?
BJP: pues, no estoy seguro, a qué dedicarme específicamente, así como ejemplo… tengo estos dos
ejemplos porque han sido mis profesoras, la profesora Gaby en el pasado trabajó en el DIF y que ese es
un ejemplo y otro, la profesora Canela que ella trabaja con niños, pero en el sector salud, pues no sabría
bien en qué sector, creo que aportar un poco en todos
JC: Mariel, en tu caso, ¿consideras que vas a continuar en esta carrera y qué te gustaría hacer como TS?
MJS: sí consideré cambiarme, pero tampoco quedé… tal vez ahora me gustaría en el sector de la salud
como enfocarme, pero también estoy como en este sector del campo, como de comunidad, como que no
me gusta mucho estar en una oficina, entonces también me gustaría especializarme en esto del campo,
interactuar más con las personas, también digo que en el hospital se hace, pues igual más al aire libre
JC: Brian, ¿algo que me quieras compartir que no haya preguntado sobre alguna motivación o algo?
BJP: no, creo que no, no tengo una motivación o alguien específico en el pasado que me haya o así. Pero
por ejemplo, esto de los animalitos se lo aprendí a mi papá, ya que hasta la actualidad mi papá animalito
que encuentra en la calle, lo adopta o le busca hogar, entonces esta situación del pasado y que le aprendí
a él fue lo que me motivó en general a las personas a ayudar, por decir a mi grupo de amigos y amigas,
pues como que también me gusta apoyarles en lo que pueda, obviamente, y si no puedo apoyarlas o
apoyarlos, pues ayudarlas y ayudarlos a buscar la ayuda que necesitan. Gracias a esas dos cuestiones fue
que me motivé a entrar a TS
JC: Mariel, ¿algo que quisieras compartir que no hayas dicho o no te haya preguntado?
MJS: no, creo que de mi parte es todo.
"""

# ===================== CATEGORÍAS (EDITABLES) =====================
st.sidebar.header("🧩 Diccionario de categorías")
st.sidebar.markdown("Formato: `Categoría: palabra1, palabra2, ...` (puedes editar)")

default_cats = """\
Motivación personal: motivó, motivación, vocación, aportar, granito de arena
Intereses académicos: materia, lecturas, plan de estudios, teoría, estadística
Trabajo comunitario: comunidad, maíz, derechos, traductores, tejido social
Sector salud: hospital, salud, pacientes, sector salud
Proyección profesional: especializarme, proyección, futuro, DIF, niños, niñas
Dificultades y retos: complejo, difícil, adaptarme, reto
Valores prosociales: ayudar, apoyo, adoptar, buscar hogar, solidaridad
Relevancia del TS: importancia, papel, guiar, empoderarse, intervenir
Preferencia de contexto laboral: oficina, campo, aire libre
"""

cats_text = st.sidebar.text_area("Categorías y palabras clave", value=default_cats, height=240)

def parse_categories(txt: str):
    cats = {}
    for line in txt.strip().split("\n"):
        if ":" in line:
            cat, kws = line.split(":", 1)
            kw_list = [w.strip().lower() for w in kws.split(",") if w.strip()]
            if cat.strip():
                cats[cat.strip()] = kw_list
    return cats

CATS = parse_categories(cats_text)

# ===================== PARSE DE TURNOS =====================
pat = r"^([A-ZÁÉÍÓÚÑ]{1,5}):\s*(.+)$"
turnos = []
for line in TRANSCRIPCION.splitlines():
    line = line.strip()
    if not line:
        continue
    m = re.match(pat, line)
    if m:
        spk = m.group(1).strip()
        utt = m.group(2).strip()
        turnos.append({"Hablante": spk, "Texto": utt})
    else:
        if turnos:
            turnos[-1]["Texto"] += " " + line

df = pd.DataFrame(turnos)
if df.empty:
    st.error("No se detectaron turnos con el patrón `INICIALES: texto`.")
    st.stop()

# ===================== FUNCS DE CODIFICACIÓN AUTOMÁTICA =====================
def sugerir_oraciones(texto: str, kws, max_len=280):
    if not isinstance(texto, str):
        return []
    sents = re.split(r"(?<=[.!?])\s+", texto.strip())
    outs = []
    for s in sents:
        s_low = s.lower()
        if any(kw in s_low for kw in kws):
            frag = s.strip()
            if len(frag) > max_len:
                frag = frag[:max_len].rstrip() + "…"
            if frag and frag not in outs:
                outs.append(frag)
    return outs

def codificar_df(df, cats_dict):
    # Devuelve dos estructuras:
    # 1) cod_long: filas (turno, hablante, categoria, extractos)
    # 2) cod_wide: matriz por categoria + extractos
    long_rows = []
    wide_rows = []

    for i, row in df.iterrows():
        texto = row["Texto"]
        habl = row["Hablante"]
        wide_entry = {"TurnoIndex": i, "Hablante": habl, "TextoCompleto": texto}

        for cat, kws in cats_dict.items():
            ext = sugerir_oraciones(texto, kws)
            wide_entry[f"{cat}_flag"] = 1 if len(ext) > 0 else 0
            wide_entry[f"{cat}_extractos"] = " || ".join(ext) if ext else ""

            if ext:
                long_rows.append({
                    "TurnoIndex": i,
                    "Hablante": habl,
                    "Categoría": cat,
                    "Extractos": " || ".join(ext),
                    "TextoCompleto": texto
                })

        wide_rows.append(wide_entry)

    return pd.DataFrame(long_rows), pd.DataFrame(wide_rows)

cod_long, cod_wide = codificar_df(df, CATS)

# ===================== FILTROS UI =====================
st.header("🎚️ Filtros")
colf1, colf2, colf3 = st.columns([1,1,2])
with colf1:
    hablantes = ["(Todos)"] + sorted(df["Hablante"].unique().tolist())
    f_spk = st.selectbox("Hablante", hablantes)
with colf2:
    f_kw = st.text_input("Palabra clave en texto")
with colf3:
    f_cat = st.selectbox("Categoría", ["(Todas)"] + list(CATS.keys()))

filtered = df.copy()
if f_spk != "(Todos)":
    filtered = filtered[filtered["Hablante"] == f_spk]
if f_kw.strip():
    mask = filtered["Texto"].str.contains(f_kw, case=False, na=False)
    filtered = filtered[mask]

st.success(f"Turnos filtrados: {len(filtered)}")

# ===================== VISTA: EXTRACTOS POR CATEGORÍA =====================
st.header("🧠 Extractos agrupados por categoría (sobre el filtro actual)")
if f_cat == "(Todas)":
    cats_to_show = list(CATS.keys())
else:
    cats_to_show = [f_cat]

for cat in cats_to_show:
    # unir con cod_wide para filtrar por turno
    merged = cod_wide.merge(filtered[["Hablante", "Texto"]], left_on="TextoCompleto", right_on="Texto", how="inner")
    cat_rows = merged[merged[f"{cat}_flag"] == 1]
    with st.expander(f"📂 {cat} — {len(cat_rows)} coincidencias"):
        for _, r in cat_rows.iterrows():
            habl = r["Hablante_x"]  # de cod_wide
            exts = r[f"{cat}_extractos"]
            st.markdown(f"**{habl}:**")
            for frag in exts.split("||"):
                frag = frag.strip()
                if frag:
                    st.markdown(f"- “{frag}”")

# ===================== RESUMEN GRÁFICO =====================
st.header("📊 Conteo de categorías (sobre el filtro actual)")
counts = []
for cat in CATS.keys():
    merged = cod_wide.merge(filtered[["Texto"]], left_on="TextoCompleto", right_on="Texto", how="inner")
    counts.append({"Categoría": cat, "Frecuencia": int(merged[f"{cat}_flag"].sum())})
summary = pd.DataFrame(counts).sort_values("Frecuencia", ascending=False)

fig, ax = plt.subplots()
ax.barh(summary["Categoría"], summary["Frecuencia"])
ax.set_xlabel("Frecuencia")
ax.invert_yaxis()
st.pyplot(fig)

# ===================== EXPORTACIÓN =====================
st.header("📦 Exportar análisis")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Formato largo (turno–categoría–extractos)")
    st.dataframe(cod_long, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (largo)",
        data=cod_long.to_csv(index=False).encode("utf-8-sig"),
        file_name="entrevista_codificacion_largo.csv",
        mime="text/csv"
    )
with c2:
    st.subheader("Formato ancho (matriz + extractos por categoría)")
    st.dataframe(cod_wide, use_container_width=True, height=260)
    st.download_button(
        "⬇️ Descargar CSV (ancho)",
        data=cod_wide.to_csv(index=False).encode("utf-8-sig"),
        file_name="entrevista_codificacion_matriz.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Dashboard cualitativo embebido • Edita categorías en el sidebar para ajustar el análisis.")
