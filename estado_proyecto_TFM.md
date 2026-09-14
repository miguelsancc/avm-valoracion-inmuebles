# Estado del proyecto — TFM AVM (idealista18)

> Documento de trabajo. Recoge la estructura de notebooks, el inventario de
> datos y las decisiones tomadas durante el desarrollo. Se actualiza a medida
> que avanza el trabajo.
>
> **Última actualización:** notebook 02 cerrado (bloques 0 a 9), verificado con
> `Restart session and run all` y semilla unificada.

---

## Ámbito del trabajo

**Ciudad: Madrid.** Barcelona y Valencia quedan fuera del desarrollo por tres
motivos: husos UTM distintos (Barcelona en el 31N), mercados inmobiliarios no
comparables entre sí y menor granularidad de barrios (69 y 73 frente a 135).

**Trimestre: 201812 (cuarto trimestre).** Se selecciona por ser el de mayor
volumen: 31.418 viviendas frente a 17.622, 12.518 y 14.246 de los anteriores.
Verificada su representatividad frente al resto del ejercicio: medianas de
superficie, dormitorios, baños, año de construcción y distancias idénticas;
equipamiento dentro de 3 puntos porcentuales; cobertura espacial del 92% de las
celdas de 500 m que alcanza el año completo. La única diferencia apreciable es
el precio (+7,2%), atribuible a la tendencia del mercado y no a un cambio de
composición.

**Conjunto de trabajo: 31.418 viviendas.**

Trazabilidad: 94.815 anuncios (Madrid, 2018) → 44.270 (filtro 201812) → 31.418
(deduplicación por `ASSETID`).

**Efectos de la restricción temporal:**

- Elimina la tendencia intraanual de precios (9,4% entre el primer y el cuarto
  trimestre), por lo que no procede deflactar la variable objetivo ni incorporar
  el periodo como variable explicativa.
- `PERIOD` queda constante y se elimina del conjunto.
- No elimina el efecto estacional sino que lo fija: las particularidades del
  cuarto trimestre quedan incorporadas al modelo sin posibilidad de contraste.
  Limitación declarada en el apartado 2.3 de la memoria.

---

## Estructura de notebooks

| Notebook | Contenido | Puntos del índice | Estado |
|---|---|---|---|
| `00_preparacion_datos` | Instalación de R, conversión de `.rda` a GeoPackage/CSV | Alimenta el 2 | **Terminado** |
| `01_eda_geo` | Identidad de registros, EDA, análisis espacial y enriquecimiento | 2.3, 3, 4 | **Terminado** |
| `02_modelizacion` | Feature engineering y modelos | 5, 6 | **Terminado** |
| `03_interpretabilidad` | Interpretabilidad, trade-off, equidad | 7, 8, 9 | **Terminado** |
| App web (código aparte) | Productivización | 10 | Pendiente |

Los puntos 1 (introducción), 11 (conclusiones) y 12 (bibliografía) no proceden de
ningún notebook: son redacción.

**Bloques del notebook 01 (cerrado):**

```
0. Entorno y datos
1. Carga y primer vistazo                    → memoria 2.1
2. Identidad de los registros y ámbito       → memoria 2.3 y 3.3
3. Análisis descriptivo                      → memoria 3.1
   3.1 variable objetivo · 3.2 superficie · 3.3 naturaleza y calidad
   3.4 exploración bivariante · 3.5 tramificación y agrupación
4. Análisis por distrito y barrio            → memoria 3.2
5. Calidad del dato y valores atípicos       → memoria 3.3
6. Reproyección a sistema métrico            → memoria 4
7. Construcción de variables geoespaciales   → memoria 4
8. Conjunto preparado y guardado
```

**Encadenado entre notebooks:**

```
00 → data/raw/*.gpkg, *.csv
   → 01 → data/processed/madrid_201812_preparado.parquet
        → 02 → modelos/
             → 03
```

---

## Entorno de trabajo

- **Google Colab.** El disco de la máquina virtual es efímero; Google Drive es
  el almacenamiento persistente.
- **Ruta base:** `/content/drive/MyDrive/Master Data Science/TFM_AVM`
  (declarada siempre en la constante `BASE`; nunca escribir rutas completas a
  mano). Los notebooks residen directamente en esa carpeta.
- **Estructura de carpetas:** `data/raw`, `data/processed`, `figuras`,
  `modelos`.
- **Patrón de trabajo:** copiar de Drive a `/content/` al empezar la sesión y
  trabajar en local. La copia se hace con `shutil`, no con comandos de shell, lo
  que además evita el problema de los espacios en la ruta base.
- **Versiones verificadas:** numpy 2.1.3, pandas 2.2.3, geopandas 1.1.4,
  mapclassify 2.10.0. `geopandas` 1.1 incorpora `pyogrio` como dependencia
  obligatoria. `mapclassify` es necesario para los esquemas de clasificación de
  los mapas de coropletas y **no viene de serie en Colab**.
- **Formato de intercambio entre notebooks:** Parquet. Conserva tipos,
  geometría y CRS sin pérdida, a diferencia del CSV.

---

## Origen y licencia de los datos

- **Paquete:** `idealista18`, instalable desde GitHub (`paezha/idealista18`).
  No está en CRAN.
- **Autores:** David Rey y Pelayo Arbués (idealista), Fernando López (UPCT),
  Antonio Páez (McMaster University).
- **Artículo de referencia:** DOI `10.1177/23998083241242844`
  (*Environment and Planning B: Urban Analytics and City Science*, 2024).
- **Documentación:** `https://paezha.github.io/idealista18/`
- **Licencia:** ODbL v1.0 (Open Database License).

**Implicaciones de la licencia:**

- La memoria, los gráficos, el modelo entrenado y la app son *produced works*:
  solo obligan a **atribución**.
- El *share-alike* solo se activaría al publicar el conjunto de datos derivado.
- **Decisión tomada:** el repositorio publicará únicamente el código, no los
  datos derivados.

---

## Diccionario de variables según la documentación oficial

Consultado en la sección de referencia del objeto `Madrid_Sale`. Varias
denominaciones admiten lecturas distintas de la efectiva, y su desconocimiento
inicial obligó a rehacer parte del análisis.

| Variable | Contenido documentado |
|---|---|
| `ROOMNUMBER` | Número de **dormitorios**, no de estancias |
| `AMENITYID` | Nivel de equipamiento: 1 sin cocina equipada ni muebles, 2 cocina equipada, 3 cocina equipada y muebles. **Es ordinal** |
| `FLATLOCATIONID` | Tipo de vistas: 1 exterior, 2 interior. Codificada 1/2, no 0/1 |
| `FLOORCLEAN` | Planta, con valor 0 para la planta baja. Fuente: anunciante |
| `CADASTRALQUALITYID` | Calidad constructiva. Fuente: catastro. Escala de mejor (0) a peor (9) |
| `BUILTTYPEID_1/2/3` | 1 obra nueva, 2 segunda mano **a reformar**, 3 segunda mano **en buen estado** |
| `HAS*ORIENTATION` | **No son excluyentes**: una vivienda puede declarar varias |
| `PARKINGSPACEPRICE` | Precio de la plaza de aparcamiento en euros |
| `DISTANCE_TO_*` | En kilómetros (verificado empíricamente; la documentación no lo indica) |

**Advertencias sobre la propia documentación.** Declara 156.016 registros y 57
variables frente a los 94.815 y 42 del objeto distribuido para Madrid, y omite
`DISTANCE_TO_METRO` por un error de sintaxis. Ambas circunstancias aconsejan
verificar empíricamente cuanto se afirme sobre el conjunto.

---

## Inventario de datos (`data/raw`, 16 ficheros)

### Viviendas — GeoPackage

| Fichero | Filas | Columnas |
|---|---|---|
| `Madrid_Sale.gpkg` | 94.815 | 42 |
| `Barcelona_Sale.gpkg` | 61.486 | 42 |
| `Valencia_Sale.gpkg` | 33.622 | 42 |

Total: 189.923 anuncios. Geometría de tipo `Point`, **CRS EPSG:4326**.

### Barrios — GeoPackage (polígonos)

`Madrid_Polygons.gpkg` (135), `Barcelona_Polygons.gpkg` (69),
`Valencia_Polygons.gpkg` (73). Geometría `MultiPolygon`.

Columnas: `LOCATIONID`, `LOCATIONNAME`, `ZONELEVELID`, `geometry`.

Madrid: suma de áreas 602,14 km², área de la unión 602,13 km². Coherente con los
604 km² del término municipal. Constituyen una partición sin solapamientos.

