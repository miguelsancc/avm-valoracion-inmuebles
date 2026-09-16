# Valoración explicada de vivienda · Madrid

Modelo automatizado de valoración de inmuebles (AVM) sobre el mercado
residencial de Madrid, con aplicación web para el contraste de tasaciones en el
análisis de riesgo de garantías hipotecarias.

Trabajo Fin de Máster · Máster en Data Science, Big Data e Inteligencia
Artificial · Universidad Complutense de Madrid.

**Aplicación desplegada:** `<pendiente de desplegar>`

---

## Qué hace

A partir de diez características de una vivienda —el barrio y nueve atributos—
estima su precio de anuncio y **descompone la valoración en la contribución
exacta de cada característica**. Esa descomposición es el objeto del trabajo.
En el uso declarado —contrastar una tasación recibida de un proveedor externo—
lo que permite decidir no es la cifra por sí sola, sino poder atribuir la
discrepancia a un factor concreto.

El trabajo compara dos modelos sobre la misma información, la misma partición y
el mismo preprocesado. Medidos sobre las 6.284 viviendas de validación:

| Procedimiento | MdAPE | PE10 | PE20 | COD |
|---|---|---|---|---|
| Superficie × precio del barrio | 14,75 % | 35,4 % | 63,2 % | 19,89 |
| Modelo interpretable (OLS) | 14,11 % | 37,1 % | 66,0 % | 19,32 |
| **Modelo de alto rendimiento (XGBoost)** | **8,77 %** | **55,3 %** | **82,2 %** | **12,93** |

MdAPE es el error relativo mediano; PE10 y PE20, la proporción de valoraciones
comprendidas dentro de un margen del 10 % y del 20 % respecto del precio
observado; COD, el coeficiente de dispersión del estándar IAAO, cuyo umbral de
consistencia está en 15. El modelo de alto rendimiento es el único de los tres
que lo alcanza, y es el que la aplicación presenta como valoración; el
interpretable se muestra solo como contraste.

**Alcance.** El modelo se calibró sobre 31.418 viviendas anunciadas en Madrid en
el cuarto trimestre de 2018, de modo que estima el precio de anuncio a diciembre
de 2018 y no el valor de mercado actual. Son además precios de oferta y no de
transacción. No sustituye a una tasación profesional conforme a la normativa
aplicable.

---

## Estructura del repositorio

```
TFM_AVM/
├── README.md
├── 00_preparacion_datos.ipynb      conversión desde R (se ejecuta una vez)
├── 01_eda_geo.ipynb                EDA y enriquecimiento geoespacial
├── 02_modelizacion.ipynb           los dos modelos y su comparación
├── 03_interpretabilidad.ipynb      SHAP, equidad y artefactos de la app
├── tfm_preprocesado.py             `tramificar`, que el pipeline lineal referencia
├── modelos/
│   ├── avm_madrid.joblib           los dos pipelines, métricas y coeficientes
│   └── avm_app.joblib              perfil de barrios y apoyo de la aplicación
├── app/
│   ├── app.py                      aplicación Streamlit
│   └── requirements.txt            versiones fijadas
├── .streamlit/config.toml
├── memoria_TFM.md
├── estado_proyecto_TFM.md          registro de decisiones y cifras
├── indice_TFM.md
└── guia_TFM_transcripcion.md
```

`data/` y `figuras/` no se versionan. La primera queda fuera por tamaño y por
licencia —véase más abajo—; la segunda se regenera al ejecutar los notebooks.

---

## Ejecutar la aplicación en local

La aplicación **no entrena nada**: carga los dos artefactos de `modelos/`,
compone la entrada, predice y descompone el resultado. Funciona sin los datos de
partida.

Requiere **Python 3.12 o 3.13**. En 3.14 no hay wheels de `scikit-learn 1.6.1` y
la instalación falla.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r app/requirements.txt
```

```bash
streamlit run app/app.py
```

Se abre en `http://localhost:8501`. En Linux o macOS, el segundo paso es
`source .venv/bin/activate`.

Las versiones de `app/requirements.txt` van fijadas y no acotadas: los
artefactos son pickles de scikit-learn, que no es un formato de intercambio
estable entre versiones. Instalarlas tal cual es condición para que la
aplicación arranque.

---

## Desplegar en Streamlit Community Cloud

