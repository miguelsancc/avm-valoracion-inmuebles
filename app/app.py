"""Valoración explicada de vivienda en Madrid.

Aplicación del apartado 10 del TFM. No entrena nada: carga los artefactos
serializados por los notebooks 02 y 03, compone la fila de entrada, predice con
los dos modelos y descompone cada valoración en la contribución de sus
características.

La interfaz se organiza en una portada y tres secciones, navegables desde la
barra superior. El formulario vive en la barra lateral y acompaña a todas, de
modo que un cambio en la vivienda actualiza a la vez la valoración y su
contraste.

Ejecución local desde la raíz del repositorio:
    streamlit run app/app.py
"""

import html
import sys
from pathlib import Path

# La app se ejecuta desde app/, pero los artefactos y el módulo de preprocesado
# viven en la raíz. Se resuelve por __file__ y no por el directorio de trabajo,
# que Streamlit Cloud no garantiza cuál es.
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib

matplotlib.use("Agg")   # sin servidor gráfico: debe fijarse antes de pyplot

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ARTEFACTOS = RAIZ / "modelos"

# --------------------------------------------------------------------------- #
# Constantes de presentación
# --------------------------------------------------------------------------- #

AZUL = "#1f4e79"       # acento principal: cifras, negritas y encabezados
FONDO = "#eef3f8"      # fondo de tarjetas y encabezados de tabla
VERDE = "#2e7d32"
ROJO = "#c62828"
GRIS = "#546e7a"
N_CASCADA = 8          # contribuciones que se detallan antes del agregado «resto»

st.set_page_config(
    page_title="Valoración explicada de vivienda · Madrid",
    page_icon="🏢",
    layout="wide",
)

# Estilos propios. Streamlit no ofrece tarjetas de indicador con el peso visual
# que pide un cuadro de mando, ni permite dar formato al encabezado de
# `st.dataframe`, que se dibuja sobre un lienzo y no responde a CSS.
st.html(f"""
<style>
  /* ---- tarjetas de indicador ---- */
  .kpi-fila {{ display:flex; gap:.85rem; flex-wrap:wrap; margin:.35rem 0 1.2rem 0; }}
  .kpi {{ flex:1 1 160px; background:{FONDO}; border-radius:.55rem;
          padding:1rem .85rem; text-align:center; }}
  .kpi .cifra {{ font-size:1.95rem; font-weight:700; color:{AZUL};
                 line-height:1.15; }}
  .kpi .rotulo {{ font-size:.68rem; font-weight:700; color:#5a6b7b;
                  text-transform:uppercase; letter-spacing:.05em;
                  margin-top:.35rem; }}
  .kpi .apunte {{ font-size:.71rem; color:#8793a0; margin-top:.2rem; }}

  /* ---- cabecera de la portada ---- */
  .portada {{ text-align:center; padding:1.7rem 0 .6rem 0; }}
  .portada .regleta {{ width:64px; height:3px; background:{AZUL};
                       margin:0 auto 1.2rem auto; }}
  .portada .antetitulo {{ font-size:.76rem; font-weight:700; color:{AZUL};
                          text-transform:uppercase; letter-spacing:.15em; }}
  .portada h1 {{ font-size:3.15rem; font-weight:700; margin:.45rem 0 .3rem 0;
                 line-height:1.1; }}
  .portada .fecha {{ color:#7a8794; font-size:.98rem; }}

  /* ---- tarjetas de seccion: el recuadro entero es clicable ----
     `st.page_link` genera un enlace de navegacion de cliente; se estira
     invisible sobre toda la tarjeta para no recargar la pagina, que
     reiniciaria el formulario. */
  div[class*="st-key-tarjeta"] {{
      position:relative; border-radius:.6rem; cursor:pointer;
      padding:.85rem 1rem !important; gap:.15rem !important;
      transition:box-shadow .16s ease, transform .16s ease, border-color .16s ease;
  }}
  div[class*="st-key-tarjeta"] .stCaption p,
  div[class*="st-key-tarjeta"] [data-testid="stCaptionContainer"] p {{
      margin-bottom:0; line-height:1.35;
  }}
  div[class*="st-key-tarjeta"]:hover {{
      box-shadow:0 6px 18px rgba(31,78,121,.18);
      transform:translateY(-3px);
      border-color:{AZUL} !important;
  }}
  /* Streamlit envuelve cada elemento en un contenedor `relative` que colapsa
     a altura cero; mientras lo sea, el enlace absoluto se dimensiona respecto
     de el y no de la tarjeta. Se neutraliza solo en el que lleva el enlace. */
  div[class*="st-key-tarjeta"] .stElementContainer:has(.stPageLink),
  div[class*="st-key-tarjeta"] .stPageLink,
  div[class*="st-key-tarjeta"] .stPageLink > div {{ position:static !important; }}
  div[class*="st-key-tarjeta"] a[data-testid="stPageLink-NavLink"] {{
      position:absolute !important;
      top:0 !important; right:0 !important; bottom:0 !important; left:0 !important;
      width:auto !important; height:auto !important;
      opacity:0; z-index:5;
  }}
  .tarjeta-titulo {{ font-size:1.12rem; font-weight:700; color:{AZUL};
                     margin-bottom:.3rem; }}

  /* ---- tabla de contribuciones ---- */
  .caja-tabla {{ max-height:390px; overflow-y:auto; border:1px solid #e3e8ee;
                 border-radius:.45rem; }}
  .tabla-contrib {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  .tabla-contrib thead th {{ background:{FONDO}; font-weight:700; color:{AZUL};
                             text-align:left; padding:.55rem .65rem;
                             position:sticky; top:0; z-index:2; }}
  .tabla-contrib thead th.num {{ text-align:right; }}
  .tabla-contrib td {{ padding:.36rem .65rem; border-bottom:1px solid #eef1f4; }}
  .tabla-contrib td.num {{ text-align:right; font-variant-numeric:tabular-nums;
                           font-weight:600; }}
  .tabla-contrib tbody tr:hover td {{ background:#f7fafc; }}

  /* ---- negritas del cuerpo en azul oscuro ---- */
  section[data-testid="stMain"] .stMarkdown strong {{ color:{AZUL}; }}

  /* ---- todos los rotulos del formulario en negrita ---- */
  section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {{
      font-weight:700;
  }}
</style>
""")