### Puntos de interés — CSV

Tablas planas con columnas `Lon`/`Lat`, sin geometría ni identificadores de
estación: lo único explotable es la posición.

| Ciudad | City_Center | Metro | Eje urbano |
|---|---|---|---|
| Madrid | 1 | 240 | Castellana (155) |
| Barcelona | 1 | 463 | Diagonal (57) |
| Valencia | 1 | 99 | Blasco (27) |

Los ejes urbanos son series de puntos que **trazan una línea**, no ubicaciones
independientes.

### Otros

`properties_by_district.gpkg` (47 filas) — agregado por **distrito** de las tres
ciudades. La documentación lo describe como el número total de propiedades por
distrito en 2018. Columnas: `District`, `N_CADASTRE`, `N`, `CITY`, `geometry`.
Su cociente da una tasa de rotación del mercado. **No utilizado:** granularidad
demasiado gruesa frente al análisis por barrio.

---

## Columnas de `*_Sale` (42)

- **Objetivo y tamaño:** `PRICE`, `UNITPRICE`, `CONSTRUCTEDAREA`
- **Características:** `ROOMNUMBER` (dormitorios), `BATHNUMBER`, `FLOORCLEAN`,
  `ISDUPLEX`, `ISSTUDIO`, `ISINTOPFLOOR`, `CONSTRUCTIONYEAR`, `FLATLOCATIONID`
- **Equipamiento:** `AMENITYID`, `HASTERRACE`, `HASLIFT`, `HASAIRCONDITIONING`,
  `HASPARKINGSPACE`, `ISPARKINGSPACEINCLUDEDINPRICE`, `PARKINGSPACEPRICE`,
  `HASBOXROOM`, `HASWARDROBE`, `HASSWIMMINGPOOL`, `HASDOORMAN`, `HASGARDEN`
- **Orientación:** `HASNORTHORIENTATION`, `HASSOUTHORIENTATION`,
  `HASEASTORIENTATION`, `HASWESTORIENTATION`
- **Catastro:** `CADCONSTRUCTIONYEAR`, `CADMAXBUILDINGFLOOR`,
  `CADDWELLINGCOUNT`, `CADASTRALQUALITYID`
- **Tipo de obra:** `BUILTTYPEID_1`, `BUILTTYPEID_2`, `BUILTTYPEID_3`
- **Localización:** `LONGITUDE`, `LATITUDE`, `geometry`
- **Distancias precalculadas:** `DISTANCE_TO_CITY_CENTER`, `DISTANCE_TO_METRO`,
  `DISTANCE_TO_CASTELLANA` (en **kilómetros**)
- **Otros:** `ASSETID`, `PERIOD`

Naturaleza estadística tras la clasificación: **24 categóricas** (4 etiquetas y
20 indicadores binarios) y **16 numéricas**, más la geometría.

---

## Hallazgos sobre la estructura del dato

### `ASSETID` no es único a nivel de fila

En Madrid, 94.815 anuncios corresponden a 75.804 identificadores. Las
repeticiones se producen **íntegramente dentro de un mismo trimestre**.

Corresponden a varios anuncios de la misma vivienda: comparten el 100% de las
variables catastrales, el 95,2% la planta, el 98,2% los dormitorios y el 99,1%
los baños, con una dispersión de precio del 4,3% en mediana.

### El identificador no permite seguimiento temporal

Ningún `ASSETID` figura en más de un trimestre, pese a que la documentación
afirma lo contrario. Un identificador alternativo por atributos confirma que
**sí existen republicaciones**: 2.323 huellas figuran en más de un trimestre,
volumen que el 4,79% de falsos positivos del procedimiento no explica.

Ese mismo 4,79% impide ir más lejos: no hay forma de señalar cuáles de las 2.323
coincidencias son republicaciones efectivas y cuáles viviendas distintas
indistinguibles entre sí. Insuficiente para fundamentar una deduplicación. De
ahí la restricción a un único trimestre.

### Perturbación de coordenadas fila a fila

Separación mediana de 73 m entre anuncios de una misma vivienda (percentil 90:
98 m), compatible con un desplazamiento de hasta unos 50 m aplicado a **cada
registro de forma independiente**. Las `DISTANCE_TO_*` presentan valores
distintos dentro de un mismo grupo, lo que acredita que se calcularon **después**
de perturbar.

**Implicación:** el ruido de 50 m fija el suelo de resolución del enriquecimiento
geoespacial. Radios de 500 m y agregados por barrio son robustos.

### `BARRIO` no identificaba el barrio *(corregido)*

La columna `BARRIO`, obtenida al partir `LOCATIONID`, contenía el código de dos
dígitos del barrio **relativo a su distrito**: diez valores distintos para 135
zonas. Verificado que ninguna agrupación del notebook 01 la empleó —todas usan
`LOCATIONID`—, por lo que ninguna cifra resulta afectada. Se elimina del conjunto
preparado por el riesgo de agrupación errónea. `LOCATIONNAME` queda como clave
legible: 135 nombres para 135 barrios, ninguno compartido entre distritos.

**Conjunto preparado: 40 columnas.** Objetivo, 36 explicativas, 3 metadatos de
zona (`LOCATIONID`, `LOCATIONNAME`, `DISTRITO`) y la geometría.

### `LOCATIONID` codifica el distrito

Estructura `0-EU-ES-28-07-001-079-{DISTRITO}-{BARRIO}`. Verificado contra la
división oficial. Proporciona 21 distritos frente a 135 barrios.

Los 135 polígonos son **zonas de idealista, no la división administrativa
oficial** (Madrid tiene 131 barrios). Declarado en la memoria.

### `CONSTRUCTIONYEAR` inservible

**56,31%** de valores ausentes sobre el conjunto de trabajo (17.690 de 31.418).
`CADCONSTRUCTIONYEAR`, de fuente catastral, está completa. Se prescinde de la
primera.

*Nota: la cifra del 58,93% que figuraba en versiones anteriores correspondía al
conjunto anual completo, no al de trabajo.*

### `UNITPRICE` es el cociente exacto de la objetivo

Diferencia máxima 0,00000000 sobre 31.418 filas, correlación 1,0. Conserva todos
los decimales del cociente (solo el 17,98% coincide con su valor redondeado a
dos decimales), lo que descarta que sea un valor de referencia publicado.

**Su empleo como predictor constituiría fuga de información.** Se conserva
únicamente con finalidad descriptiva.

### La planta está censurada en el valor 11 *(no documentado en la fuente)*

La frecuencia decrece de forma continua hasta la planta décima (125 viviendas) y
repunta a 339 en la undécima. Existen 1.733 viviendas en edificios de más de once
plantas. La censura opera **por agrupación**, no por exclusión: las viviendas
permanecen con su planta recodificada.

El valor −1 es legítimo (300 viviendas bajo rasante) y constituye el suelo real
de la variable.

### `PARKINGSPACEPRICE` no describe la vivienda *(no documentado)*

El 97,6% de los registros presenta el valor 1, código de ausencia. Los 757 con
precio efectivo corresponden **en su totalidad** a anuncios que declaran no
incluir plaza, mientras que ninguna de las 6.980 que sí la declaran presenta
precio. Registra el importe de una plaza ofertada de forma independiente.

`ISPARKINGSPACEINCLUDEDINPRICE` coincide **exactamente** con `HASPARKINGSPACE` en
las 31.418 filas.

### Discrepancia entre planta declarada y altura catastral

758 registros con planta superior a la altura del edificio. De ellos, 26 con
altura nula (error) y 732 con excesos reducidos: 378 de una planta y 190 de dos.
Compatible con discrepancia de criterio entre fuentes en el cómputo de la planta
baja. No corregible: no hay criterio para determinar cuál de las dos fuentes
ajustar.

### Otras incidencias de codificación

- Las orientaciones **no son excluyentes**: 5.194 viviendas declaran dos, 492
  tres y 271 las cuatro. El 51,3% no declara ninguna.
- `BUILTTYPEID_1/2/3` **sí** constituyen partición completa: suman 1 en el 100%
  de las filas. Implica dependencia lineal: requieren categoría de referencia.
- `AMENITYID` y `FLATLOCATIONID` respetan sus escalas documentadas.
- 65 valores materialmente imposibles, recodificados a ausente: 3 con más de 15
  dormitorios, 32 con baños nulos o superiores a 10, 3 con año catastral
  anterior a 1800 y 27 con altura de edificio nula.
