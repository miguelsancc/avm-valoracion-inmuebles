"""Valoración automatizada de vivienda en Madrid.

Aplicación del apartado 10 del TFM. No entrena nada: carga los artefactos
serializados por los notebooks 02 y 03, compone la fila de entrada, predice con
los dos modelos y descompone cada valoración en la contribución de sus
características.

Ejecución local desde la raíz del repositorio:
    streamlit run app/app.py
"""

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

VERDE = "#2e7d32"
ROJO = "#c62828"
GRIS = "#546e7a"
N_CASCADA = 8          # contribuciones que se detallan antes del agregado «resto»
UMBRAL_DISCREPANCIA = 15.0   # % a partir del cual se recomienda revisión

st.set_page_config(
    page_title="Valoración automatizada de vivienda · Madrid",
    page_icon="🏢",
    layout="wide",
)


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
            "requiere Python 3.12 o anterior.\n\n"
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


def pasos_cascada(tabla, base, valoracion):
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
    encadena las contribuciones y cierra en la valoración."""
    etiquetas = [titulo_base] + [p[0] for p in pasos] + [titulo_final]
    n = len(etiquetas)
    fig, ax = plt.subplots(figsize=(9, 0.46 * n + 1.1))

    acumulado = base
    for i, etiqueta in enumerate(etiquetas):
        y = n - 1 - i
        if i == 0 or i == n - 1:
            valor = base if i == 0 else valoracion
            ax.barh(y, valor, color=GRIS, height=0.62, zorder=3)
            ax.text(valor, y, f"  {eur(valor)}", va="center", ha="left",
                    fontsize=9, color=GRIS, fontweight="bold", zorder=4)
        else:
            _, _, importe = pasos[i - 1]
            inicio = acumulado
            acumulado += importe
            ax.barh(y, importe, left=inicio, height=0.62, zorder=3,
                    color=VERDE if importe >= 0 else ROJO)
            extremo = max(inicio, acumulado)
            ax.text(extremo, y, f"  {'+' if importe >= 0 else '−'}"
                                f"{es(abs(importe))} €",
                    va="center", ha="left", fontsize=9,
                    color=VERDE if importe >= 0 else ROJO, zorder=4)

    ax.set_yticks(range(n))
    ax.set_yticklabels(etiquetas[::-1], fontsize=9.5)
    ax.set_xlim(0, max(base, valoracion, acumulado) * 1.30)
    ax.set_xlabel("Euros", fontsize=9)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: es(v)))
    ax.tick_params(axis="x", labelsize=8.5)
    ax.grid(axis="x", alpha=0.25, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    return fig


def tabla_presentable(tabla):
    salida = tabla[["Característica", "Valor", "Bloque", "Efecto", "Importe"]].copy()
    salida["Efecto"] = salida["Efecto"].map(lambda v: f"{'+' if v >= 0 else '−'}{es(abs(v), 2)} %")
    salida["Importe"] = salida["Importe"].map(lambda v: f"{'+' if v >= 0 else '−'}{es(abs(v))} €")
    return salida


# --------------------------------------------------------------------------- #
# Formulario
# --------------------------------------------------------------------------- #

st.sidebar.title("Características de la vivienda")

barrio = st.sidebar.selectbox("Barrio", BARRIOS,
                              index=BARRIOS.index("Acacias") if "Acacias" in BARRIOS else 0)

superficie = st.sidebar.number_input(
    "Superficie construida (m²)", min_value=20, max_value=950, value=82, step=1)
dormitorios = st.sidebar.number_input(
    "Dormitorios", min_value=0, max_value=10, value=3, step=1)
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
    "madrileño. Las variables de localización se aproximan por la mediana del "
    "barrio: la dispersión interna es reducida en las distancias a referencias "
    "urbanas y apreciable en las de escala local."
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
perfil = PERFIL.loc[barrio]


# --------------------------------------------------------------------------- #
# Resultado principal
# --------------------------------------------------------------------------- #

st.title("Valoración automatizada de vivienda")
st.caption(
    "Herramienta de contraste para análisis de riesgo de garantías "
    "hipotecarias. Madrid, cuarto trimestre de 2018."
)

tabla_xgb, base_xgb, valoracion = descomponer(X, "xgboost")
unitario = valoracion / superficie
referencia = float(perfil["precio_m2_mediano"])

izq, der = st.columns([1.15, 1])

with izq:
    st.metric("Valoración estimada", eur(valoracion))
    st.markdown(
        "**Precio de anuncio a diciembre de 2018.** No es el valor de mercado "
        "actual: el modelo se calibró sobre anuncios del cuarto trimestre de "
        "2018 y el nivel general de precios ha variado de forma apreciable "
        "desde entonces."
    )

with der:
    st.markdown(
        f"**{es(unitario)} €/m²** sobre {es(superficie)} m² construidos  \n"
        f"Mediana del barrio: **{es(referencia)} €/m²** "
        f"({'+' if unitario >= referencia else '−'}"
        f"{es(abs(unitario / referencia - 1) * 100, 1)} % respecto de ella)  \n"
        f"{barrio} · distrito {perfil['DISTRITO']} · "
        f"{es(int(perfil['n_entrenamiento']))} viviendas en el entrenamiento"
    )

if not MINIMO <= valoracion <= MAXIMO:
    st.warning(
        f"**La valoración queda fuera del rango operativo del modelo** "
        f"({eur(MINIMO)} – {eur(MAXIMO)}). Fuera de esa banda el modelo pierde "
        f"fiabilidad: el error es sensiblemente mayor en los deciles extremos "
        f"de precio. Esta valoración requiere revisión profesional."
    )

if int(perfil["n_entrenamiento"]) < 30:
    st.info(
        f"**Barrio con muestra reducida.** {barrio} aporta solo "
        f"{es(int(perfil['n_entrenamiento']))} viviendas al entrenamiento, de "
        f"modo que su perfil de localización está peor estimado que el de un "
        f"barrio con varios centenares. Conviene contrastar el resultado."
    )
if perfil[GEO].isna().any():
    ausentes = [ETIQUETA[c] for c in GEO if pd.isna(perfil[c])]
    st.info(
        f"**Perfil de barrio incompleto.** En {barrio} no hay valor propio para "
        f"{' ni '.join(ausentes).lower()}; el modelo las sustituye por la "
        f"mediana del conjunto de Madrid."
    )

st.divider()

# ------------------------------------------------------------------ cascada
st.subheader("De qué se compone la valoración")
st.markdown(
    "La descomposición reparte la valoración entre las características de la "
    "vivienda mediante valores SHAP, que atribuyen a cada una su contribución "
    "exacta. Parte del valor de referencia del modelo —la valoración media "
    "sobre las viviendas de entrenamiento— y encadena las ocho contribuciones "
    "de mayor magnitud hasta cerrar en la valoración."
)

pasos = pasos_cascada(tabla_xgb, base_xgb, valoracion)
figura = grafico_cascada(pasos, base_xgb, valoracion,
                         "Valor de referencia del modelo", "Valoración")
st.pyplot(figura, use_container_width=True)
plt.close(figura)

st.caption(
    "El efecto en porcentaje de cada característica no depende del orden en "
    "que se consideren, porque la descomposición es aditiva en logaritmos. Su "
    "traducción a euros sí: se obtiene por acumulación sucesiva en orden "
    "decreciente de magnitud, que es la convención que emplea esta "
    "herramienta."
)

st.markdown("**Contribución de las 35 características**")
st.dataframe(tabla_presentable(tabla_xgb), use_container_width=True,
             hide_index=True, height=360)

st.divider()

# --------------------------------------------------------------------------- #
# Panel de contraste
# --------------------------------------------------------------------------- #

with st.expander("Contraste con el modelo interpretable"):
    tabla_lin, base_lin, valoracion_lin = descomponer(X, "lineal")
    diferencia = valoracion - valoracion_lin
    relativa = diferencia / valoracion_lin * 100

    uno, dos, tres = st.columns(3)
    uno.metric("Modelo de alto rendimiento", eur(valoracion))
    dos.metric("Modelo interpretable", eur(valoracion_lin))
    tres.metric("Discrepancia", eur(diferencia),
                f"{'+' if relativa >= 0 else '−'}{es(abs(relativa), 1)} %")

    if abs(relativa) >= UMBRAL_DISCREPANCIA:
        st.warning(
            "**Discrepancia elevada entre los dos modelos.** Suele indicar una "
            "vivienda atípica o una combinación poco frecuente de "
            "características, sobre la que el modelo aditivo y el de alto "
            "rendimiento difieren. Aconseja revisión."
        )
    else:
        st.markdown(
            "Los dos modelos coinciden dentro de un margen razonable. Una "
            "discrepancia grande indicaría una vivienda atípica o una "
            "combinación poco frecuente de características, y aconsejaría "
            "revisión."
        )

    st.markdown(
        "El modelo interpretable es una regresión lineal sobre los mismos "
        "datos. Se muestra como contraste, no como alternativa: el apartado 8 "
        "del trabajo concluye que el modelo de alto rendimiento es preferible, "
        "y la valoración que ofrece esta herramienta es la suya."
    )

    pasos_lin = pasos_cascada(tabla_lin, base_lin, valoracion_lin)
    figura_lin = grafico_cascada(pasos_lin, base_lin, valoracion_lin,
                                 "Vivienda de referencia", "Valoración lineal")
    st.pyplot(figura_lin, use_container_width=True)
    plt.close(figura_lin)

    st.info(
        "**Las dos cascadas no son comparables paso a paso.** La del modelo de "
        "alto rendimiento arranca en la valoración media del entrenamiento "
        f"({eur(base_xgb)}). La del modelo lineal arranca en el término "
        f"independiente de la regresión ({eur(base_lin)}), que es la valoración "
        "de una vivienda de referencia concreta: obra nueva, exterior, en el "
        "distrito Centro, a menos de 1,5 km del centro, a menos de 1 km de la "
        "Castellana, a menos de 200 m de una estación de metro, anterior a "
        "1955 y con el resto de características en su valor medio. Cada "
        "contribución mide la separación respecto de esa vivienda, no respecto "
        "de la media del mercado."
    )

    st.markdown("**Contribución de las 35 características**")
    st.dataframe(tabla_presentable(tabla_lin), use_container_width=True,
                 hide_index=True, height=360)

st.divider()

# --------------------------------------------------------------------------- #
# Sobre el modelo
# --------------------------------------------------------------------------- #

with st.expander("Sobre el modelo"):
    meta = ART["metadatos"]
    st.markdown(
        f"Ámbito: **{meta['ambito']}**. Modelo calibrado sobre "
        f"**{es(meta['n_entrenamiento'])} viviendas** y validado sobre otras "
        f"**{es(meta['n_validacion'])}** que no intervinieron en el ajuste. "
        f"La estimación es la **{meta['estimacion']}**."
    )

    st.markdown("**Rendimiento sobre las viviendas de validación**")
    NOMBRES = {
        "Ref. barrio (135)": "Superficie × precio del barrio",
        "Modelo lineal (OLS)": "Modelo interpretable (OLS)",
        "XGBoost": "Modelo de alto rendimiento (XGBoost)",
    }
    filas = []
    for clave in ("Ref. barrio (135)", "Modelo lineal (OLS)", "XGBoost"):
        m = ART["metricas"][clave]
        filas.append({
            "Procedimiento": NOMBRES[clave],
            "MdAPE": f"{es(m['MdAPE (%)'], 2)} %",
            "PE10": f"{es(m['PE10 (%)'], 1)} %",
            "PE20": f"{es(m['PE20 (%)'], 1)} %",
            "COD": es(m["COD"], 2),
        })
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    st.caption(
        "MdAPE: error relativo mediano. PE10 y PE20: proporción de "
        "valoraciones que se desvían menos de un 10 % y de un 20 % del precio "
        "observado. COD: coeficiente de dispersión; el estándar IAAO sitúa el "
        "umbral de consistencia en 15. El modelo de alto rendimiento es el "
        "único de los tres que lo alcanza."
    )

    st.markdown("**Limitaciones**")
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