# --------------------------------------------------------------------------- #
# Carga de artefactos
# --------------------------------------------------------------------------- #

@st.cache_resource(show_spinner="Cargando los modelos…")
def cargar():
    """Carga los dos artefactos una sola vez por sesión de servidor.

    Los dos fallos previsibles se distinguen en el mensaje: que el módulo de
    preprocesado no sea importable y que la versión de las librerías no permita
    deserializar los pipelines.
    """
    import joblib

    try:
        import tfm_preprocesado  # noqa: F401  el FunctionTransformer lo referencia
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "MODULO:No se encuentra `tfm_preprocesado.py` en la raíz del "
            "repositorio. El pipeline lineal referencia desde un "
            "`FunctionTransformer` la función `tramificar` que ese módulo "
            "define, de modo que el artefacto no se puede deserializar sin él. "
            f"Se ha buscado en: {RAIZ}"
        ) from exc

    if not ARTEFACTOS.exists():
        raise RuntimeError(
            f"ARCHIVO:No existe la carpeta `modelos/`. Se ha buscado en: "
            f"{ARTEFACTOS}"
        )

    try:
        art = joblib.load(ARTEFACTOS / "avm_madrid.joblib")
        app = joblib.load(ARTEFACTOS / "avm_app.joblib")
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"ARCHIVO:Falta un artefacto en `modelos/`: {exc.filename}. "
            "La aplicación necesita `avm_madrid.joblib` y `avm_app.joblib`."
        ) from exc
    except (AttributeError, ImportError, ModuleNotFoundError, TypeError) as exc:
        import sklearn
        import xgboost

        raise RuntimeError(
            "VERSION:Los artefactos no se han podido deserializar, casi con "
            "seguridad por una diferencia de versiones. Se serializaron con "
            "scikit-learn 1.6.1 y xgboost 3.0.0; el entorno actual tiene "
            f"scikit-learn {sklearn.__version__} y xgboost {xgboost.__version__}. "
            "Fije esas versiones en `requirements.txt`. scikit-learn 1.6.1 "
            "publica wheels hasta Python 3.13 inclusive.\n\n"
            f"Error original: {type(exc).__name__}: {exc}"
        ) from exc

    return art, app


try:
    ART, APP = cargar()
except RuntimeError as exc:
    clase, _, mensaje = str(exc).partition(":")
    titulo = {
        "MODULO": "No se encuentra el módulo de preprocesado",
        "VERSION": "Versiones incompatibles",
        "ARCHIVO": "Faltan los artefactos del modelo",
    }.get(clase, "No se han podido cargar los modelos")
    st.error(f"**{titulo}**\n\n{mensaje}")
    st.stop()