- 58 viviendas sin dormitorios y sin declararse estudio, y 2 estudios con más de
  un dormitorio. Se conservan: no hay criterio para distinguir tipología
  legítima de error.

---

## Estructura del precio: resultados del EDA

### Variable objetivo

| Magnitud | Valor |
|---|---|
| Precio mediano | 268.000 € |
| Precio medio | 406.266 € (52% sobre la mediana) |
| Asimetría | 4,20 → 0,55 en logaritmos |
| Superficie mediana | 82 m² |
| Precio unitario mediano | 3.565 €/m² |

El precio unitario está acotado en origen entre 805 y 9.994 €/m². La cola decrece
de forma continua hasta el corte (476, 344, 248, 200, 127 y 75 viviendas en los
tramos de 500 €/m² entre 7.000 y 10.000), lo que acredita **exclusión en origen
y no reasignación al límite**.

**Precisión importante:** lo excluido es el segmento de mayor precio **unitario**,
no el de mayor importe. El conjunto llega a 8.133.000 € por vía de la superficie
(máximo 934 m²).

### Relación con la superficie

- Elasticidad log-log: **1,14**. Duplicar la superficie multiplica el precio por
  2,20.
- Varianza explicada: 74% del precio.
- **Error relativo mediano de la valoración por superficie sola: 33,7%.**
- La especificación lineal sobre variables originales produce 233 predicciones
  negativas (superficies ≤ 27 m²). Descartada.

### Relación en U con el tamaño *(recurrente en el conjunto)*

El precio unitario describe una U respecto a la superficie: 4.581 €/m² en el
decil inferior (40 m²), mínimo de 2.595 en el entorno de 70 m², y 4.685 en el
superior (226 m²). Factor 1,81 entre extremos.

**Causa: confusión con la localización.** La distancia mediana al centro describe
el perfil inverso (2,58 → 4,78 → 2,89 km), con correlación de −0,935 sobre los
diez tramos.

El mismo patrón se repite con la antigüedad del edificio, con la antigüedad
mediana del barrio y con la densidad de anuncios. **En Madrid, casi toda variable
que aparenta medir otra cosa acaba midiendo centralidad.**

### Localización

| Partición | η² sobre log(precio unitario) |
|---|---|
| Barrio (135) | **0,727** |
| Distrito (21) | 0,651 |
| Superficie (deciles) | 0,145 |

- Precio unitario por barrio: de 1.241 (San Cristóbal) a 7.595 €/m² (Recoletos).
  **Factor 6,12.** Por distrito, factor 3,39.
- El gradiente se organiza en torno al **eje de la Castellana**, no de forma
  radial: `DISTANCE_TO_CASTELLANA` supera a `DISTANCE_TO_CITY_CENTER` en
  capacidad explicativa (0,23 frente a 0,16 sobre el precio).
- **Error de la valoración por zona × superficie: 14,6%.**
- Cruce espacial: barrio asignado a la totalidad de las viviendas. 24 puntos
  caían fuera de todo polígono —mediana de 0 m al borde, máxima de 254 m— y se
  asignan al más próximo.
- **Umbral de 30 viviendas por barrio** para agregados: afecta a 6 barrios y al
  0,28% del conjunto. Todos corresponden a suelo no residencial (El Pardo,
  aeropuerto, Cuatro Vientos) o urbanizaciones de baja densidad.

### No linealidad de las variables de localización

La brecha entre razón de correlación y coeficiente de determinación lineal
identifica las variables que exigen transformación:

| Variable | η² | r² lineal | Brecha |
|---|---|---|---|
| `DISTANCE_TO_CASTELLANA` | 0,225 | 0,128 | +0,097 |
| `DISTANCE_TO_CITY_CENTER` | 0,161 | 0,070 | +0,090 |
| `CADMAXBUILDINGFLOOR` | 0,137 | 0,068 | +0,069 |
| `DISTANCE_TO_METRO` | 0,032 | 0,000 | +0,032 |

`DISTANCE_TO_METRO` presenta correlación lineal prácticamente nula pese a tener
capacidad explicativa: un modelo lineal sobre la variable en bruto no vería nada.

---

## Variables descartadas

| Variable | Motivo |
|---|---|
| `ASSETID` | Identificador. Agotó su función en la deduplicación |
| `UNITPRICE` | Cociente exacto de la objetivo. Fuga de información |
| `PARKINGSPACEPRICE` | No describe la vivienda anunciada. 97,6% con código de ausencia |
| `ISPARKINGSPACEINCLUDEDINPRICE` | Idéntica a `HASPARKINGSPACE` |
| `CONSTRUCTIONYEAR` | 56,31% de ausentes. Sustituida por la catastral |
| `AMENITYID` | 94,33% en un nivel, η² nulo |
| `LONGITUDE`, `LATITUDE` | Redundantes con la geometría |
| `PERIOD` | Constante tras el filtro temporal |

**No descartadas pese a η² bajo:** las cuatro orientaciones, `HASTERRACE`,
`ISSTUDIO`, `ISDUPLEX`, `ISINTOPFLOOR` y los tres `BUILTTYPEID`. Un η² reducido
indica ausencia de señal *bivariante*, no ausencia de aportación al modelo. Su
descarte, en su caso, se decide sobre la importancia estimada.

---

## Variables construidas (bloque 7)

Nueve construidas, **cuatro retenidas** tras verificar que la supresión de las
restantes no altera el error.

| Retenida | Contenido |
|---|---|
| `METRO_EN_1000M` | Estaciones de metro en 1 km. η² 0,37 sobre precio unitario |
| `ANUNCIOS_EN_500M` | Anuncios en 500 m, excluida la propia vivienda |
| `BARRIO_ANTIGUEDAD_MED` | Año mediano de construcción del barrio |
| `BARRIO_AREA_MED` | Superficie mediana del barrio. **η² 0,42, la más alta del conjunto** |

| Descartada | Motivo |
|---|---|
| `DIST_METRO_2A`, `DIST_METRO_3A` | Correlación 0,947 y 0,902 con la distancia a la primera |
| `RATIO_METRO_2A1A` | η² exactamente 0,00 |
| `METRO_EN_500M`, `ANUNCIOS_EN_1000M` | Redundantes con su par del otro radio |
| `BARRIO_DENSIDAD_KM2` | Correlación 0,903 con `ANUNCIOS_EN_500M` |

**Aportación medida:** reducción del **16,4%** del error sobre un modelo que ya
incorpora las tres distancias de origen (18,3% → 15,1%). Las distancias de origen
aportan, a su vez, un 22,2% sobre el modelo de atributos de la vivienda.

**Dos resultados destacables.** `BARRIO_AREA_MED` presenta correlación de solo
0,198 con la variable de origen más próxima: el tipo de producto de la zona es
información genuinamente nueva. Y `BARRIO_ANTIGUEDAD_MED`, pese a su correlación
de 0,792 con la distancia al centro, resulta necesaria: su supresión eleva el
error un 1,75%. La correlación bivariante habría llevado a descartarla por error.

**Excluidas por construcción:** precio mediano del barrio y retardo espacial del
precio. Ambos emplean la variable objetivo de las viviendas del entorno → fuga de
información, dependencia de una tabla de referencia en explotación y deterioro de
la interpretabilidad.

---

## Decisiones técnicas tomadas