1. En [share.streamlit.io](https://share.streamlit.io), entrar con la cuenta de
   GitHub. Si el repositorio es privado, hay que **autorizar el acceso a
   repositorios privados**; de lo contrario no aparecerá en la lista.
2. «Create app» → «Yup, I have an app».
3. Repositorio, rama `main`, fichero principal **`app/app.py`**.
4. En **«Advanced settings», seleccionar Python 3.12.** No es opcional: si el
   valor por defecto de la plataforma subiera a 3.14, `scikit-learn==1.6.1` no
   tendría wheels y el despliegue se rompería.
5. Desplegar. La primera construcción tarda unos minutos, porque instala XGBoost
   y scikit-learn.

Una aplicación desplegada desde un repositorio privado nace privada. Se da
acceso a terceros añadiéndolos como colaboradores en GitHub o invitando su
correo como *viewer* desde el botón «Share». La cuenta gratuita admite una sola
aplicación privada a la vez.

---

## Reproducir el análisis completo

Los notebooks están escritos para **Google Colab**, con Google Drive como
almacenamiento persistente. La ruta base se declara en la constante `BASE` de la
primera celda de cada uno; cambiarla es lo único necesario para moverlos de
sitio.

```
/content/drive/MyDrive/Master Data Science/TFM_AVM
├── data/raw
├── data/processed
├── figuras
└── modelos
```

### Orden de ejecución

| Notebook | Entrada | Salida |
|---|---|---|
| **00** Preparación | paquete R `idealista18` | `data/raw/*.gpkg`, `*.csv` |
| **01** EDA y geo | `data/raw/` | `data/processed/madrid_201812_preparado.parquet` |
| **02** Modelización | el parquet anterior | `modelos/avm_madrid.joblib`, `tfm_preprocesado.py` |
| **03** Interpretabilidad | ambos anteriores | `modelos/avm_app.joblib` |

El **00 se ejecuta una sola vez**: es el único punto del trabajo en el que
interviene R, y su resultado es el punto de partida inmutable del análisis. El
resto se desarrolla íntegramente en Python.

El artefacto `avm_madrid.joblib` lo genera el bloque 9 del notebook 02, y
`avm_app.joblib`, el bloque 7 del 03. Ambos están versionados, de modo que **la
aplicación funciona sin reejecutar nada**.

### Descargas manuales

El paquete de datos se instala solo, desde el propio notebook 00. Las dos
descargas del INE hay que hacerlas a mano y colocarlas antes de ejecutar el
**bloque 5 del notebook 03**, que es el del análisis de equidad.

**1. Atlas de Distribución de Renta de los Hogares.** En el INE: serie
2015-2023 → Resultados por municipios, distritos y secciones censales por
provincias → Madrid → «Indicadores de renta media y mediana». Indicador **renta
neta media por persona**, periodo **2018**. CSV separado por `;`, codificación
ISO-8859.

```
data/raw/ine_renta_madrid_2018.csv        (580 KB, 4.788 filas)
```

**2. Cartografía de secciones censales, fichero nacional de 2018.**
`SECC_CE_20180101`, seccionado del Censo Electoral a 1 de enero, shapefile en
UTM huso 30. Descarga en <https://www.ine.es/dyngs/DAB/index.htm?cid=1389>.

```
data/raw/seccionado_2018/                 (5 ficheros, 105 MB el .shp)
```

El fichero nacional se filtra a Madrid en la primera ejecución y se conserva
recortado en `data/processed/secciones_madrid_2018.gpkg`, de 2 MB.

### Versiones

Los notebooks se ejecutaron con numpy 2.1.3, pandas 2.2.3, scikit-learn 1.6.1,
xgboost 3.0.0, geopandas 1.1.4 y mapclassify 2.10.0. Las dos últimas solo hacen
falta en los notebooks, no en la aplicación.

`xgboost` debe ser **3.0 o posterior**; la 2.1.3 es incompatible con
scikit-learn 1.6.1. `mapclassify` no viene de serie en Colab.

La semilla es 2018 en los tres notebooks que la necesitan, y el `XGBRegressor`
se instancia con `N_HILOS = 4`, condición para que las métricas sean
reproducibles. El motivo consta en `estado_proyecto_TFM.md`.

---

## Datos y licencias

**Conjunto de partida:** paquete de R `idealista18`, de David Rey y Pelayo
Arbués (idealista), Fernando López (UPCT) y Antonio Páez (McMaster University).
Publicado bajo **ODbL v1.0**. Artículo de referencia:
[10.1177/23998083241242844](https://doi.org/10.1177/23998083241242844),
*Environment and Planning B: Urban Analytics and City Science*, 2024.
Documentación: <https://paezha.github.io/idealista18/>.

La memoria, las figuras, el modelo entrenado y la aplicación son *produced
works* en los términos de la ODbL, de modo que solo obligan a atribución. La
cláusula de *share-alike* se activaría al publicar el conjunto de datos
derivado, y **este repositorio publica el código, no los datos**.

**Renta y cartografía:** Instituto Nacional de Estadística, **CC BY 4.0**.