TIPOS = ART["variables_entrada"]              # dict ordenado nombre -> dtype
ORDEN = list(TIPOS)                           # las 35 variables, en orden
PERFIL = APP["perfil_barrio"]
DEFECTO = APP["por_defecto"]
PEDIDAS = APP["variables_pedidas"]
GEO = [c for c in PERFIL.columns
       if c not in ("DISTRITO", "precio_m2_mediano", "n_entrenamiento")]
ETIQUETA = APP["etiquetas_var"]
BLOQUE = APP["bloques"]
ORIGEN = APP["origen_columnas"]
MINIMO, MAXIMO = APP["rango_operativo"]
PIPE = {"xgboost": ART["modelos"]["xgboost"], "lineal": ART["modelos"]["lineal"]}
BARRIOS = sorted(PERFIL.index)


# --------------------------------------------------------------------------- #
# Formato
# --------------------------------------------------------------------------- #

def es(valor, decimales=0):
    """Número con separador de millar y coma decimal."""
    txt = f"{valor:,.{decimales}f}"
    return txt.replace(",", " ").replace(".", ",").replace(" ", ".")


def eur(valor, decimales=0):
    return f"{es(valor, decimales)} €"


def legible(variable, valor):
    """Valor de una variable en la forma en que debe leerlo un analista."""
    # Seis de los 135 barrios no tienen valor propio de superficie ni de
    # antigüedad medias. El pipeline las imputa por la mediana del conjunto,
    # y la tabla debe decirlo en lugar de mostrar un valor que no existe.
    if pd.isna(valor):
        return "Sin dato (imputado)"
    if variable.startswith(("HAS", "IS")) or variable.startswith("BUILTTYPEID"):
        return "Sí" if float(valor) == 1 else "No"
    if variable == "DISTRITO":
        return f"Distrito {valor}"
    if variable == "FLATLOCATIONID":
        return {1.0: "Exterior", 2.0: "Interior"}.get(float(valor), "No declarado")
    if variable.startswith("DISTANCE_TO"):
        return f"{es(float(valor), 2)} km"
    if variable == "CONSTRUCTEDAREA":
        return f"{es(float(valor))} m²"
    if variable in ("CADCONSTRUCTIONYEAR", "BARRIO_ANTIGUEDAD_MED"):
        return f"{int(valor)}"
    if variable == "BARRIO_AREA_MED":
        return f"{es(float(valor))} m²"
    if float(valor) == int(float(valor)):
        return es(float(valor))
    return es(float(valor), 2)


def kpis(tarjetas):
    """Fila de tarjetas de indicador.

    tarjetas: lista de (cifra, rótulo, apunte o None)
    """
    piezas = []
    for cifra, rotulo, apunte in tarjetas:
        extra = f'<div class="apunte">{html.escape(apunte)}</div>' if apunte else ""
        piezas.append(
            f'<div class="kpi"><div class="cifra">{html.escape(cifra)}</div>'
            f'<div class="rotulo">{html.escape(rotulo)}</div>{extra}</div>'
        )
    st.html(f'<div class="kpi-fila">{"".join(piezas)}</div>')


# --------------------------------------------------------------------------- #
# Composición de la entrada y valoración
# --------------------------------------------------------------------------- #

def componer(barrio, respuestas):
    """DataFrame de una fila con las 35 columnas, en orden y con su tipo.

    Tres fuentes sin solapamiento: las 9 del formulario, las 7 geoespaciales
    más el distrito que aporta el barrio elegido, y las 18 restantes fijadas en
    su valor típico de entrenamiento.
    """
    fila = dict(DEFECTO)
    perfil = PERFIL.loc[barrio]
    fila.update({c: perfil[c] for c in GEO})
    fila["DISTRITO"] = perfil["DISTRITO"]
    fila.update({v: respuestas[v] for v in PEDIDAS})

    X = pd.DataFrame([[fila[v] for v in ORDEN]], columns=ORDEN)
    for variable, tipo in TIPOS.items():
        X[variable] = X[variable].astype(tipo)
    return X


def valorar(X, modelo):
    """Los dos pipelines predicen el logaritmo natural del precio."""
    return float(np.exp(PIPE[modelo].predict(X))[0])


# --------------------------------------------------------------------------- #
# Descomposición de la valoración
# --------------------------------------------------------------------------- #