| Decisión | Motivo |
|---|---|
| Convertir con R en lugar de `pyreadr` / `rdata` | Los objetos `sf` tienen columna-lista de geometría; `pyreadr` no la soporta |
| GeoPackage como formato intermedio (notebook 00) | Conserva geometría y CRS |
| Parquet como formato de salida (notebook 01) | Conserva tipos, geometría y CRS; más rápido y compacto que CSV o GPKG |
| Escribir primero en `/content` y copiar a Drive | Drive es un montaje de red, lento y frágil para escrituras grandes |
| Separar preparación de análisis | La preparación es determinista y de un solo uso; evita depender de R |
| Guardar en 4326, reproyectar al calcular | Se conserva el dato tal como viene |
| **Restringir el ámbito a Madrid** | Husos UTM distintos, mercados no comparables, mayor granularidad |
| **Restringir el ámbito a 201812** | El identificador es fiable dentro de un trimestre pero no entre trimestres |
| **Deduplicar por `ASSETID`, conservando el anuncio de precio mediano** | Robusto frente a errores de tecleo; preserva la coherencia interna del registro |
| **No corregir la perturbación de coordenadas** | Promediar reduciría el error solo en el 18% de las viviendas, produciendo dos niveles de precisión indistinguibles |
| **Asignar explícitamente EPSG:4326 a los polígonos** | El fichero declara el datum pero no el código |
| **Emplear la razón de correlación (η²) para ordenar variables** | Análoga al valor de la información en clasificación, adaptada a objetivo continua. Capta relaciones no monótonas, que Pearson no detecta |
| **Criterio de variabilidad por peso del valor dominante (>95%)** | El umbral del 5% de valores distintos depende del tamaño muestral: sobre 31.418 filas exigiría 1.571 valores, inalcanzable para variables discretas |
| **No depurar atípicos de la variable objetivo** | Un precio elevado no es un error. Su exclusión reduciría el ámbito justo donde se concentran las garantías de mayor importe |
| **Asignar por proximidad los puntos fuera de polígono** | La mediana de distancia al borde es 0 m: caen sobre la línea de frontera, que el predicado `within` excluye. Rechazarlos aplicaría al 0,08% del conjunto un criterio distinto del asumido para el resto, dado que la perturbación de coordenadas afecta por igual a todas las viviendas |
| **Umbral de 30 viviendas por barrio para agregados** | Criterio convencional. Afecta al 0,28% y solo a suelo no residencial |
| **Precio unitario como magnitud de comparación entre zonas** | El precio absoluto confunde nivel de precio con tamaño típico de la vivienda |
| **Descartar el retardo espacial como predictor** | Emplea la respuesta de las vecinas. Su uso como diagnóstico de residuos queda opcional en el notebook 03 |
| **No emplear fuentes externas más allá del INE** | Google Maps u OpenStreetMap devolverían el estado actual, no el de 2018, y añadirían dependencia de red que compromete la reproducibilidad |

---

## Notebook 02 — decisiones tomadas (bloques 0-3)

### Partición

Aleatoria por filas, 80/20, **estratificada por decil de precio**: 25.134 y
6.284 viviendas. Distribuciones equivalentes en todos los percentiles; 135
barrios en entrenamiento y 134 en validación. Se descarta la partición espacial
por bloques: mide transferibilidad a territorios no observados, cuestión ajena
al caso de uso.

Se parte el GeoDataFrame completo y no una matriz de explicativas, para
conservar geometría e identificadores en ambas particiones.

### Tramificación de variables no monótonas

Procedimiento: se compara la capacidad explicativa de cada formulación frente a
un **techo** estimado con veinte tramos (forma libre), midiendo qué fracción de
la **brecha** respecto a la especificación lineal recupera cada una.

| Variable | Techo (η²) | Lineal (r²) | Log | Cortes fijos |
|---|---|---|---|---|
| `DISTANCE_TO_CITY_CENTER` | 0,177 | 0,068 | 16,2% | **70,8%** |
| `DISTANCE_TO_CASTELLANA` | 0,233 | 0,125 | 49,4% | **78,5%** |
| `DISTANCE_TO_METRO` | 0,036 | 0,000 | 14,4% | **89,7%** |
| `CADCONSTRUCTIONYEAR` | 0,048 | 0,002 | — | **89,7%** |

**Transformación logarítmica descartada.** Recupera el 16% en la distancia al
centro. Las curvas presentan extremos interiores —máximo a 2,5 km del centro,
mínimo a 700 m del metro— que ninguna función monótona reproduce.

**Cuantiles descartados.** Producen recuperación no monótona respecto al número
de intervalos: la distancia al centro cae al 42,5% con cuatro intervalos frente
al 62,2% con tres, y el año al 57,5% con seis frente al 81,7% con cuatro. Los
cortes automáticos promedian el extremo con el tramo contiguo. Los cortes fijos
baten a los cuantiles en las cuatro variables con igual número de intervalos.

**Cortes adoptados:**

| Variable | Cortes | Intervalos |
|---|---|---|
| Centro | 1,5 · 3 · 5 · 8 km | 5 |
| Castellana | 1 · 2,5 · 4 · 6 km | 5 |
| Metro | 200 · 350 · 500 · 800 m | 5 |
| Año catastral | 1955 · 1970 · 1985 | 4 |

Seis intervalos en el año recuperan 1,2 puntos más (90,9%) a cambio de dos
columnas: no compensa sobre un techo de 0,048. Los cortes descartados separaban
periodos de nivel próximo.

**Hallazgo.** El máximo de precio está en la corona de 1,5-3 km del centro, un
21% por encima del casco histórico. Una distancia radial única mezcla el norte
caro con el sur barato; de ahí que la distancia al eje supere a la radial.

### Preprocesado

**Grupos:** 10 numéricas continuas · 18 binarias · 4 tramificadas · 2
categóricas · 1 ordinal = **35 explicativas**.

| Decisión | Motivo |
|---|---|
| `DISTRITO` como predictor, `LOCATIONNAME` solo como identificador | 135 niveles deterioran la interpretabilidad; la codificación por la respuesta sería fuga |
| `BUILTTYPEID` sin refundir: se descarta uno como referencia | Los tres ya son una codificación disyuntiva completa |
| `CADASTRALQUALITYID` ordinal en una columna | Escala monótona verificada; parsimonia |
| Referencia de vistas: exterior (no la ausencia) | `drop="first"` habría dejado como base el nivel no declarado |
| Referencia de distrito: Centro (01), fijada explícitamente | Evita que dependa del orden alfabético |
| Imputación de agregados de barrio por la mediana | 88 casos, 0,28%, suelo no residencial. El agregado de distrito habría exigido función propia |
| Estandarización, no normalización al rango | La normalización es sensible a los extremos; máximo de 934 m² |
| Encapsulado en `Pipeline` + `ColumnTransformer` serializado | La app aplica el mismo preprocesado que el entrenamiento por construcción |
| Módulo `tfm_preprocesado.py` con la función de tramificación | `KBinsDiscretizer` no admite cortes propios; sobrescribir `bin_edges_` se rompe con la validación cruzada, que reajusta en cada pliegue |

**Dos ramas.** Tramificada y estandarizada (66 columnas) para el modelo
interpretable; escala original (55 columnas) para XGBoost. Comparten imputación,
codificación y partición. Declarado en la memoria para que la comparación del
6.4 no parezca inconsistente.

**Salidas del bloque:** `modelos/preprocesado.joblib` (18 KB) con ambas ramas
ajustadas, los nombres de columna, la tramificación y la semilla. Carga
verificada sobre validación.

**Etiquetas de presentación.** Diccionario que traduce `DISTANCE_TO_METRO_2` a
`Metro: 350-500`, para la lectura de coeficientes e importancias del apartado 7.
No forma parte del objeto serializado.

## Notebook 02 — bloque 4: protocolo de validación y métricas

### Validación

`StratifiedKFold`, 5 pliegues, estratificación por decil de precio, semilla
12345. Índices fijados una sola vez en `PLIEGUES`: todas las configuraciones de
los bloques 6 y 7 se miden sobre los mismos pliegues, requisito para que las
diferencias observadas respondan al modelo y no a la partición. El conjunto de
validación (6.284) queda reservado hasta el bloque 8.

Homogeneidad verificada: mediana idéntica en los cinco pliegues (268.000 €) y
P90 dentro de un rango de 2.800 € sobre 813.000.

### Objetivo en logaritmos — justificación

- Convierte el error absoluto en relativo: la diferencia en logaritmos *es* el
  error porcentual. Sin logaritmos, el ajuste persigue la cola alta.
- Recoge la naturaleza multiplicativa de los efectos hedónicos: sumar en
  logaritmos equivale a multiplicar en euros.
- Estabiliza la varianza del error y simetriza la distribución (asimetría
  4,20 → 0,55).
- Impide predicciones negativas. La especificación lineal producía 233.

### Criterio de selección

MdAPE como *scorer* de la validación cruzada, con pérdida interna cuadrática
sobre `y_log`. La distinción es la siguiente: la pérdida interna guía cada
iteración del algoritmo y debe ser derivable; el criterio de selección se limita
a ordenar configuraciones ya estimadas y no lo requiere. MdAPE no es admisible
como pérdida —al ser una mediana, su derivada es nula o discontinua— pero sí
como criterio.

`refit` por MdAPE. Scorers auxiliares `MAE_log` y `R2_log` para diagnóstico.
Parámetros comunes en `CV_KWARGS`.

### Retro-transformación sin corrección

`exp(ŷ)` estima la **mediana** condicional del precio. No se aplica corrección
de Duan (*smearing*), que estimaría la media.

Motivo: media y mediana son magnitudes distintas y para tasación de garantías
interesa el valor típico del inmueble, no el promedio de escenarios incluidos
los excepcionales. Sobre una distribución asimétrica, la media condicional queda
desplazada al alza por la cola. A ello se añade coherencia interna: MdAPE es
precisamente la métrica que minimiza la mediana condicional, de modo que
corregir introduciría inconsistencia entre la magnitud estimada y la que la
evalúa.

### Batería de métricas

`metricas_avm()` devuelve MdAPE (principal), PE10, PE20, mediana del ratio y
COD, más MAE log y R² log como control técnico. `tabla_metricas()` compone la
comparativa. `ratio_por_quintil()` cubre la equidad vertical.

Verificada sobre cuatro casos simulados de resultado conocido: predicción
exacta, sesgo de nivel del +10%, regresividad deliberada y ruido puro.

### PRD y PRB retirados

Decisión documentada. El PRB presenta **sesgo de endogeneidad por
construcción**: regresa la desviación del ratio sobre un proxy de valor que
contiene la propia predicción, lo que induce pendiente positiva espuria (IAAO
Statistical Tools and Measures Task Force, 2023). En sentido contrario, la
compresión de las predicciones hacia la media induce **regresividad mecánica**
(McMillen y Singh, 2023). Ambos sesgos escalan con la imprecisión del modelo, de
modo que el PRB no es comparable entre modelos de precisión distinta ni entre
zonas con error distinto.

Comprobación propia: sobre 8.000 precios log-normales con ruido gaussiano puro
de σ = 0,15, sin regresividad alguna, el PRB resultó +0,0266 en lugar de 0.

**Sustituidos por `ratio_por_quintil()`**: mediana del ratio y MdAPE por quintil
de viviendas, ordenados por una variable ajena al error de la vivienda concreta
(superficie, o nivel de precio de la zona). Verificado que detecta la
regresividad del caso 3 y no la inventa en el caso 4 (ratios de 1,006 a 1,009).

**COD conservado.** Mide dispersión en torno a la mediana del ratio y no en
torno a 1, lo que separa consistencia de sesgo de nivel: un modelo puede ser
consistente y estar desplazado a la vez.

### Salvedad IAAO — debe figurar literalmente en la memoria

El estándar procede de la tasación catastral con fines fiscales y presupone un
denominador constituido por precios de transacción verificados, obtenidos con
posterioridad e independencia respecto de la valoración. Aquí el denominador es
el precio de oferta y procede de la misma fuente con que se entrenó el modelo.
Los valores resultantes son optimistas frente a un estudio de ratio real: sirven
como comparación entre modelos y entre zonas, no como certificación frente al
estándar.

**No existe equivalente europeo.** Las European Valuation Standards de TEGoVA
—y en particular su EVS 6 sobre modelos automatizados— son de naturaleza
procedimental y no métrica: regulan quién firma y qué controles se aplican, sin
definir medidas de equidad ni umbrales. El artículo 229.1 del Reglamento de
Requisitos de Capital exige además intervención de tasador competente, requisito
reflejado en las directrices de la Autoridad Bancaria Europea. De ahí que se
recurra al marco IAAO pese a su origen fiscal: es el único que define métricas
de equidad cuantificables.

Ese marco da contenido al apartado 1.2: el AVM asiste al tasador y no lo
sustituye, de modo que los usos legítimos son la actualización de valoraciones
de cartera, el cribado previo y el contraste de tasaciones recibidas, y no la
tasación de originación.

---

## Notebook 02 — bloque 5: modelos de referencia

### Diseño

Tres niveles de agregación espacial sobre idéntica fórmula —precio unitario
mediano de zona × superficie—, **construidos sobre entrenamiento y evaluados
sobre validación**. La mediana, no la media, por el mismo motivo que MdAPE.

| Nivel | Unidades | Qué aísla |
|---|---|---|
| Global | 1 | Prescinde de la localización |
| Distrito | 21 | Misma información espacial que el modelo |
| Barrio | 135 | Máxima granularidad disponible |

La referencia de árboles (15,1% en CV) **se retira**: era instrumento del
notebook 01 para medir la aportación geoespacial, no un modelo de referencia. El
XGBoost del bloque 7 la sustituye con ventaja.

Zonas bajo el umbral de 30 viviendas → mediana de su distrito. Zonas ausentes en
entrenamiento → mediana global (rama defensiva; no se activó).

### Resultados sobre validación (6.284 viviendas)

| Referencia | MdAPE | PE10 | PE20 | Mediana ratio | COD |
|---|---|---|---|---|---|
| Superficie (global) | 33,71% | 14,0% | 29,0% | 1,0100 | 45,79 |
| Distrito (21) | 17,76% | 30,1% | 54,9% | 1,0099 | 22,85 |
| Barrio (135) | **14,75%** | 35,4% | 63,2% | 1,0005 | 19,89 |

Precio unitario mediano global en entrenamiento: 3.571 €/m². Recorrido por
distrito 1.645–5.578 (factor 3,39); por barrio 1.243–7.574 (factor 6,09).

**El 33,7% se reproduce exactamente. El 14,6% pasa a 14,75%**, subida menor de
la prevista: con unas 230 viviendas por barrio, la contribución de una vivienda
a la mediana de su zona es marginal.

### Hallazgos para el 6.1

- La localización reduce el error un **56,2%** respecto a la referencia global.
- El salto de distrito a barrio vale un **17%** de reducción (17,76% → 14,75%):
  mide exactamente lo que al modelo se le negó al descartar el barrio como
  predictor. Si el AVM bate el 14,75%, lo hace compensando con enriquecimiento
  geoespacial una desventaja de tres puntos.
- **COD de la referencia de barrio: 19,89**, por encima del umbral IAAO de 15.
  La regla elemental no alcanza el estándar de consistencia del sector.
  Argumento de negocio no previsto.
- Ratio por quintil de superficie: 0,933 en Q1 frente a 1,038 en Q5. La
  referencia **infravalora las viviendas pequeñas**, manifestación de la
  elasticidad 1,14 del apartado 3.1: un precio unitario constante de zona no
  recoge la relación no proporcional entre superficie y precio. Defecto
  estructural que el modelo sí puede corregir.

### Corrección respecto al notebook 01

**8 barrios** bajo el umbral de 30 viviendas en entrenamiento (123 viviendas,
**0,49%**), frente a los 6 (0,28%) sobre el conjunto completo. Dos cruzan a la
baja al estimarse sobre el 80%.

Los nuevos —Arroyo del Fresno y Palomas, 24 viviendas cada uno— son
urbanizaciones residenciales, no suelo no residencial. **Revisar la frase del
apartado 3.2 de la memoria** que afirma que todos corresponden a suelo no
residencial o urbanizaciones de baja densidad.

### Asimetría a declarar en el 6.1

La referencia de barrio emplea la respuesta de las viviendas del entorno, que es
precisamente lo que se excluyó del modelo como fuga (apartado 4). Es legítimo
—las medianas se estiman solo en entrenamiento y ninguna vivienda de validación
contribuye a la suya—, pero la asimetría debe quedar explícita: la referencia
juega con información que al modelo se le negó deliberadamente.

---

---

## Notebook 02 — bloque 6: modelo interpretable

**Familia: OLS sin regularización.** Es el estándar en valoración masiva, ámbito
del que procede el marco IAAO adoptado, y conserva inferencia sobre los
coeficientes. Ridge se ajustó como contraste y se descartó: encogimiento del
0,3%, discrepancia máxima de 0,0026, ningún cambio de signo. Stepwise descartado:
invalida los p-valores, es inestable con variables correlacionadas y rompe las
escaleras de tramos.

**Sin depuración por significación.** Con 25.134 observaciones el contraste no
discrimina (55 de 67 significativos). Los 12 no significativos son casi todos
tramos frontera o distritos pequeños: «no significativo» significa
«indistinguible del tramo de referencia», no «irrelevante».

**Colinealidad.** VIF > 10 en 4 columnas, todas tramos de distancia al centro;
VIF 8-9 en distritos. Estructural, no tratable, sí declarable.

**Influencia.** Cook máxima 0,0128 (umbral de preocupación: 1). Excluir las 20
más influyentes mueve el coeficiente más afectado 0,0139 y ninguno cambia de
signo. **El extremo de 13 desviaciones típicas no exige tratamiento**: cuestión
pendiente desde el bloque 3, resuelta con medición.

**Coeficientes.** Ascensor +19%, piscina +12,3%, garaje +7,5%, aire +7,1%. Obra
usada −23,3% y a reformar −16,2% frente a obra nueva. Estudio −14,6%. Distritos
periféricos hasta −45% frente a Centro. Control de signos superado.