def _contribuciones(X, modelo):
    """Contribución de cada columna del preprocesado, en logaritmos, y base."""
    pipe = PIPE[modelo]
    Z = pipe.named_steps["preproceso"].transform(X)
    columnas = list(ORIGEN[modelo])

    if modelo == "xgboost":
        # Valores SHAP por la implementación nativa del booster: mismo
        # algoritmo que la librería `shap`, sin la dependencia y mucho más
        # rápido. La última posición es el valor base.
        from xgboost import DMatrix

        booster = pipe.named_steps["regresion"].get_booster()
        contrib = booster.predict(DMatrix(Z), pred_contribs=True)[0]
        return pd.Series(contrib[:-1], index=columnas), float(contrib[-1])

    # En el lineal la contribución de cada columna es coef_j * z_j y el valor
    # base es el término independiente.
    reg = pipe.named_steps["regresion"]
    return pd.Series(reg.coef_ * Z[0], index=columnas), float(reg.intercept_)


@st.cache_data(show_spinner=False)
def descomponer(X, modelo):
    """Descomposición agregada a las 35 variables originales y en euros.

    La descomposición es aditiva en logaritmos y por tanto multiplicativa en
    euros: el efecto porcentual de cada variable no depende del orden, pero su
    traducción a euros sí. Convención: acumulación sucesiva en orden decreciente
    de magnitud.
    """
    columnas, base = _contribuciones(X, modelo)
    log_pred = float(PIPE[modelo].predict(X)[0])

    # XGBoost predice en precisión simple: se exige tolerancia relativa, no
    # igualdad.
    assert np.isclose(base + columnas.sum(), log_pred, rtol=1e-4), (
        f"La descomposición de {modelo} no reproduce la predicción"
    )

    # Agregación exacta: sumar las columnas del preprocesado que proceden de la
    # misma variable original.
    agregada = (columnas.groupby(pd.Series(ORIGEN[modelo])).sum()
                .reindex(ORDEN).fillna(0.0))
    agregada = agregada.reindex(agregada.abs().sort_values(ascending=False).index)

    valor, importes = float(np.exp(base)), []
    for contribucion in agregada:
        nuevo = valor * np.exp(contribucion)
        importes.append(nuevo - valor)
        valor = nuevo

    tabla = pd.DataFrame({
        "variable": agregada.index,
        "Característica": [ETIQUETA[v] for v in agregada.index],
        "Valor": [legible(v, X[v].iloc[0]) for v in agregada.index],
        "Bloque": [BLOQUE[v] for v in agregada.index],
        "log": agregada.values,
        "Efecto": (np.exp(agregada.values) - 1) * 100,
        "Importe": importes,
    })
    return tabla, float(np.exp(base)), float(np.exp(log_pred))


def pasos_cascada(tabla):
    """Las N mayores contribuciones más un agregado con el resto."""
    cabeza, cola = tabla.head(N_CASCADA), tabla.tail(len(tabla) - N_CASCADA)
    pasos = [(r["Característica"], r["Efecto"], r["Importe"])
             for _, r in cabeza.iterrows()]
    if len(cola):
        log_resto = cola["log"].sum()
        pasos.append((f"Resto de variables ({len(cola)})",
                      (np.exp(log_resto) - 1) * 100, cola["Importe"].sum()))
    return pasos