**Las cuatro orientaciones son irrelevantes**: coeficientes de 0,2%, p > 0,58, y
0,09 pp de aporte en CV. Hallazgo contraintuitivo frente a los manuales de
tasación.

**`ISINTOPFLOOR` nulo (+0,63%, n.s.) — diagnosticado.** No es absorción por
terraza (quitarla lo sube solo a +1,22%). El indicador captura dos efectos
opuestos: en plantas bajas el ático vale MENOS (2.605 €/m² frente a 3.456 en
primera), porque ser última planta de un edificio de dos significa edificio bajo
y periférico; a partir de la quinta se invierte (5.280 frente a 3.842 en octava).
El modelo aditivo los promedia a cero. **Requiere interacción con la altura del
edificio: material para el apartado 8**, como caso concreto de dónde el lineal
pierde frente a XGBoost. Apunte aparte: solo el 24,3% de los áticos declarados
tiene planta igual a la altura catastral.

### Aportación de bloques de variables (MdAPE en CV)

| Especificación | MdAPE |
|---|---|
| Características de vivienda | 22,41% |
| + distrito | 15,00% |
| + enriquecimiento geoespacial | 14,34% |
| + contexto de barrio | **14,03%** |
| Completo sin orientación | 14,12% |

**Distrito y geoespacial se solapan fuertemente.** Aporte aislado frente a
marginal: distrito 7,41 → 3,69 pp; geoespacial 4,38 → 0,66 pp. Ambos pierden
cerca de la mitad al entrar el otro. Juntos aportan 8,07 pp no atribuibles por
separado.

**Lectura para la memoria:** el enriquecimiento geoespacial aporta 4,38 pp por sí
solo, no 0,66. Y es la vía **portable**: un modelo de vivienda + distancias da
18,03% partiendo solo de coordenadas. Las variables construidas no dependen de
una zonificación administrativa concreta, lo que las hace trasladables a otro
mercado sin rehacer la especificación.

### Evaluación (CV sobre entrenamiento)

MdAPE 14,04% · PE10 36,9% · PE20 65,9% · mediana ratio 0,9905 · COD 19,31 ·
R² log 0,8956.

**Dos hallazgos:**

1. **El modelo NO corrige el sesgo por tamaño de la referencia: lo invierte y lo
   amplía.** Referencia: Q1 0,933 → Q5 1,038 (recorrido 0,105). Modelo: Q1
   **1,106** → Q5 **0,943** (recorrido 0,163). Es compresión hacia la media: la
   superficie entra como continua con elasticidad constante y el modelo no puede
   variarla por tramo. **Tratable tramificando la superficie o añadiendo término
   cuadrático; arrastraría el preprocesado. Candidato para el apartado 11.**
2. **El error por decil de precio describe una U pronunciada:** 19,12% en el
   decil 1, mínimo de 10,79% en el 6, **20,82% en el 10**. El segmento de mayor
   exposición en cartera hipotecaria es donde el modelo es menos fiable.
   **Respalda empíricamente el uso declarado en el 1.2**: segmentación por rango
   de valor con derivación a tasador en los extremos.
3. COD 19,31, por encima del umbral IAAO de 15. El modelo lineal tampoco alcanza
   el estándar de consistencia.

---

## Notebook 02 — bloque 7: modelo de alto rendimiento

Instalación: `xgboost>=3.0`. **La 2.1.3 es incompatible con scikit-learn 1.6.1**,
que exige `__sklearn_tags__`; el fallo aparece al insertar el estimador en un
`Pipeline`. Versión final: 3.0.0.

Configuración de partida (500 árboles, profundidad 6, lr 0,05): **9,81%** en CV.
Búsqueda aleatoria, 40 combinaciones × 5 pliegues, 17,5 minutos: **8,99%**.
Ganancia del ajuste: 0,82 pp.

Hiperparámetros seleccionados: n_estimators 887 · max_depth 9 ·
learning_rate 0,0378 · subsample 0,8564 · colsample_bytree 0,9747 ·
min_child_weight 11 · reg_lambda 0,2553.

**Ausentes imputados**, por coherencia con la rama lineal (decisión del usuario;
no se probó la gestión nativa de XGBoost). **`reg:squarederror`**; no se probó
`reg:absoluteerror`. Ambas quedan como palancas si el MdAPE se quedara corto.

**La superficie de error es plana.** Una configuración obtenida en una ejecución
anterior sobre pliegues distintos (n_estimators 1149, max_depth 10, lr 0,0664)
arroja 8,78% sobre los pliegues actuales, dos décimas menos que la seleccionada.
El muestreo aleatorio no garantiza el óptimo del espacio. **Se conserva la
configuración procedente de la búsqueda sobre los pliegues de evaluación**, por
ser el único procedimiento de selección documentado sobre esos datos. Declarado
en el markdown del apartado 7.3.

La búsqueda queda en el notebook con `EJECUTAR_BUSQUEDA = False`; el apartado 7.3
recupera los hiperparámetros del fichero `modelos/busqueda_xgb.joblib` y emplea
valores transcritos como respaldo. Así el `Restart and run all` no gasta 17
minutos.

---

## Notebook 02 — bloque 8: comparativa sobre validación (6.284 viviendas)

| Procedimiento | MdAPE | PE10 | PE20 | Mediana ratio | COD |
|---|---|---|---|---|---|
| Superficie (global) | 33,71% | 14,0% | 29,0% | 1,0100 | 45,79 |
| Superficie × distrito | 17,76% | 30,1% | 54,9% | 1,0099 | 22,85 |
| Superficie × barrio | 14,75% | 35,4% | 63,2% | 1,0005 | 19,89 |
| Modelo lineal (OLS) | 14,11% | 37,1% | 66,0% | 0,9890 | 19,32 |
| **XGBoost** | **8,83%** | **55,1%** | **82,2%** | 0,9974 | **12,91** |

**Resultado central:** XGBoost reduce el error de la referencia un 40,1%; el
lineal, un 4,3%. Sobre la vivienda mediana (268.000 €), de 39.530 € a 23.664 € de
desviación.

> **Corrección aplicada (notebook 03).** El control de coherencia del bloque 0
> detectó que las cifras documentadas no coincidían con el artefacto. Las válidas
> son las de esta tabla: 8,83% de MdAPE, 55,1% de PE10 y COD de 12,91. Quedan sin
> validez el 8,77% / 55,3% / 12,93 anotados antes, y el 8,66% de la síntesis del
> bloque 8, anterior a la unificación de semilla. **La fuente de verdad es
> `avm_madrid.joblib`.** La diferencia entre ambos modelos no responde a la información
disponible, que es idéntica, sino a la capacidad de combinarla sin restricción
aditiva.

**Generalización verificada:** CV → test da 14,04 → 14,11 (lineal) y
8,97 → 8,83 (XGBoost).

**COD:** XGBoost es el único procedimiento por debajo del umbral IAAO de 15.

**El sesgo por tamaño se elimina.** Recorrido del ratio entre quintiles extremos
de superficie: referencia 0,105 · lineal 0,154 · **XGBoost 0,012**. Los árboles
no imponen elasticidad constante entre superficie y precio, que era la causa del
sesgo del lineal.

**La U del error por decil persiste pero se aplana:** lineal de 19,07% a 21,25%
en los extremos con mínimo de 10,95%; XGBoost de 12,39% a 10,72% con mínimo de
7,89%. La mejora es máxima donde el lineal fallaba más: **10,53 pp en el decil
superior**, 7,04 en el noveno.

**Criterio operativo para el 1.2.** PE10 de XGBoost por decil: 55–61% en los
deciles 2 a 9, frente a 42,8% (decil 1) y 47,2% (decil 10). Sugiere valoración
automatizada sin intervención profesional en el rango aproximado de
**120.000 – 900.000 €**, con derivación a tasador fuera de él.

**Figura `06_comparativa_modelos.png`:** dos paneles — barras de MdAPE por
procedimiento y curva de error por decil para ambos modelos. Sin línea de umbral,
redundante con las barras.

**Material para el apartado 8 (trade-off).** El coste de la interpretabilidad
está cuantificado: **5,28 pp de MdAPE, 18,0 pp de PE10**, y un COD que no alcanza
el estándar.

> **Corrección del diagnóstico de `ISINTOPFLOOR` (notebook 03, bloque 4).** Se
> anotó aquí que el efecto del ático se invierte según la altura del edificio y
> que el modelo aditivo lo promedia a cero. **Es incorrecto.** La comparación que
> lo sostenía enfrentaba áticos con primeras plantas sin condicionar por altura,
> y confundía el efecto de la posición con el de la localización: los edificios
> bajos son periféricos y baratos. Condicionando por altura, la última planta es
> más cara en los cuatro tramos.
>
> El indicador es irrelevante en ambos modelos (SHAP 0,045%, permutación
> 0,016 pp) por una razón más simple: solo el 24,3% de las viviendas que lo
> declaran tienen planta coincidente con la altura catastral.
>
> **El caso del apartado 8 pasa a ser `FLOORCLEAN`.** Su contribución recorre de
> −1,52% (planta intermedia, edificio ≤3 alturas) a +5,50% (última planta,
> edificio ≥9), con inversión de signo en la planta intermedia. El lineal estima
> +0,63% no significativo.

---

## Notebook 02 — bloque 9: guardado

`modelos/avm_madrid.joblib` (3,8 MB): ambos modelos con su preprocesado
incorporado, métricas sobre validación, error por decil, coeficientes del lineal
con etiquetas legibles, variables de entrada con su tipo, hiperparámetros y
metadatos (ámbito, tamaños, semilla, versiones de scikit-learn y XGBoost).
Verificado que ambos reproducen sus predicciones tras deserializar.

`modelos/validacion_predicciones.gpkg`: las 6.284 viviendas de validación con
geometría, `LOCATIONID`, `LOCATIONNAME`, `DISTRITO`, superficie, precio y las
predicciones y ratios de ambos modelos. Es la entrada del notebook 03.

**Decisión de productivización tomada (ver «App web» más abajo).** No hay
selector de modelo: la app emite la valoración de XGBoost con su cascada y ofrece
la del lineal como contraste en segundo plano, con la discrepancia entre ambas.
Así no contradice la conclusión del apartado 8 y muestra las dos
interpretabilidades.

---

## Semilla unificada

`SEMILLA = SEED = 2018` gobierna partición, preprocesado, pliegues de validación
cruzada, búsqueda de hiperparámetros y estimación de los modelos. Durante el
desarrollo convivieron dos semillas (2018 en los bloques 0-3, 12345 en los 4-9);
se unificó y se reejecutó todo el notebook, incluida la búsqueda. Las cifras
anteriores a la unificación quedan sin validez.

**Corrección a una anotación previa:** `y_log` y `y_anyo` NO son residuos sin
uso. Son variables de trabajo del bloque 2, empleadas en el análisis de
tramificación.

## Pendiente para los notebooks siguientes

- Tramificar la superficie o añadir término cuadrático para corregir el sesgo por
  tamaño del modelo lineal. Arrastraría el preprocesado; candidato al
  apartado 11.
- Ampliar el rango de `max_depth` en la búsqueda de hiperparámetros. Descartado
  por no alterar las conclusiones.

## Referencias cuantitativas para la modelización

**Cifras definitivas, recalculadas sobre validación en el bloque 5.**

| Referencia | Error relativo mediano |
|---|---|
| Superficie sola (global) | 33,71% |
| Precio unitario del distrito × superficie | 17,76% |
| Precio unitario del barrio × superficie | **14,75%** |

La tercera es la referencia exigente: **un AVM que no mejore de forma apreciable
ese 14,75% no justifica su complejidad frente a una regla de cálculo
elemental.** Equivale a unos 39.500 € de desviación sobre la vivienda mediana de
268.000 €.

**Nota sobre la partición.** Con una fila por vivienda, la partición aleatoria
por filas es admisible. Un experimento sobre el conjunto sin deduplicar muestra
que dicha partición **subestima el error mediano en 0,8 puntos** (9,35% frente a
10,14%), porque el mismo inmueble aparece en entrenamiento y validación con
anuncios distintos. Para un AVM destinado a tasación de garantías, esa
subestimación daría a un comité de riesgos una confianza que el modelo no tiene.

---

## Apartado 9 — análisis de equidad: ejecutado

**Precondición verificada.** El Atlas de Distribución de Renta de los Hogares
publica la serie 2015-2023 a nivel de sección censal. Las 2.443 secciones de
Madrid capital vigentes en 2018 tienen todas dato de renta. No hubo que recurrir
a la salida alternativa de ordenar barrios por precio unitario, y el enunciado
del 9.2 del índice no necesitó corrección.

**Fuentes (INE, licencia CC BY 4.0), descarga manual.** Documentadas en la
cabecera del bloque 5 del notebook 03:

1. Atlas de Distribución de Renta de los Hogares, serie 2015-2023 → Resultados
   por municipios, distritos y secciones censales por provincias → Madrid →
   «Indicadores de renta media y mediana». Indicador: **renta neta media por
   persona**. Periodo: **2018**. CSV separado por `;`, codificación ISO-8859.
   → `data/raw/ine_renta_madrid_2018.csv` (580 KB, 4.788 filas)
2. Cartografía de secciones censales, fichero nacional **del año 2018**
   (`SECC_CE_20180101`, seccionado del Censo Electoral a 1 de enero), shapefile
   en UTM huso 30. Descarga en `https://www.ine.es/dyngs/DAB/index.htm?cid=1389`.
   → `data/raw/seccionado_2018/` (5 ficheros, 105 MB el `.shp`)

**Por qué el año importa.** Las secciones se redelimitan anualmente. Cruzar la
renta de 2018 con otra cartografía produciría cifras plausibles y erróneas sin
error visible.

**Trampas del CSV, resueltas en el código.** Codificación `latin-1`, formato
numérico español (`27.785` son 27.785 €) y código de sección embebido en la
columna de texto (10 primeros caracteres, leído como texto).

**Desajuste declarado.** El fichero de renta trae 2.493 secciones y el seccionado
2018 tiene 2.443. Las 50 sobrantes son subdivisiones posteriores: el Atlas refiere
la serie completa a un seccionado más reciente. Verificado que la inclusión es en
un solo sentido —cero secciones de 2018 sin renta—, de modo que el ámbito queda
cubierto por completo. Una vivienda cayó sobre un límite y se asignó por
proximidad.

**Cartografía recortada.** El nacional se filtra a Madrid en la primera ejecución
y se conserva en `data/processed/secciones_madrid_2018.gpkg` (2 MB). El recorte
va dentro del notebook, de modo que sigue siendo reproducible de punta a punta.

### Resultados

| Quintil de renta | Renta mediana | Precio mediano | Ratio | MdAPE | PE10 |
|---|---|---|---|---|---|
| 1 | 9.461 € | 136.000 € | 1,014 | 9,01% | 53,3% |
| 2 | 12.246 € | 184.000 € | 0,997 | 9,46% | 52,5% |
| 3 | 16.328 € | 284.000 € | 0,994 | 8,37% | 57,3% |
| 4 | 20.562 € | 413.000 € | 0,995 | 8,32% | 58,0% |
| 5 | 28.291 € | 682.000 € | 0,993 | 8,86% | 54,6% |

**No hay sesgo por renta.** Recorrido del ratio: **0,021 por renta frente a 0,081
por precio**. El desvío existente es compresión hacia la media —que opera sobre
el precio— y se diluye al ordenar por renta. La advertencia anotada antes de ver
las cifras se cumplió, y el contraste renta/precio es lo que permite separarlo.

**Residuo a vigilar:** 1,4% de sobrevaloración en el quintil de renta inferior,
unos 1.900 € sobre su vivienda mediana. Dirección desfavorable para el negocio.
No justifica corregir el modelo; sí incorporarlo al control periódico.

**Sesgo de la muestra, a declarar.** Renta mediana de las secciones con vivienda
anunciada: 16.328 € frente a 14.657 € del conjunto del municipio. El análisis se
refiere al parque anunciado, no al residencial.

### Análisis territorial: descartado

Se ejecutó y se retiró. Índice de Moran sobre 83 barrios con k vecinos más
próximos: **I = −0,051 (p = 0,277)** para el ratio, **+0,034 (p = 0,203)** para
el error, estable entre k = 4 y k = 10. Sin estructura espacial.

Motivos de la retirada: no aportaba evidencia adicional al contraste
renta/precio, obligaba a dos dependencias más (`libpysal`, `esda`) y consumía
media cara. El índice pasa a un apartado 9 sin subdivisión.

**Nota técnica por si se recupera:** la contigüidad de reina no funciona. El
dataset no trae contornos de barrio, y las envolventes convexas de las viviendas
no se tocan entre sí —las viviendas están dentro del barrio, no en su frontera—,
de modo que los 83 barrios salen como islas y el índice da `nan`. Hay que usar
vecindad por k vecinos sobre centroides, o descargar los contornos
administrativos del portal de datos de Madrid.