def grafico_cascada(pasos, base, valoracion, titulo_base, titulo_final):
    """Cascada horizontal: arranca en el valor de referencia del modelo,
    encadena las contribuciones y cierra en la valoración.

    Compacta a propósito: se muestra a tamaño natural, sin estirarse al ancho
    del contenedor, para que no domine visualmente sobre los indicadores.
    """
    etiquetas = [titulo_base] + [p[0] for p in pasos] + [titulo_final]
    n = len(etiquetas)
    fig, ax = plt.subplots(figsize=(5.9, 0.245 * n + 0.6), dpi=115)

    acumulado = base
    for i, etiqueta in enumerate(etiquetas):
        y = n - 1 - i
        if i == 0 or i == n - 1:
            valor = base if i == 0 else valoracion
            ax.barh(y, valor, color=GRIS, height=0.6, zorder=3)
            ax.text(valor, y, f"  {eur(valor)}", va="center", ha="left",
                    fontsize=5.8, color=GRIS, fontweight="bold", zorder=4)
        else:
            _, _, importe = pasos[i - 1]
            inicio = acumulado
            acumulado += importe
            ax.barh(y, importe, left=inicio, height=0.6, zorder=3,
                    color=VERDE if importe >= 0 else ROJO)
            extremo = max(inicio, acumulado)
            ax.text(extremo, y, f"  {'+' if importe >= 0 else '−'}"
                                f"{es(abs(importe))} €",
                    va="center", ha="left", fontsize=5.8,
                    color=VERDE if importe >= 0 else ROJO, zorder=4)

    ax.set_yticks(range(n))
    ax.set_yticklabels(etiquetas[::-1], fontsize=6.2)
    ax.set_xlim(0, max(base, valoracion, acumulado) * 1.30)
    ax.set_xlabel("Euros", fontsize=6.2)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: es(v)))
    ax.tick_params(axis="x", labelsize=5.5)
    ax.grid(axis="x", alpha=0.25, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    return fig


def tabla_contribuciones(tabla):
    """Tabla en HTML propio.

    `st.dataframe` dibuja sobre un lienzo y no admite formato en el
    encabezado, que es lo que aquí se necesita.
    """
    filas = []
    for _, r in tabla.iterrows():
        signo_e = "+" if r["Efecto"] >= 0 else "−"
        signo_i = "+" if r["Importe"] >= 0 else "−"
        color = VERDE if r["Importe"] >= 0 else ROJO
        filas.append(
            "<tr>"
            f"<td>{html.escape(str(r['Característica']))}</td>"
            f"<td>{html.escape(str(r['Valor']))}</td>"
            f"<td>{html.escape(str(r['Bloque']))}</td>"
            f"<td class='num' style='color:{color}'>"
            f"{signo_e}{es(abs(r['Efecto']), 2)} %</td>"
            f"<td class='num' style='color:{color}'>"
            f"{signo_i}{es(abs(r['Importe']))} €</td>"
            "</tr>"
        )
    st.html(
        '<div class="caja-tabla"><table class="tabla-contrib"><thead><tr>'
        '<th>Característica</th><th>Valor</th><th>Bloque</th>'
        '<th class="num">Efecto</th><th class="num">Importe</th>'
        f'</tr></thead><tbody>{"".join(filas)}</tbody></table></div>'
    )


def mostrar_cascada(tabla, base, valoracion, titulo_base, titulo_final):
    """Cascada y tabla de detalle, ambas plegadas."""
    with st.expander("Ver el gráfico de cascada", icon=":material/bar_chart:"):
        figura = grafico_cascada(pasos_cascada(tabla), base, valoracion,
                                 titulo_base, titulo_final)
        st.pyplot(figura, use_container_width=False)
        plt.close(figura)
        st.caption(
            "El efecto en porcentaje de cada característica no depende del "
            "orden en que se consideren, porque la descomposición es aditiva "
            "en logaritmos. Su traducción a euros sí: se obtiene por "
            "acumulación sucesiva en orden decreciente de magnitud, que es la "
            "convención que emplea esta herramienta."
        )

    with st.expander("Ver la contribución de las 35 características",
                     icon=":material/table_rows:"):
        tabla_contribuciones(tabla)


# --------------------------------------------------------------------------- #
# Formulario: vive en la barra lateral y acompaña a todas las secciones
# --------------------------------------------------------------------------- #

st.sidebar.title("Características de la vivienda")

barrio = st.sidebar.selectbox(
    "Barrio", BARRIOS,
    index=BARRIOS.index("Acacias") if "Acacias" in BARRIOS else 0,
    help=APP["metadatos"]["nota_geoespacial"])

superficie = st.sidebar.number_input(
    "Superficie construida (m²)", min_value=20, max_value=950, value=82, step=1)
dormitorios = st.sidebar.number_input(
    "Dormitorios", min_value=0, max_value=10, value=3, step=1,
    help="A superficie constante, más dormitorios implica estancias menores, "
         "lo que el mercado penaliza.")
banos = st.sidebar.number_input(
    "Baños", min_value=1, max_value=8, value=1, step=1)
planta = st.sidebar.number_input(
    "Planta", min_value=0, max_value=25, value=2, step=1,
    help="0 corresponde a la planta baja.")
anio = st.sidebar.number_input(
    "Año de construcción", min_value=1900, max_value=2018, value=1967, step=1)

st.sidebar.markdown("**Equipamiento**")
col_a, col_b = st.sidebar.columns(2)
ascensor = col_a.checkbox("Ascensor", value=True)
garaje = col_b.checkbox("Garaje", value=False)
terraza = col_a.checkbox("Terraza", value=False)
aire = col_b.checkbox("Aire acondicionado", value=False)

st.sidebar.caption(
    "El resto de características se fijan en su valor típico del mercado "
    "madrileño, y la localización se aproxima por la mediana del barrio."
)

RESPUESTAS = {
    "CONSTRUCTEDAREA": superficie,
    "ROOMNUMBER": dormitorios,
    "BATHNUMBER": banos,
    "FLOORCLEAN": planta,
    "CADCONSTRUCTIONYEAR": anio,
    "HASLIFT": int(ascensor),
    "HASPARKINGSPACE": int(garaje),
    "HASTERRACE": int(terraza),
    "HASAIRCONDITIONING": int(aire),
}

X = componer(barrio, RESPUESTAS)
PERFIL_BARRIO = PERFIL.loc[barrio]
TABLA_XGB, BASE_XGB, VALORACION = descomponer(X, "xgboost")


# --------------------------------------------------------------------------- #
# Secciones
# --------------------------------------------------------------------------- #

def _tarjeta_seccion(columna, clave, titulo, descripcion):
    """Tarjeta de acceso. El enlace se estira invisible sobre todo el recuadro,
    de modo que basta con pulsar en cualquier punto."""
    with columna.container(border=True, height=124, key=f"tarjeta_{clave}"):
        st.html(f'<div class="tarjeta-titulo">{html.escape(titulo)}</div>')
        st.caption(descripcion)
        st.page_link(PAGINAS[clave], label=titulo)


def portada():
    meta = ART["metadatos"]
    metricas = ART["metricas"]["XGBoost"]

    st.html(
        '<div class="portada">'
        '<div class="regleta"></div>'
        '<div class="antetitulo">Modelo de tasación</div>'
        '<h1>Valoración explicada de vivienda</h1>'
        f'<div class="fecha">{html.escape(meta["ambito"])}</div>'
        '</div>'
    )

    kpis([
        (f"{es(metricas['MdAPE (%)'], 2)} %", "Error relativo mediano",
         "La mitad se desvía menos de esa cifra (MdAPE)"),
        (f"{es(metricas['PE10 (%)'], 1)} %", "Valoraciones dentro del ±10 %",
         "del precio observado (PE10)"),
        (f"{es(metricas['PE20 (%)'], 1)} %", "Valoraciones dentro del ±20 %",
         "del precio observado (PE20)"),
        (es(metricas["COD"], 2), "Coeficiente de dispersión",
         "Umbral IAAO de consistencia: 15"),
        (es(meta["n_validacion"]), "Viviendas de validación",
         "ajenas por completo al ajuste"),
    ])

    st.markdown(
        "Herramienta de contraste para el análisis de riesgo de garantías "
        "hipotecarias. Estima el precio de anuncio de una vivienda en Madrid a "
        "partir de diez características y descompone cada valoración en la "
        "contribución exacta de cada una, de modo que una discrepancia frente "
        "a una tasación recibida pueda atribuirse a un factor concreto."
    )

    st.divider()

    uno, dos, tres = st.columns(3)
    _tarjeta_seccion(uno, "valoracion", "Valoración estimada",
                     "La valoración del modelo y su descomposición "
                     "característica a característica.")
    _tarjeta_seccion(dos, "contraste", "Contraste con el modelo interpretable",
                     "La valoración de la regresión lineal y la diferencia "
                     "frente al modelo principal.")
    _tarjeta_seccion(tres, "modelo", "Sobre el modelo",
                     "Rendimiento sobre el conjunto de validación y "
                     "limitaciones de alcance.")

    st.caption(
        "Los indicadores corresponden al modelo de alto rendimiento medido "
        f"sobre {es(meta['n_validacion'])} viviendas que no intervinieron en "
        "el ajuste. La valoración estima el precio de anuncio a diciembre de "
        "2018 y no sustituye a una tasación profesional."
    )


def pagina_valoracion():
    st.title("Valoración estimada")

    unitario = VALORACION / superficie
    referencia = float(PERFIL_BARRIO["precio_m2_mediano"])
    desvio = (unitario / referencia - 1) * 100

    kpis([
        (eur(VALORACION), "Valoración estimada", "Precio de anuncio, dic. 2018"),
        (f"{es(unitario)} €", "Precio por metro cuadrado",
         f"sobre {es(superficie)} m² construidos"),
        (f"{es(referencia)} €", "Mediana del barrio",
         f"{'+' if desvio >= 0 else '−'}{es(abs(desvio), 1)} % respecto de ella"),
        (es(int(PERFIL_BARRIO["n_entrenamiento"])), "Muestra del barrio",
         f"{barrio} · distrito {PERFIL_BARRIO['DISTRITO']}"),
    ])

    st.markdown(
        "**Precio de anuncio a diciembre de 2018.** No es el valor de mercado "
        "actual: el modelo se calibró sobre anuncios del cuarto trimestre de "
        "2018 y el nivel general de precios ha variado de forma apreciable "
        "desde entonces."
    )

    if not MINIMO <= VALORACION <= MAXIMO:
        st.warning(
            f"**La valoración queda fuera del rango operativo del modelo** "
            f"({eur(MINIMO)} – {eur(MAXIMO)}). Fuera de esa banda el modelo "
            f"pierde fiabilidad: la proporción de valoraciones dentro del 10 % "
            f"cae al 42,8 % y al 47,2 % en los deciles extremos de precio, "
            f"frente al 55-61 % de los centrales. Esta valoración requiere "
            f"revisión profesional."
        )

    if int(PERFIL_BARRIO["n_entrenamiento"]) < 30:
        st.info(
            f"**Barrio con muestra reducida.** {barrio} aporta solo "
            f"{es(int(PERFIL_BARRIO['n_entrenamiento']))} viviendas al "
            f"entrenamiento, de modo que su perfil de localización está peor "
            f"estimado que el de un barrio con varios centenares. Conviene "
            f"contrastar el resultado."
        )
    if PERFIL_BARRIO[GEO].isna().any():
        ausentes = [ETIQUETA[c] for c in GEO if pd.isna(PERFIL_BARRIO[c])]
        st.info(
            f"**Perfil de barrio incompleto.** En {barrio} no hay valor propio "
            f"para {' ni '.join(ausentes).lower()}; el modelo las sustituye "
            f"por la mediana del conjunto de Madrid."
        )

    st.divider()

    st.subheader(
        "De qué se compone la valoración",
        help="La descomposición se obtiene por valores SHAP, que reparten la "
             "valoración entre las características atribuyendo a cada una su "
             "contribución exacta. El valor de referencia del modelo es la "
             "valoración media sobre las viviendas de entrenamiento.",
    )
    st.markdown(
        f"La cascada parte del valor de referencia del modelo, "
        f"**{eur(BASE_XGB)}**, encadena las ocho contribuciones de mayor "
        f"magnitud y cierra en la valoración."
    )
    mostrar_cascada(TABLA_XGB, BASE_XGB, VALORACION,
                    "Valor de referencia del modelo", "Valoración")


def pagina_contraste():
    st.title("Contraste con el modelo interpretable")

    tabla_lin, base_lin, valoracion_lin = descomponer(X, "lineal")
    diferencia = VALORACION - valoracion_lin
    relativa = diferencia / valoracion_lin * 100

    kpis([
        (eur(VALORACION), "Modelo de alto rendimiento", "XGBoost"),
        (eur(valoracion_lin), "Modelo interpretable", "Regresión lineal (OLS)"),
        (f"{'+' if diferencia >= 0 else '−'}{es(abs(diferencia))} €",
         "Discrepancia entre ambos",
         f"{'+' if relativa >= 0 else '−'}{es(abs(relativa), 1)} % "
         f"sobre el interpretable"),
    ])

    # La discrepancia se informa, pero no se interpreta como señal de
    # fiabilidad. Medido sobre las 6.284 viviendas de validación, su
    # correlación de Spearman con el error del modelo es 0,038: el error
    # relativo mediano se mantiene entre el 8,5 % y el 9,6 % del primer al
    # quinto quintil de discrepancia, mientras la discrepancia se multiplica
    # por catorce. Avisar de que una valoración requiere revisión porque los
    # dos modelos difieren sería engañar al analista.
    st.markdown(
        "La discrepancia entre los dos modelos **no anticipa el error de la "
        "valoración**.",
        help="Sobre las 6.284 viviendas de validación su correlación con el "
             "error es de 0,038, y el error relativo mediano apenas se mueve "
             "entre el 8,5 % y el 9,6 % aunque la discrepancia se multiplique "
             "por catorce. Por eso esta sección informa de la diferencia pero "
             "no recomienda revisión a partir de ella.",
    )
    st.markdown(
        "El modelo interpretable es una regresión lineal sobre los mismos "
        "datos. Se muestra como contraste, no como alternativa: el apartado 8 "
        "del trabajo concluye que el modelo de alto rendimiento es preferible, "
        "y la valoración que ofrece esta herramienta es la suya."
    )

    st.divider()

    st.subheader("De qué se compone la valoración lineal")
    st.markdown(
        "**Las dos cascadas no son comparables paso a paso**, porque parten de "
        "bases distintas.",
        help=(
            "La del modelo de alto rendimiento arranca en la valoración media "
            f"del entrenamiento ({eur(BASE_XGB)}). La del modelo lineal "
            f"arranca en el término independiente de la regresión "
            f"({eur(base_lin)}), que es la valoración de una vivienda de "
            "referencia concreta: obra nueva, exterior, en el distrito "
            "Centro, a menos de 1,5 km del centro, a menos de 1 km de la "
            "Castellana, a menos de 200 m de una estación de metro, anterior "
            "a 1955 y con el resto de características en su valor medio. Cada "
            "contribución mide la separación respecto de esa vivienda, no "
            "respecto de la media del mercado."
        ),
    )
    mostrar_cascada(tabla_lin, base_lin, valoracion_lin,
                    "Vivienda de referencia", "Valoración lineal")


def pagina_modelo():
    st.title("Sobre el modelo")

    meta = ART["metadatos"]
    st.markdown(
        f"Ámbito: **{meta['ambito']}**. Modelo calibrado sobre "
        f"**{es(meta['n_entrenamiento'])} viviendas** y validado sobre otras "
        f"**{es(meta['n_validacion'])}** que no intervinieron en el ajuste. "
        f"La estimación es la **{meta['estimacion']}**."
    )

    st.subheader("Rendimiento sobre las viviendas de validación")
    NOMBRES = {
        "Ref. barrio (135)": "Superficie × precio del barrio",
        "Modelo lineal (OLS)": "Modelo interpretable (OLS)",
        "XGBoost": "Modelo de alto rendimiento (XGBoost)",
    }
    filas = []
    for clave in ("Ref. barrio (135)", "Modelo lineal (OLS)", "XGBoost"):
        m = ART["metricas"][clave]
        filas.append(
            "<tr>"
            f"<td>{NOMBRES[clave]}</td>"
            f"<td class='num'>{es(m['MdAPE (%)'], 2)} %</td>"
            f"<td class='num'>{es(m['PE10 (%)'], 1)} %</td>"
            f"<td class='num'>{es(m['PE20 (%)'], 1)} %</td>"
            f"<td class='num'>{es(m['COD'], 2)}</td>"
            "</tr>"
        )
    st.html(
        '<table class="tabla-contrib"><thead><tr><th>Procedimiento</th>'
        '<th class="num">MdAPE</th><th class="num">PE10</th>'
        '<th class="num">PE20</th><th class="num">COD</th></tr></thead>'
        f'<tbody>{"".join(filas)}</tbody></table>'
    )

    st.caption(
        "MdAPE: error relativo mediano. PE10 y PE20: proporción de "
        "valoraciones comprendidas dentro de un margen del 10 % y del 20 % "
        "respecto del precio observado. "
        "COD: coeficiente de dispersión; el estándar IAAO sitúa el "
        "umbral de consistencia en 15. El modelo de alto rendimiento es el "
        "único de los tres que lo alcanza."
    )

    st.subheader("Limitaciones")
    st.markdown(
        "**Alcance temporal.** El modelo se calibró sobre "
        f"{es(meta['n_entrenamiento'] + meta['n_validacion'])} viviendas "
        "anunciadas en Madrid en el cuarto trimestre de 2018, de modo que "
        "estima el precio de anuncio a diciembre de 2018 y no el valor de "
        "mercado actual. El nivel general de precios ha variado de forma "
        "apreciable desde entonces. Las relaciones que el modelo captura —el "
        "diferencial entre barrios, el valor relativo de cada característica— "
        "envejecen más despacio que el nivel de precios, pero el procedimiento "
        "requeriría recalibración periódica antes de un uso efectivo."
    )
    st.markdown(
        "**Precios de oferta y no de transacción.** Los datos proceden de "
        "anuncios, que incorporan el margen de negociación habitual del "
        "mercado."
    )
    st.markdown(
        "**No sustituye a una tasación profesional** conforme a la normativa "
        "aplicable."
    )


# --------------------------------------------------------------------------- #
# Navegación
# --------------------------------------------------------------------------- #

PAGINAS = {
    "portada": st.Page(portada, title="Portada", icon=":material/home:",
                       url_path="portada", default=True),
    "valoracion": st.Page(pagina_valoracion, title="Valoración estimada",
                          icon=":material/euro:", url_path="valoracion"),
    "contraste": st.Page(pagina_contraste, title="Contraste",
                         icon=":material/compare_arrows:", url_path="contraste"),
    "modelo": st.Page(pagina_modelo, title="Sobre el modelo",
                      icon=":material/info:", url_path="modelo"),
}

st.navigation(list(PAGINAS.values()), position="top").run()