**Hipótesis contrastada y rechazada.** El mapa sugería que el desvío se
concentraba en la almendra central. Medido: correlación de Spearman entre desvío
absoluto y distancia al centro de −0,041 (p = 0,712); desvío mediano de 1,18 pp
en la mitad interior frente a 0,94 pp en la exterior. Artefacto de percepción por
densidad desigual de puntos. No entra en la memoria.

---

## Notebook 03 — estructura final

```
0. Entorno y carga                                    → —
1. Importancia global (1.1 SHAP · 1.2 permutación · 1.3 figura)  → memoria 7.1
2. Explicación individual (2.1 casos · 2.2 cascadas)  → memoria 7.2
3. Intrínseca frente a post-hoc                       → memoria 7.3
4. Discusión del trade-off (contribución de la planta) → memoria 8
5. Renta por sección censal                           → memoria 9
6. Equidad por nivel de renta                         → memoria 9
7. Material para la app y la memoria                  → memoria 10
```

**El artefacto del notebook 02 no guarda `X_test`.** El notebook 03 reconstruye
la partición desde el parquet con `SEED = 2018` y verifica la reconstrucción
aplicando ambos modelos y contrastando con las predicciones del GeoPackage.
Coinciden al límite de la precisión simple.

**Método de interpretabilidad post-hoc: SHAP, decidido tras analizar
alternativas.** Se descartaron LIME (inestable, sin aditividad), árbol sustituto
(no aporta sobre SHAP) y contrafactuales (fuera del índice). Se añadió la
importancia por permutación como segunda medida, porque SHAP mide atribución y no
acierto.

**TreeSHAP en la implementación nativa de XGBoost** (`pred_contribs=True`), no la
librería `shap`: mismo algoritmo exacto, segundos en lugar de minutos, y una
dependencia menos. Variante `tree_path_dependent`, sin muestra de fondo, dada la
colinealidad documentada.

### Resultados del bloque 1 (memoria 7.1)

| Bloque | Atribución SHAP | Δ MdAPE | Variables |
|---|---|---|---|
| Vivienda | 56,1% | 30,8 pp | 23 |
| Geoespacial | 34,9% | 21,1 pp | 7 |
| Distrito | 4,8% | 3,0 pp | 1 |
| Catastro | 4,2% | 1,6 pp | 4 |

- **Spearman 0,957** entre ambos órdenes. El modelo atribuye sus valoraciones a
  las mismas variables de las que depende para acertar. Argumento de gobernanza,
  y el hallazgo del apartado; la discrepancia que yo esperaba no se produjo.
- **Las cuatro variables construidas en el notebook 01 aportan 12,7 pp**, frente
  a 8,4 de las distancias de origen y 3,0 del distrito. Es la cuantificación del
  eje diferencial.
- **El distrito no se hunde** en permutación (sexta posición, 3,02 pp): hay
  información administrativa que las coordenadas no reconstruyen. Corrige una
  lectura previa.
- **Orientaciones confirmadas irrelevantes** por tercera vía independiente.
- Descienden por redundancia: aire acondicionado (−7), calidad constructiva (−5),
  jardín (−6, efecto sobre el error indistinguible de cero).
- **La columna «% del deterioro» no es una descomposición.** Los deltas de
  permutación no son aditivos. Darla como orden de magnitud o no darla.

### Resultados del bloque 2 (memoria 7.2)

Tres casos por criterio calculado, no por elección: mediana dentro del rango
operativo con error <5%, y percentiles 99 y 1 del ratio.

- **Adelfas (55 m²):** el modelo descuenta 84.484 € por tamaño y recupera
  34.065 € por contexto de barrio. Es la interacción que el aditivo no puede
  representar, y apareció en el primer caso sin buscarla.
- **Colina (75 m², anunciada a 161.000 €, valorada en 288.295 €):** el reparto es
  coherente; el barrio tiene ratio mediano 0,993 y error del 6,5%. El anuncio
  pide 2.147 €/m² donde el barrio está a 3.787. **La explicación permite
  distinguir error del modelo de precio anunciado atípico.** Es el argumento de
  negocio más fuerte del apartado 7.
- El caso de gama alta se eliminó: el reparto era coherente y no ilustraba nada.
- `descomponer()` es el prototipo de la función que ejecutará la app.

### Resultados del bloque 3 (memoria 7.3)

Sobre 18 atributos binarios: **signo 94%, correlación 0,870, pendiente 1,69.**
Concuerdan en dirección y orden; el lineal estima magnitudes mayores, lectura
coherente con los VIF de 8-9 pero no contrastada.

- Verificado que los efectos del artefacto están **por unidad**, no por
  desviación típica.
- **Descartado por vacío:** la proporción de efectos negativos entre quienes
  declaran el atributo (0,0%–1,7%). El efecto no cambia de signo, solo varía en
  magnitud. El argumento lo sostiene el recorrido, no la inversión.
- Ascensor: **3,4% a 10,1%** entre percentiles 5 y 95, frente al +19% único.

---

## App web — decisiones tomadas

**Formulario:** barrio más nueve características del inmueble. Las siete
variables geoespaciales se derivan del barrio; las dieciocho restantes se fijan
en su valor típico de entrenamiento y se declara en pantalla.

**Salida:** valoración de XGBoost con su cascada; panel secundario con la del
lineal y la discrepancia entre ambas. **Sin selector de modelo**, para no
contradecir la conclusión del apartado 8.

**Implementación:** `app/app.py` con Streamlit, no un notebook. Carga
`avm_madrid.joblib` y `avm_app.joblib`, sin reentrenar.

**Aproximación declarada.** Las variables geoespaciales se toman como mediana del
barrio. Coeficiente de variación interno: 0,07 (distancia al centro), 0,13
(Castellana), 0,26 (metro en 1 km y densidad de oferta), **0,41 (distancia al
metro)**. Las tres inestables aportan menos de 1,5 pp al error en conjunto, de
modo que el efecto es acotado. Limitación del prototipo, a declarar en el 10.

### Artefactos del notebook 03

`modelos/avm_app.joblib` (10 KB): perfil de localización de 135 barrios calculado
**sobre entrenamiento**, 18 valores por defecto, correspondencia columna→variable
para ambos modelos (55 y 66), etiquetas, clasificación por bloque, valor base de
XGBoost (12,5871 en log, 292.754 €) y rango operativo.

`modelos/resultados_notebook03.joblib` (7 KB): las tablas del análisis, para
verificar cifras al redactar sin reejecutar.

**Figuras:** `07_importancia_global`, `08_explicacion_individual`,
`09_intrinseca_vs_posthoc`, `10_interaccion_planta`. La `11_equidad_territorial`
debe borrarse: ya no la genera nada.

---

## Pendientes

- Borrar `figuras/11_equidad_territorial.png`.
- `Restart and run all` del notebook 03 tras los recortes.
- La app debe replicar el criterio de asignación al polígono más próximo para
  viviendas fuera de la zonificación.
- Decidir el tratamiento de los 58 registros sin dormitorios y sin declararse
  estudio.
- Revisar en el apartado 3.2 de la memoria la frase sobre los seis barrios bajo
  umbral (sobre entrenamiento son ocho, y dos de ellos son urbanizaciones
  residenciales).

---

## Bibliografía incorporada durante el desarrollo

- IAAO Statistical Tools and Measures Task Force (2023). *A review of vertical
  equity measures in property assessments*. JPTAA 20(2).
- McMillen, D. y Singh, R. (2023). *Measures of vertical inequality in
  assessments*. Journal of Housing Economics 61, 101950.

---

## Recordatorios de la guía

- Memoria: máximo 20 caras (sin portada, índice ni anexos).
- **Estado actual: exceden su presupuesto los apartados 3, 5, 6, 7 y 8.** Poda
  pendiente, con la memoria completa delante. El 9 se redujo ya en el análisis al
  descartar el diagnóstico territorial.
- Informe entendible por perfil de negocio.
- Aportar más que un AutoML → el enriquecimiento geoespacial y la
  interpretabilidad son los ejes diferenciales. La investigación sobre la
  identidad de los registros y el procedimiento de descarte de variables
  construidas también lo son.
- Proyecto reproducible → probar `Restart session and run all` en cada notebook
  antes de darlo por cerrado.
- Vídeo de máximo 5 minutos en `.mp4`.
- Dar acceso al repositorio a Carlos Ortega y Santiago Mota.
