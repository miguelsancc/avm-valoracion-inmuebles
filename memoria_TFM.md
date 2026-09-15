# Memoria del TFM — borrador de trabajo

**Título provisional:** Modelo de valoración automatizada de inmuebles (AVM):
interpretabilidad, equidad y productivización

---

> **Qué es este documento.** El borrador de la memoria, redactado como informe
> para un perfil de negocio. No es un resumen del notebook ni un registro de
> decisiones técnicas: eso vive en `estado_proyecto_TFM.md`.
>
> **Cómo se usa.** Se redacta un apartado únicamente cuando el análisis que lo
> sustenta está cerrado. Los apartados pendientes conservan su presupuesto de
> extensión y una nota sobre qué falta. El texto final se traslada a Word al
> terminar.
>
> **Regla de oro.** Si al redactar un apartado hace falta consultar el notebook
> para saber qué se hizo, ese apartado todavía no está listo para escribirse.

---

## Presupuesto de extensión

Límite: **20 caras** sin portada, índice ni anexos. A tamaño 10-11 en Verdana o
Arial, una cara de prosa admite en torno a 500 palabras; con figuras y tablas,
bastante menos. Las cifras siguientes son orientativas y se ajustan sobre la
marcha, pero el total no se mueve.

| Apartado | Caras | Palabras aprox. | Estado |
|---|---|---|---|
| 1. Introducción y motivación | 1,5 | 750 | Pendiente |
| 2. El conjunto de datos | 1,5 | 700 | **2.1 y 2.3 redactados** |
| 3. Análisis exploratorio | 2,0 | 800 | **Redactado — excede el presupuesto** |
| 4. Enriquecimiento geoespacial | 1,5 | 650 | **Redactado** |
| 5. Preparación y feature engineering | 1,5 | 650 | **Redactado** |
| 6. Modelización | 4,0 | 1.700 | **Redactado** |
| 7. Interpretabilidad post-hoc | 2,5 | 1.100 | **Redactado — excede el presupuesto** |
| 8. Discusión del trade-off | 1,0 | 500 | **Redactado — excede el presupuesto** |
| 9. Análisis de equidad | 1,5 | 650 | **Redactado** |
| 10. Productivización | 1,5 | 650 | Pendiente |
| 11. Conclusiones | 1,5 | 750 | Pendiente |
| 12. Bibliografía | 0,5 | — | Pendiente |
| **Total** | **20,5** | | |

El total se pasa medio folio. El apartado 9 se ha reducido ya en el propio
análisis: el diagnóstico territorial por barrio con índice de Moran se descartó
tras comprobar que no aportaba evidencia adicional al contraste entre renta y
precio, lo que devuelve media cara al presupuesto.

> **Aviso de extensión.** Cinco apartados exceden su presupuesto. El 3 alcanza
> unas 1.400 palabras frente a 800, el 5 unas 950 frente a 650, y el 6 unas
> 3.400 frente a 1.700, repartidas entre un 6.1 que reúne protocolo de
> validación, escala logarítmica, retro-transformación, métricas y modelos de
> referencia, y unos 6.2 a 6.4 con el diagnóstico de ambos modelos y la
> comparativa. El 7 alcanza unas 1.400 palabras frente a 1.100, repartidas entre
> tres subapartados con una figura cada uno, y el 8 unas 700 frente a 500.
>
> La poda pendiente debe decidir qué se conserva en el cuerpo y qué pasa al
> anexo. Candidatos a recorte: el detalle del contraste de republicación en 3.3,
> la tabla de barrios extremos en 3.2, el procedimiento de descarte de variables
> en 4, en el 5 la tabla de intervalos de distancia y el detalle de la
> imputación, y en el 6.1 la justificación de la formulación logarítmica y la
> discusión del marco europeo, que se solapa con el apartado 1.2.

**Figuras previstas** (cada una consume espacio del apartado que la contiene):

| Figura | Apartado | Estado |
|---|---|---|
| Distribución de precios y precio unitario | 3.1 | **Disponible** |
| Relación entre superficie y precio | 3.1 / anexo | **Disponible** |
| Mapa de coropletas: precio unitario por barrio | 3.2 | **Disponible** |
| Contraste de republicación entre trimestres | 3.3 | **Disponible** |
| Capacidad explicativa de las variables | anexo | **Disponible** |
| Calidad catastral y periodo de construcción | anexo | **Disponible** |
| Comparativa de rendimiento entre modelos y referencias | 6.4 | Disponible |
| Importancia global de variables | 7.1 | Pendiente |
| Explicación de una predicción individual | 7.2 | Pendiente |
| Error del modelo frente a renta de barrio | 9.2 | Pendiente |
| Arquitectura de la aplicación | 10.1 | Pendiente |

Del bloque 3 del notebook salieron cuatro figuras y del bloque 4 una. A la
memoria van dos: la distribución de precios y el mapa. Las restantes, al anexo.

---

# 1. Introducción y motivación

## 1.1. Contexto: la valoración automatizada de inmuebles

*Pendiente. No depende de ningún notebook.*

## 1.2. Caso de negocio

*Pendiente. Eje: tasación de garantías hipotecarias y gestión de riesgo.
Conviene mencionar el ámbito de aplicación del modelo como cuestión relevante
en la validación de modelos internos, que enlaza con el apartado 6.*

## 1.3. Objetivos y preguntas de investigación

*Pendiente. Se redacta al final, cuando se sepa qué preguntas han quedado
efectivamente respondidas.*

---

# 2. El conjunto de datos

## 2.1. Descripción del dataset y ámbito del trabajo

*Redactado. Presupuesto: 300 palabras.*

El trabajo se apoya en `idealista18`, un conjunto de datos abiertos publicado
por el portal inmobiliario idealista en colaboración con las universidades
Politécnica de Cartagena y McMaster. Recoge 189.923 anuncios de venta de
vivienda correspondientes a Madrid, Barcelona y Valencia durante el ejercicio
2018, distribuidos en cuatro capturas trimestrales. Cada anuncio incorpora 42
variables que describen la vivienda, el edificio según información catastral y
su localización geográfica.

La unidad de observación es el anuncio y no la vivienda. Un mismo inmueble puede
figurar en varios registros cuando se comercializa simultáneamente a través de
varias agencias o cuando su anuncio se renueva. Esta circunstancia, junto con
las limitaciones del identificador de inmueble, se analiza en el apartado 3.3.

**Ámbito seleccionado.** El desarrollo se restringe a Madrid y al cuarto
trimestre de 2018, lo que arroja un conjunto de trabajo de 31.418 viviendas.

La restricción geográfica responde a que los tres mercados no son directamente
comparables entre sí, de modo que un modelo conjunto describiría de forma
imprecisa cada uno de ellos, y a que Madrid presenta la mayor granularidad
espacial disponible, con 135 unidades de barrio frente a 69 y 73 de las otras
dos ciudades. Se añade un motivo técnico: las tres ciudades se sitúan en husos
UTM distintos —Barcelona en el 31 Norte frente al 30 Norte de Madrid y
Valencia—, de modo que un tratamiento conjunto obligaría a proyectar alguna de
ellas fuera de su huso y degradaría la precisión de las distancias sobre las que
se apoya el enriquecimiento geoespacial del apartado 4.

La restricción temporal se justifica en el apartado 3.3, por derivarse del
análisis de la estructura del conjunto. El trimestre seleccionado es el de mayor
volumen y su representatividad se ha verificado frente al resto del ejercicio:
las medianas de número de dormitorios, número de baños y año de construcción
coinciden con las del conjunto anual, la superficie difiere en un 1,2% —84
frente a 83 metros cuadrados— y las distancias a puntos de referencia en menos
del 1%; el equipamiento declarado se mantiene dentro de tres puntos y medio
porcentuales y la cobertura espacial alcanza el 92% del territorio cubierto por
el año completo. La única diferencia apreciable es el precio, superior en un
8,3% en importe y en un 6,2% por metro cuadrado, atribuible a la evolución del
mercado y no a un cambio en la composición de la muestra.

## 2.2. Variables disponibles y licencia de uso

*Pendiente. Requiere el conjunto de variables final tras el bloque 5 del
notebook de modelización.*

Contenido previsto: agrupación de las 42 variables por naturaleza (objetivo y
tamaño, características, equipamiento, orientación, información catastral,
localización), licencia ODbL v1.0 y su implicación (la memoria, los gráficos, el
modelo y la aplicación son obras derivadas sujetas únicamente a atribución; el
repositorio publica código y no datos).

Conviene mencionar que la documentación oficial del paquete presenta
inconsistencias —declara 156.016 registros y 57 variables frente a los 94.815 y
42 del objeto distribuido para Madrid, y omite una de las variables de
distancia—, lo que motivó verificar empíricamente cuanto se afirma sobre el
conjunto.

## 2.3. Limitaciones de partida

*Redactado. Presupuesto: 400 palabras. El texto actual las excede y requiere
poda.*

El conjunto presenta siete limitaciones que acotan el alcance de los resultados
y que conviene declarar antes de exponerlos.

**Precio de oferta frente a precio de transacción.** La variable objetivo es el
precio solicitado por el vendedor, no el importe efectivamente escriturado. La
literatura sitúa la diferencia entre ambos en un margen apreciable, y el sesgo
no es uniforme: resulta mayor en los inmuebles que permanecen más tiempo en
comercialización, precisamente aquellos cuyo precio de salida se aleja más del
valor de mercado. Un modelo entrenado sobre precios de oferta estima, por tanto,
la pretensión del vendedor y no el valor realizable, lo que en un contexto de
tasación de garantías aconseja aplicar un ajuste conservador.

**Antigüedad de los datos.** El conjunto corresponde a 2018. Los niveles de
precio estimados no son directamente trasladables al momento actual, si bien las
relaciones entre características y valor presentan mayor estabilidad temporal.
La actualización a una fecha posterior requeriría la aplicación de un índice
externo de precios de vivienda, procedimiento habitual en la práctica del sector
y que se recoge en el diseño de la aplicación del apartado 10.

**Perturbación de las coordenadas.** Las coordenadas facilitadas son
aproximadas, conforme declara la documentación del conjunto. El análisis
realizado permite cuantificar dicha aproximación: los anuncios correspondientes
a un mismo inmueble presentan una separación mediana de 73 metros, con el
percentil 90 situado en 98 metros, lo que resulta compatible con un
desplazamiento aleatorio de hasta unos 50 metros aplicado a cada registro de
forma independiente. Las variables de distancia incorporadas en el conjunto
presentan valores distintos entre anuncios de un mismo inmueble, lo que acredita
que fueron calculadas con posterioridad a la perturbación y arrastran en
consecuencia el mismo error. La consecuencia práctica es que el enriquecimiento
geoespacial no puede operar por debajo de esa resolución: las variables
construidas sobre radios de 500 metros o superiores y los agregados por barrio
resultan robustos, mientras que cualquier magnitud que dependa de identificar el
portal o el lado de la vía quedaría dominada por el ruido.

**Ausencia de variables temporales por debajo del trimestre.** El conjunto no
incorpora fecha de publicación ni tiempo de permanencia en el mercado. Esta
última constituiría la variable más informativa para detectar sobrevaloración,
dado que la permanencia prolongada señala precisamente un precio de salida
excesivo.

**Acotación del precio unitario.** El precio por metro cuadrado se sitúa entre
805 y 9.994 euros, sin que ningún anuncio de Madrid alcance los 10.000 euros por
metro. La cola superior decrece de forma continua hasta ese valor sin presentar
acumulación, lo que indica que los registros situados fuera del rango fueron
excluidos en origen y no reasignados al límite.

Procede precisar el alcance de esta exclusión, que no equivale a la del segmento
de mayor importe. El conjunto contiene vivienda de precio elevado —el máximo
observado asciende a 8.133.000 euros— por vía de la superficie, que alcanza los
934 metros cuadrados. Lo excluido es el segmento de mayor precio por metro
cuadrado, esto es, el producto de lujo por calidad y ubicación. La distinción
resulta relevante para el caso de uso: una garantía de importe elevado asociada
a una vivienda de gran superficie y precio unitario moderado queda dentro del
ámbito del modelo, mientras que la asociada a una vivienda de superficie
reducida en el segmento de lujo queda fuera.

**Censura de la planta.** La variable que recoge la planta de la vivienda está
limitada al valor 11, en el que se agrupan todas las plantas superiores. La
limitación no consta en la documentación del conjunto y se deduce del
comportamiento de la distribución: la frecuencia decrece de forma continua hasta
la planta décima y repunta en la undécima, existiendo además 1.733 viviendas en
edificios de más de once plantas. La variable no permite en consecuencia
distinguir entre plantas altas dentro del segmento de edificios de mayor altura,
precisamente donde el efecto de la altura sobre el precio resulta más acusado.

**Unidad espacial.** Las 135 unidades empleadas como barrio corresponden a la
zonificación comercial del portal y no a la división administrativa oficial del
municipio, que comprende 131 barrios. Las agrupaciones difieren en algunos
casos, por lo que el enlace con fuentes estadísticas oficiales se realiza a
nivel de distrito, identificador que sí resulta directamente extraíble.

---

# 3. Análisis exploratorio de datos

## 3.1. Análisis descriptivo y distribución de precios

*Redactado. Presupuesto: 350 palabras.*

La vivienda mediana del conjunto se sitúa en 268.000 euros y 82 metros
cuadrados, con un precio unitario de 3.565 euros por metro cuadrado. La
distribución del precio presenta una asimetría acusada: la media, 406.266 euros,
supera a la mediana en un 52%, y la vivienda situada en el percentil 99
multiplica por 8,3 el valor de la vivienda central.

La asimetría tiene consecuencia directa sobre la evaluación del modelo. Un error
de 50.000 euros resulta despreciable sobre una vivienda de dos millones y
determinante sobre una de cien mil, por lo que la valoración debe medirse en
términos de error relativo y no absoluto. La transformación logarítmica reduce
el coeficiente de asimetría del precio de 4,20 a 0,55 y el de la superficie de
3,19 a 0,52, lo que respalda la formulación logarítmica habitual en los modelos
hedónicos de precios.

*[Figura: distribución del precio y del precio unitario]*

**Relación con la superficie.** La superficie construida constituye el
determinante inmediato del precio, si bien la relación no es de
proporcionalidad estricta: la elasticidad estimada asciende a 1,14, de modo que
duplicar la superficie multiplica el precio por 2,20. El metro cuadrado de las
viviendas de mayor tamaño resulta, en promedio, más caro.

Dos magnitudes describen esta relación y conviene leerlas de forma conjunta. La
superficie explica el 74% de la varianza del precio, proporción que podría
sugerir que la aportación pendiente del resto de variables es residual. Sin
embargo, la valoración basada exclusivamente en la superficie presenta un error
relativo mediano del 33,7%, equivalente a unos 90.000 euros sobre una vivienda
de precio mediano. La discrepancia se explica por el peso que las viviendas de
precio elevado tienen sobre la varianza: sobre el grueso del mercado, la
superficie por sí sola no proporciona una valoración utilizable.

**Estructura de submercados.** La distribución del precio unitario presenta dos
máximos, en torno a 2.000 y 4.000 euros por metro cuadrado, lo que sugiere la
superposición de mercados con niveles de precio distintos. La relación entre
precio unitario y superficie confirma esa lectura al describir una U: el precio
unitario mediano parte de 4.581 euros por metro cuadrado en las viviendas de
menor tamaño, desciende hasta 2.595 en el entorno de los 70 metros cuadrados y
remonta hasta 4.685 en las de mayor superficie.

El patrón no responde a un efecto del tamaño sobre el valor del metro cuadrado
sino a la asociación entre tamaño y localización: la distancia mediana al centro
describe el perfil inverso, con la vivienda pequeña concentrada en el casco
histórico, la de tamaño intermedio en los desarrollos periféricos y la de mayor
superficie de nuevo en las zonas centrales. La observación motiva el análisis
espacial del apartado siguiente.

## 3.2. Análisis por distrito y barrio

*Redactado. Presupuesto: 350 palabras.*

*Nota: el índice recogía este apartado como «Análisis por ciudad y por barrio».
Al restringirse el ámbito a Madrid, el análisis es por distrito y barrio.*

La localización constituye el determinante principal del valor. El precio
unitario mediano por barrio recorre de 1.241 a 7.595 euros por metro cuadrado:
el barrio más caro multiplica por 6,12 al más barato. Ninguna característica de
la vivienda produce un efecto de magnitud comparable, de modo que dos inmuebles
de prestaciones idénticas separados por unos kilómetros pueden diferir en un
factor de seis en su valor unitario.

La agregación por distrito reduce ese recorrido a un factor de 3,39, lo que
revela una heterogeneidad interna apreciable dentro de cada distrito y aconseja
emplear el barrio como unidad de análisis. En términos cuantitativos, el barrio
explica el 72,7% de la variación del precio unitario frente al 65,1% del
distrito, y frente al 14,5% atribuible a la superficie construida.

*[Figura: mapa de coropletas del precio unitario mediano por barrio]*

**Geometría del gradiente.** El precio no decrece de forma radial desde el
centro sino en torno a un eje: la banda de mayor valor recorre la ciudad de
norte a sur siguiendo el trazado del Paseo de la Castellana y su prolongación, y
se extiende hacia el noroeste. El sector meridional conforma una masa continua
de precio reducido, con transiciones abruptas entre barrios contiguos que
alcanzan diferencias superiores al cincuenta por ciento.

La observación resulta coherente con el análisis de variables: la distancia al
eje de la Castellana presenta mayor capacidad explicativa que la distancia al
centro de la ciudad, y ambas se comportan de forma marcadamente no lineal.

**Referencia para la modelización.** La valoración obtenida al aplicar el precio
unitario mediano de la zona a la superficie del inmueble —procedimiento habitual
en ausencia de modelo— presenta un error relativo mediano del 14,75%, frente al
33,71% de la estimación basada únicamente en la superficie. Dos magnitudes
elementales reducen por tanto el error a menos de la mitad.

La cifra delimita la exigencia aplicable al trabajo: un sistema de valoración
automatizada que no mejore de forma apreciable ese 14,75% no justificaría su
complejidad frente a una regla de cálculo que cabe en una línea. Ambas
magnitudes proceden del recálculo practicado en el apartado 6.1 sobre el
conjunto de validación, donde se detalla asimismo el nivel intermedio de
agregación por distrito.

**Cobertura muestral.** Se establece un umbral de treinta viviendas por barrio
para la estimación de agregados por zona. Afecta a seis barrios que reúnen el
0,28% del conjunto, correspondientes a suelo no residencial —el monte de El
Pardo, el recinto aeroportuario y la base aérea de Cuatro Vientos— o a
urbanizaciones de baja densidad. Sus viviendas se conservan en el conjunto: la
limitación afecta a la estimación de agregados, no a la validez de los registros
individuales. Sobre el conjunto de entrenamiento, que comprende el ochenta por
ciento de las observaciones, el umbral alcanza a ocho barrios y al 0,49% de los
registros.

## 3.3. Calidad del dato e identidad de los registros

*Redactado. Presupuesto: 450 palabras. El texto actual las excede y requiere
poda; el candidato natural es el detalle del contraste de republicación.*

El conjunto identifica cada inmueble mediante un código que la documentación
describe como único por vivienda. La verificación de esta propiedad reveló que
no se cumple: los 94.815 anuncios de Madrid corresponden a 75.804
identificadores distintos.

El análisis de las repeticiones permitió establecer su naturaleza. Los registros
que comparten identificador coinciden en la totalidad de las variables
catastrales, en la planta en el 95,2% de los casos, en el número de dormitorios
en el 98,2% y en el de baños en el 99,1%, con una diferencia de precio del 4,3%
en mediana. Se trata, por tanto, de varios anuncios de un mismo inmueble dentro
de un trimestre, resultado de la comercialización simultánea por distintas
agencias o de la renovación del anuncio.

Una segunda observación resultó más relevante para el diseño del trabajo: ningún
identificador figura en más de un trimestre, pese a que la documentación
establece que un inmueble no vendido reaparece en periodos posteriores. Para
contrastar ambas afirmaciones se construyó un identificador alternativo basado
en los atributos que no varían al renovarse un anuncio. El contraste confirmó la
existencia de reapariciones: 2.323 de esas huellas figuran en más de un
trimestre, volumen que la tasa de error del procedimiento no alcanza a explicar.
El identificador publicado no permite, en consecuencia, el seguimiento temporal
de una vivienda.

El procedimiento presenta, sin embargo, una tasa medida de coincidencias entre
inmuebles distintos del 4,79%, y no permite determinar cuáles de las 2.323
coincidencias corresponden a reapariciones efectivas y cuáles a viviendas
distintas pero indistinguibles en los atributos disponibles. Fundamentar sobre
él la depuración del conjunto habría supuesto eliminar inmuebles distintos y
conservar duplicados.

Se optó por restringir el ámbito a una única captura trimestral, en la que el
identificador está verificado y la depuración se apoya en evidencia directa. El
conjunto de trabajo resulta de conservar, por identificador, el anuncio cuyo
precio es más próximo a la mediana del grupo: 44.270 anuncios del cuarto
trimestre que corresponden a 31.418 viviendas.

*[Figura: contraste de variación de precio entre trimestres, observado frente a
grupo de control]*

**Verificación de rangos.** La revisión de los valores admisibles identificó 65
registros con valores materialmente imposibles, sobre un total de 31.418:
recuentos de baños nulos o superiores a diez, recuentos de dormitorios
superiores a quince, años de construcción catastral anteriores a 1800 y alturas
de edificio nulas. En todos los casos se trata de valores ausentes codificados
numéricamente o de errores de registro, y se convierten en ausentes.

**Coherencia de los registros extremos.** No procede depurar valores atípicos de
la variable objetivo: un precio elevado no constituye un error sino una vivienda
de valor elevado, y su exclusión reduciría el ámbito de aplicación del modelo
precisamente en el segmento donde se concentran las garantías de mayor importe.
Sí se verificó, en cambio, que los registros extremos presentan un precio
compatible con el resto de sus características. El contraste no identificó
ninguna incidencia: los casos de mayor desviación respecto a la mediana de su
barrio corresponden a viviendas cuya tipología difiere de la predominante en la
zona, y ningún registro presenta un importe incompatible con una operación de
compraventa. No se elimina ningún registro por esta vía.

---

# 4. Enriquecimiento geoespacial

*Redactado. Presupuesto: 650 palabras.*

## 4.1. Fundamento: la localización como driver del precio

El apartado 3.2 estableció que el barrio explica el 72,7% de la variación del
precio unitario, frente al 14,5% atribuible a la superficie. El conjunto
incorpora tres variables de localización —distancia al centro, a la estación de
metro más próxima y al eje de la Castellana— cuya reconstrucción no aportaría
información nueva. El enriquecimiento debe generar, por tanto, variables que el
conjunto no proporciona.

Con carácter previo, las coordenadas se transforman de un sistema de referencia
expresado en grados a otro expresado en metros. Sobre coordenadas geográficas,
la distancia euclídea carece de significado físico, dado que un grado de latitud
y un grado de longitud no equivalen a la misma distancia real. La corrección de
la transformación se verificó reconstruyendo una de las variables de distancia
ya presentes en el conjunto, que se reproduce con una correlación de 0,999996.

## 4.2. Variables construidas

Se construyeron nueve variables atendiendo a dos carencias de las disponibles.

La primera es la distinción entre proximidad y conectividad. La distancia a la
estación de metro más próxima no diferencia entre una vivienda con una única
estación en su entorno y otra con varias, pese a que la accesibilidad efectiva
difiere. Se construyeron a tal efecto densidades de estaciones por radio y
distancias a la segunda y tercera estación más próximas.

La segunda es la caracterización del entorno. Ni la densidad de la zona ni el
tipo de producto predominante figuran en el conjunto, pese a constituir
determinantes reconocidos del valor. Se construyeron densidades de anuncios por
radio y agregados de antigüedad y superficie mediana por barrio.

El error de localización de hasta cincuenta metros documentado en el apartado
2.3 fija el suelo de resolución utilizable, por lo que los radios empleados
parten de los quinientos metros.

De las nueve variables construidas se retuvieron cuatro, tras verificar que la
supresión de las restantes no altera el error del modelo. Las descartadas
resultaron redundantes: la distancia a la segunda estación de metro presenta una
correlación de 0,947 con la distancia a la primera, de modo que la proximidad a
una estación implica en la práctica la proximidad a las siguientes, y los pares
de variables construidas sobre dos radios distintos no aportan información
diferenciada entre sí.

| Variable retenida | Contenido |
|---|---|
| Estaciones de metro en 1 km | Oferta de transporte del entorno |
| Anuncios en 500 m | Densidad y actividad de mercado de la zona |
| Antigüedad mediana del barrio | Momento de desarrollo urbano de la zona |
| Superficie mediana del barrio | Tipo de producto predominante |

**Aportación.** Las cuatro variables retenidas reducen en un 16,4% el error de
un modelo que ya incorpora las tres distancias de origen, del 18,3% al 15,1% de
error relativo. La magnitud resulta comparable a la aportación de las propias
distancias de origen, que reducen en un 22,2% el error del modelo basado
exclusivamente en atributos de la vivienda.

Dos resultados merecen comentario. La superficie mediana del barrio constituye
la variable de mayor capacidad explicativa del conjunto, superior a la de
cualquiera de las variables de origen, pese a presentar una correlación de
apenas 0,198 con la más próxima de aquellas: el tipo de producto predominante en
la zona aporta información que las medidas de distancia no contienen. Y la
antigüedad mediana del barrio, cuya elevada correlación con la distancia al
centro sugería redundancia, resultó necesaria: su supresión eleva el error en un
1,75%, por recoger una relación con el precio de naturaleza no monótona que las
medidas de distancia no reproducen.

**Variables excluidas por construcción.** No se incorporan el precio mediano del
barrio ni el retardo espacial del precio, pese a su capacidad explicativa
previsible. Ambos emplean la variable objetivo de las viviendas del entorno para
estimar la de la vivienda considerada, lo que constituiría una fuga de
información: el modelo dispondría de una versión promediada de su propia
respuesta. La exclusión responde asimismo a una consideración de explotación,
dado que su empleo obligaría a mantener y actualizar una tabla de referencia de
precios por zona, y a una de interpretabilidad, al situar como variable
principal del modelo una magnitud derivada del propio precio.

---

# 5. Preparación de datos y feature engineering

*Redactado. Presupuesto: 650 palabras.*

## 5.1. Transformaciones y tratamiento de variables

**Variables descartadas.** El precio unitario, por constituir el cociente exacto
entre precio y superficie y suponer su empleo como predictor una fuga de
información. El precio de la plaza de aparcamiento, que registra el importe de
una plaza ofertada de forma independiente y no un atributo de la vivienda. El
indicador de plaza incluida en el precio, que coincide exactamente con el
indicador de disponibilidad de plaza. El año de construcción declarado por el
anunciante, con un 56,31% de valores ausentes, en favor del procedente de
catastro, que está completo. El nivel de equipamiento, que concentra el 94,33%
de las observaciones en un único valor.

**Variables de relación no monótona.** Las variables cuya relación con el precio
no resulta monótona se incorporan tramificadas, dado que una especificación
lineal únicamente permite estimar un efecto constante a lo largo de todo su
recorrido. Afecta a las tres variables de distancia y al año de construcción del
edificio. Los intervalos se establecen en valores fijos, seleccionados sobre los
cambios de pendiente observados en el perfil de precio, y no mediante partición
por cuantiles: esta última sitúa los cortes con arreglo al reparto de
observaciones, lo que en dos de las cuatro variables produce intervalos que
promedian un máximo con el descenso posterior y anulan la señal. Los cortes
adoptados recuperan entre el 71% y el 90% de la capacidad explicativa alcanzable
por una especificación sin restricción de forma, superando en todos los casos a
la partición por cuantiles con igual número de intervalos.

| Distancia al centro | Viviendas | Precio mediano | Índice |
|---|---|---|---|
| Menos de 1,5 km | 3.368 | 362.000 € | 82 |
| 1,5 a 3 km | 5.055 | 440.000 € | 100 |
| 3 a 5 km | 7.007 | 222.000 € | 50 |
| 5 a 8 km | 6.829 | 197.000 € | 45 |
| Más de 8 km | 2.875 | 243.000 € | 55 |

El perfil resultante desmiente el decaimiento radial que cabría suponer: el
máximo de precio no se sitúa en el centro sino en la corona comprendida entre
1,5 y 3 kilómetros, que supera al casco histórico en un 21%. La observación
resulta coherente con el gradiente organizado en torno al eje de la Castellana
descrito en el apartado 3.2, y explica que la distancia al eje presente mayor
capacidad explicativa que la radial. El año de construcción presenta su mínimo
en el periodo 1955-1969, un 43% por debajo de la edificación anterior, sin que
la posterior llegue a recuperar ese nivel: la antigüedad no penaliza el valor de
forma progresiva, sino que la penalización se concentra en el producto
característico del desarrollismo.

**Calidad catastral.** Se agrupa en seis niveles, fusionando los tres superiores
y los tres inferiores de la escala, al presentar cinco de sus diez niveles
originales una representación inferior al cinco por ciento. La escala resultante
mantiene la monotonía respecto al precio, lo que permite incorporarla como
variable ordinal en una única columna.

**Tipo de obra.** Los tres indicadores disponibles suman la unidad en la
totalidad de los registros, lo que introduce dependencia lineal si se incorporan
simultáneamente. Se descarta uno como categoría de referencia.

**Valores ausentes.** Se imputan por la mediana o la moda según su naturaleza,
con estimación exclusiva sobre el conjunto de entrenamiento. La incidencia es
reducida: la planta con un 4,23%, los agregados de barrio con un 0,28% y cinco
variables por debajo del 0,1%. El tipo de vistas, con un 6,38%, incorpora la
ausencia como categoría propia, al constituir la falta de declaración una
circunstancia informativa y no un dato perdido.

**Naturaleza de las variables de equipamiento.** Son declaradas por el
anunciante y no verificadas, por lo que un valor cero indica ausencia de
declaración y no ausencia del atributo. La circunstancia es particularmente
acusada en las variables de orientación, que el 51,3% de los anuncios no
declara, y debe tenerse presente al interpretar el modelo.

## 5.2. Conjunto final de variables

El conjunto de trabajo comprende 35 variables explicativas: diez numéricas
continuas, dieciocho indicadores binarios, cuatro tramificadas, dos categóricas
y una ordinal. El distrito se incorpora mediante codificación disyuntiva. El
barrio se descarta como predictor: sus 135 niveles deterioran la
interpretabilidad del modelo lineal, y su codificación por la respuesta
reproduciría la fuga de información que motivó excluir el precio mediano de zona
en el apartado 4. Se conserva no obstante como identificador, por resultar
necesario en el análisis de equidad del apartado 9.

**Encapsulado del preprocesado.** La totalidad de las transformaciones se agrupa
en un objeto único que se ajusta sobre el conjunto de entrenamiento y se
conserva junto con el modelo. La decisión responde a una consideración de
explotación: la aplicación descrita en el apartado 10 carga dicho objeto y lo
aplica a la vivienda introducida por el usuario, de modo que el tratamiento
recibido por los datos en producción no puede diferir del empleado durante el
entrenamiento. La divergencia entre ambos constituye una de las causas
habituales de deterioro de los modelos desplegados.

**Dos formulaciones de la misma información.** Las variables tramificadas se
incorporan como tales al modelo interpretable y en su escala original al modelo
de alto rendimiento, que determina sus propios puntos de corte y para el que la
tramificación supondría una pérdida de información. Las variables numéricas se
estandarizan únicamente en la primera formulación. Ambas operan sobre idéntica
información de partida, idéntica partición e idéntica imputación, de modo que la
comparación del apartado 6.4 mida la capacidad de los modelos y no el ajuste del
preprocesado a uno de ellos. El conjunto resultante comprende 66 columnas en la
primera formulación y 55 en la segunda.

---

# 6. Modelización

## 6.1. Estrategia de validación y métricas de evaluación

*Redactado.*

**Partición y validación cruzada.** La partición se realiza de forma aleatoria
por filas, con una proporción del 80/20 y estratificación por decil de precio,
lo que arroja 25.134 viviendas de entrenamiento y 6.284 de validación. Un
experimento sobre el conjunto sin depurar muestra que la partición aleatoria por
filas subestima el error mediano en 0,8 puntos porcentuales (9,35% frente a
10,14%), al aparecer un mismo inmueble en ambos conjuntos bajo anuncios
distintos; la deduplicación por identificador elimina esa circunstancia. La
estratificación por decil garantiza que la validación reproduzca la distribución
de la variable objetivo, con particular atención a la cola superior, que reúne
pocas observaciones y ejerce una influencia elevada sobre las métricas.

El conjunto de validación no interviene en decisión alguna de modelización. La
elección de familia de modelo, de hiperparámetros y de tratamiento de valores
ausentes se resuelve mediante validación cruzada en cinco pliegues sobre el
conjunto de entrenamiento, igualmente estratificados por decil. Los pliegues se
fijan una única vez, de modo que todas las configuraciones evaluadas se midan
sobre idéntica partición y las diferencias observadas respondan al modelo. El
requisito responde a una exigencia habitual en la validación de modelos
internos: el error comunicado debe estimarse sobre datos que no hayan
participado en elección alguna.

**Formulación logarítmica de la variable objetivo.** El modelo estima el
logaritmo del precio y no el precio. La transformación responde a cuatro
motivos. Convierte el error absoluto en relativo, dado que la diferencia entre
logaritmos equivale al error porcentual, lo que impide que el ajuste se oriente
a las viviendas de precio elevado en detrimento del grueso del mercado. Recoge
la naturaleza multiplicativa de los efectos que determinan el valor, dado que un
atributo no añade un importe fijo sino una proporción del precio. Estabiliza la
dispersión del error y reduce la asimetría de la distribución de 4,20 a 0,55. Y
excluye por construcción las estimaciones negativas, que la especificación
lineal sobre las variables originales producía en 233 casos.

La valoración se obtiene aplicando la función exponencial a la predicción, sin
corrección adicional. La elección determina que el modelo estime la mediana
condicional del precio y no su media: sobre una distribución asimétrica, la
media queda desplazada al alza por la cola superior, mientras que la mediana
describe el valor típico de un inmueble con esas características. La magnitud
relevante para la valoración de una garantía es la segunda. La decisión mantiene
además la coherencia con la métrica principal, que es precisamente la medida que
la mediana condicional minimiza.

**Métricas.** Todas se construyen sobre el ratio entre valoración estimada y
precio observado, magnitud que constituye la base de los estudios de valoración
masiva. El error relativo mediano (MdAPE) constituye la métrica principal, por
las razones de asimetría expuestas en el apartado 3.1. Las proporciones de
valoraciones comprendidas dentro de un margen del diez y del veinte por ciento
(PE10 y PE20) expresan el mismo resultado en los términos habituales del sector.
La mediana del ratio informa del sesgo global de nivel, y el coeficiente de
dispersión (COD) mide la dispersión en torno a dicha mediana y no en torno a la
unidad, lo que permite distinguir un modelo consistente pero desplazado de otro
centrado pero errático.

Las tres últimas medidas proceden del estándar de estudios de ratio de la
*International Association of Assessing Officers*, cuyo alcance conviene
precisar. Dicho estándar tiene origen en la tasación catastral con fines
fiscales y presupone un denominador constituido por precios de transacción
verificados, obtenidos con posterioridad e independencia respecto de la
valoración. Aquí el denominador es el precio de oferta y procede de la misma
fuente con que se entrenó el modelo, por lo que los valores resultantes serán
optimistas frente a un estudio de ratio real. Se emplean en consecuencia como
comparación entre modelos y entre zonas, donde el sesgo afecta por igual a todos
los casos, y no como certificación frente al estándar.

Se recurre a dicho marco pese a su origen fiscal por ser el único que define
métricas de equidad cuantificables. El marco europeo de referencia —las European
Valuation Standards y, en particular, su norma sobre modelos automatizados— es
de naturaleza procedimental: regula las condiciones en que resulta admisible un
sistema de valoración automatizada y la intervención profesional exigible, sin
definir medidas de equidad ni umbrales numéricos.

**Modelos de referencia.** Tres procedimientos elementales delimitan la
exigencia aplicable al modelo. Todos estiman el valor como producto de la
superficie del inmueble por el precio unitario mediano de su zona, y difieren
únicamente en el grado de agregación espacial: una única cifra para el conjunto
del mercado, una por distrito o una por barrio. Los agregados se estiman
exclusivamente sobre el conjunto de entrenamiento y se aplican a las viviendas
de validación, de modo que el precio de estas últimas no intervenga en la
construcción del procedimiento con el que se valoran.

| Procedimiento | Unidades | MdAPE | PE10 | PE20 | COD |
|---|---|---|---|---|---|
| Superficie y precio del mercado | 1 | 33,71% | 14,0% | 29,0% | 45,79 |
| Superficie y precio del distrito | 21 | 17,76% | 30,1% | 54,9% | 22,85 |
| Superficie y precio del barrio | 135 | **14,75%** | 35,4% | 63,2% | 19,89 |

La comparación entre los tres niveles cuantifica la aportación de la
localización con independencia del resto de características de la vivienda:
conocer el barrio reduce el error de valoración en un 56%. Ninguna otra
información disponible en el conjunto produce un efecto de magnitud comparable.

La última fila constituye la referencia exigente. Un error mediano del 14,75%
equivale a una desviación aproximada de 39.500 euros sobre la vivienda mediana,
y un sistema de valoración automatizada que no mejore esa cifra de forma
apreciable no justificaría su complejidad frente a una regla de cálculo que cabe
en una línea.

Dos circunstancias matizan la comparación y conviene declararlas. La primera es
que el procedimiento de referencia opera sobre 135 barrios mientras que el
modelo dispone únicamente de los 21 distritos, dado que el barrio se descartó
como variable explicativa por las razones expuestas en el apartado 5.2. El
nivel intermedio de la tabla mide con exactitud esa diferencia: pasar de
distrito a barrio reduce el error en un 17%. El modelo debe compensar dicha
desventaja mediante el enriquecimiento geoespacial del apartado 4. La segunda es
que el procedimiento de referencia emplea el precio de las viviendas del entorno,
esto es, precisamente la información que se excluyó del modelo por constituir
fuga. La referencia dispone así de un elemento que al modelo se le negó de forma
deliberada.

**Limitaciones del procedimiento de referencia.** Su distribución de error
revela dos debilidades que un modelo puede corregir. El coeficiente de
dispersión de la referencia de barrio asciende a 19,89, por encima del valor de
quince que el estándar del sector considera admisible en mercado residencial:
la regla elemental no solo resulta imprecisa, sino inconsistente entre inmuebles
comparables. Y la valoración presenta un sesgo sistemático por tamaño, al
infravalorar en un 7% las viviendas del quintil inferior de superficie y
sobrevalorar en un 4% las del superior. El comportamiento es consecuencia
necesaria de su formulación: aplicar un precio unitario constante a cada zona
supone asumir proporcionalidad entre superficie y precio, cuando la elasticidad
estimada en el apartado 3.1 asciende a 1,14.

## 6.2. Modelo interpretable

*Redactado.*

El primer modelo se estima mediante regresión lineal múltiple por mínimos
cuadrados ordinarios, especificación que constituye el procedimiento habitual en
valoración masiva y que proporciona inferencia estándar sobre los coeficientes.
Se descarta la regularización, que introduce sesgo deliberado en la estimación y
no conserva dicha propiedad; su aplicación con finalidad diagnóstica no altera
los coeficientes de forma apreciable ni modifica signo alguno. Se descarta
asimismo la selección automática de variables: la especificación se resolvió en
el apartado 5 atendiendo a criterios de fuga de información y pertinencia para el
negocio, y los procedimientos secuenciales invalidan los contrastes de
significación al practicarlos de forma reiterada sobre los mismos datos.

**Lectura de los coeficientes.** La estimación sobre el logaritmo del precio
permite expresar cada coeficiente como efecto porcentual. Entre los atributos de
la vivienda, el ascensor resulta el de mayor incidencia con un incremento del
19%, seguido de la piscina con un 12,3%, la plaza de garaje con un 7,5% y el aire
acondicionado con un 7,1%. El estado de conservación ejerce un efecto de
magnitud comparable a la localización: la vivienda usada se valora un 23,3% por
debajo de la de obra nueva y la que precisa reforma un 16,2%. Los distritos
periféricos presentan diferencias de hasta el 45% respecto del distrito Centro.
La comprobación de coherencia verifica que la totalidad de los atributos que
añaden valor de forma inequívoca presenten efecto positivo.

Doce coeficientes no alcanzan significación al cinco por ciento, cifra que
conviene interpretar con cautela: sobre veinticinco mil observaciones el
contraste distingue efectos de magnitud irrelevante, y los coeficientes
afectados corresponden en su mayoría a tramos limítrofes o a distritos de escasa
representación, para los que la ausencia de significación indica
indistinguibilidad respecto del tramo de referencia y no irrelevancia. Resulta
destacable, por contraintuitivo, que las cuatro variables de orientación
presenten efectos inferiores al 1,4% y aportación nula al error de valoración:
el mercado de oferta madrileño no incorpora al precio un atributo que los
manuales de tasación consideran relevante.

**Diagnóstico.** El registro identificado en el análisis descriptivo como valor
extremo no ejerce influencia apreciable sobre la estimación. La distancia de
Cook máxima asciende a 0,0128, tres órdenes de magnitud por debajo del valor
unitario indicativo de influencia severa, y la exclusión de las veinte
observaciones más influyentes altera el coeficiente más afectado en una magnitud
equivalente al 1,4% de efecto sobre el precio, sin modificar signo alguno. Se
conservan en consecuencia todos los registros: corresponden a inmuebles de
superficie excepcional cuya valoración el modelo subestima, esto es, a
información legítima sobre el segmento de mayor exposición en términos de riesgo.

**Aportación de los bloques de variables.** La estimación de especificaciones
acumulativas cuantifica el rendimiento marginal de cada conjunto de predictores.
Las características físicas de la vivienda arrojan por sí solas un error del
22,41%; la incorporación del distrito lo reduce al 15,00%, el enriquecimiento
geoespacial al 14,34% y los agregados de barrio al 14,03%.

La lectura marginal resulta no obstante engañosa si se omite el solapamiento
entre los dos bloques de localización. Evaluado sin el distrito, el
enriquecimiento geoespacial reduce el error en 4,38 puntos porcentuales, frente a
los 0,66 que aporta una vez aquel se encuentra incorporado; de forma simétrica,
el distrito aporta 7,41 puntos aislado y 3,69 marginales. Ambos bloques pierden
cerca de la mitad de su aportación en presencia del otro, circunstancia esperable
dado que miden el mismo fenómeno desde perspectivas distintas. Los 8,07 puntos
que aportan conjuntamente no resultan atribuibles por separado.

La observación reviste interés para la explotación del sistema. Una
especificación basada en características de vivienda y variables geoespaciales,
sin zonificación administrativa alguna, alcanza un error del 18,03% partiendo
exclusivamente de coordenadas. Dicha vía resulta portable a mercados distintos
del madrileño, mientras que la basada en el distrito exige una zonificación
específica de cada ciudad.

**Resultado.** El modelo alcanza un error relativo mediano del 14,04% en
validación cruzada. La mejora respecto del procedimiento de referencia asciende a
siete décimas, magnitud reducida en relación con el coste de una especificación
que incorpora sesenta y seis columnas.

El diagnóstico por segmento revela dos limitaciones de naturaleza estructural. La
primera es que el modelo no corrige el sesgo por tamaño del procedimiento de
referencia sino que lo invierte y lo amplía: valora por exceso en un 10,6% las
viviendas del quintil inferior de superficie y por defecto en un 5,7% las del
superior, con un recorrido entre extremos superior al de aquel. La segunda es la
distribución del error por segmento de valor, que describe una forma de U con
mínimo del 10,79% en el sexto decil y degradación hasta el 19,12% y el 20,82% en
los extremos. Ambas comparten origen en la restricción aditiva de la
especificación, que impide que el efecto de una variable dependa del valor que
tomen las restantes y que obliga a estimar una elasticidad única entre superficie
y precio aplicable a la totalidad del rango.

## 6.3. Modelo de alto rendimiento

*Redactado.*

El segundo modelo emplea *gradient boosting* sobre árboles de decisión,
procedimiento habitual en los sistemas comerciales de valoración automatizada.
Se estima sobre la rama de árboles del preprocesado, que conserva las variables
en su escala original y prescinde de la tramificación por resultar ambas
innecesarias: el algoritmo determina por sí mismo los puntos de corte y su
comportamiento no depende de la escala. Ambas ramas comparten imputación,
codificación y partición, de modo que las diferencias observadas respondan a la
familia de modelo.

Los hiperparámetros se seleccionan mediante muestreo aleatorio de cuarenta
configuraciones evaluadas sobre los mismos pliegues que el resto de
comparaciones, con el error relativo mediano como criterio. El procedimiento
resulta preferible a la exploración exhaustiva con siete hiperparámetros, dado
que una rejilla de coste equivalente examinaría apenas dos valores de cada uno.
La configuración seleccionada emplea ochocientos ochenta y siete árboles de
profundidad máxima nueve, con tasa de aprendizaje de 0,038 y submuestreo del
86% de las observaciones en cada iteración.

El ajuste de hiperparámetros aporta 0,82 puntos porcentuales respecto de una
configuración de partida no ajustada, que arroja un 9,81%. La superficie de error
resulta plana en el entorno del óptimo: las mejores configuraciones difieren
entre sí de forma apreciable y arrojan errores comprendidos en un intervalo
reducido, de modo que la elección concreta reviste escasa relevancia.

**Resultado.** El modelo alcanza un error relativo mediano del 8,97% en
validación cruzada, frente al 14,04% del modelo interpretable. La mejora no
responde a la información disponible, idéntica en ambos casos, sino a la
capacidad de combinarla sin restricción aditiva.

La estructura de árboles corrige las dos limitaciones del modelo interpretable.
El sesgo por tamaño desaparece: los ratios medianos por quintil de superficie se
comprenden entre 0,994 y 0,998, con un recorrido entre extremos cincuenta veces
inferior al de la especificación lineal. Y la distribución del error por segmento
de valor se aplana de forma sustancial, con mejoras máximas precisamente en los
extremos donde el modelo interpretable resultaba menos fiable.

## 6.4. Comparativa de rendimiento

*Redactado.*

El conjunto de validación reservado en el apartado 6.1 se emplea por primera vez.
Ninguno de los procedimientos evaluados ha intervenido sobre él: los agregados de
zona se estimaron sobre entrenamiento, la selección de hiperparámetros se
resolvió mediante validación cruzada, y la especificación del modelo
interpretable respondió a criterios establecidos con anterioridad.

| Procedimiento | MdAPE | PE10 | PE20 | COD |
|---|---|---|---|---|
| Superficie y precio del mercado | 33,71% | 14,0% | 29,0% | 45,79 |
| Superficie y precio del distrito | 17,76% | 30,1% | 54,9% | 22,85 |
| Superficie y precio del barrio | 14,75% | 35,4% | 63,2% | 19,89 |
| Modelo interpretable | 14,11% | 37,1% | 66,0% | 19,32 |
| **Modelo de alto rendimiento** | **8,83%** | **55,1%** | **82,2%** | **12,91** |

El modelo de alto rendimiento reduce el error del procedimiento de referencia en
un 40,1%, frente al 4,3% que alcanza el modelo interpretable. Sobre la vivienda
mediana del conjunto, la desviación esperada disminuye de 39.530 a 23.664 euros.
Es asimismo el único de los cinco procedimientos cuyo coeficiente de dispersión
se sitúa por debajo del valor de quince que el estándar del sector considera
admisible, y el único que elimina el sesgo sistemático por tamaño.

La correspondencia entre las estimaciones obtenidas por validación cruzada y las
obtenidas sobre el conjunto reservado —14,04% frente a 14,11% en el modelo
interpretable, 8,97% frente a 8,83% en el de alto rendimiento— verifica que el
protocolo de validación no produjo estimaciones optimistas.

Conviene precisar que la comparación no favorece al modelo. El procedimiento de
referencia opera sobre ciento treinta y cinco barrios mientras que ambos modelos
disponen únicamente de veintiún distritos, y emplea además el precio de las
viviendas del entorno, esto es, la información que se excluyó del modelo por
constituir fuga. La superación de dicha referencia se produce por tanto pese a
una desventaja informativa deliberada, que el enriquecimiento geoespacial
compensa.

**Criterio de aplicación.** La proporción de valoraciones comprendidas dentro de
un margen del diez por ciento se mantiene entre el 55% y el 61% en los deciles
segundo a noveno y desciende al 42,8% y al 47,2% en los extremos de la
distribución. El resultado delimita el rango de valor en que la valoración
automatizada resulta admisible sin intervención profesional, situado de forma
aproximada entre los 120.000 y los 900.000 euros, y sustenta en términos
empíricos el uso declarado en el apartado 1.2.

---

# 7. Interpretabilidad post-hoc del modelo caja negra

*Redactado.*

## 7.1. Importancia global de variables

El modelo de alto rendimiento admite dos lecturas distintas de la importancia de
sus variables, y ambas se practican porque responden a preguntas distintas. La
primera reparte cada valoración entre las características del inmueble mediante
valores SHAP: descompone la diferencia entre la predicción y un valor de
referencia común —292.754 euros, el valor esperado del modelo— en una suma exacta
de contribuciones. La segunda mide de qué información no puede prescindir el
modelo para acertar, inutilizando cada variable por separado y registrando el
deterioro del error relativo mediano sobre el conjunto de validación.

La distinción no es académica. Ante un cliente que pregunta por qué su vivienda
se ha valorado en una cifra determinada, la respuesta válida es la primera. Ante
un comité de validación que pregunta qué ocurre si una fuente de datos deja de
estar disponible, la válida es la segunda. Un modelo puede apoyar sus
valoraciones en variables de las que en realidad podría prescindir, y en tal caso
sus explicaciones no resistirían una auditoría.

**El modelo supera ese contraste.** Sobre las treinta y cinco variables, la
correlación de rangos entre ambos órdenes alcanza 0,957: las que sostienen las
valoraciones son las mismas de las que depende la precisión. Las discrepancias se
concentran en el aire acondicionado y la calidad constructiva, que descienden
siete y cinco posiciones respectivamente al medirlas por su aportación al
acierto, y en el jardín, cuyo efecto sobre el error resulta indistinguible de
cero. En los tres casos la información está disponible por otras vías —el tipo de
obra, el año de construcción, el distrito—, de modo que el modelo la recupera
cuando se le priva de la variable.

La superficie construida domina ambas medidas: concentra el 31,1% de la
atribución y su pérdida degrada el error en 22,7 puntos porcentuales. El
resultado es esperable en valoración inmobiliaria y su ausencia habría sido
motivo de revisión.

| Bloque de información | Atribución | Deterioro del error | Variables |
|---|---|---|---|
| Características de la vivienda | 56,1% | 30,8 pp | 23 |
| Geoespacial | 34,9% | 21,1 pp | 7 |
| Distrito | 4,8% | 3,0 pp | 1 |
| Catastro | 4,2% | 1,6 pp | 4 |

El hallazgo relevante está en el bloque de localización. Las siete variables
geoespaciales reúnen el 34,9% de la atribución y 21,1 puntos de deterioro, frente
a los 3,0 puntos del distrito. Dentro de ese bloque, las cuatro variables
construidas en el apartado 4 —superficie y antigüedad medias del barrio,
estaciones de metro en un kilómetro y densidad de oferta en quinientos metros—
aportan 12,7 puntos, por encima de los 8,4 de las distancias disponibles en
origen y más de cuatro veces lo que aporta la zonificación administrativa. El
enriquecimiento geoespacial no constituye por tanto un complemento del modelo
sino su segundo componente explicativo, y lo es además por una vía portable: se
obtiene a partir de coordenadas, sin depender de una división administrativa
concreta.

El distrito, no obstante, conserva una aportación propia que no resulta
reconstruible desde las coordenadas. Su permanencia en la sexta posición de ambas
medidas indica que la pertenencia administrativa transmite información
—reputación de zona, régimen urbanístico— que las distancias y los agregados de
barrio no capturan.

Dos variables merecen mención por su ausencia. Las cuatro orientaciones ocupan
las últimas posiciones en ambas medidas, con aportaciones al error comprendidas
entre 0,001 y 0,049 puntos porcentuales. El resultado confirma el obtenido en el
modelo interpretable del apartado 6.2 y descarta que se tratara de una limitación
de la especificación aditiva: dos modelos de familia distinta, uno de ellos sin
restricción funcional alguna, coinciden en no encontrar señal en un atributo que
los manuales de tasación consideran relevante. El indicador de ático se comporta
de igual modo, circunstancia que se examina en el apartado 8.

*Figura 7: importancia global por atribución y por aportación al acierto.*

## 7.2. Explicación de predicciones individuales

La descomposición del apartado anterior admite lectura sobre una vivienda
concreta: sus contribuciones, sumadas al valor de referencia del modelo,
reproducen exactamente la valoración obtenida. Esa lectura es la que acompaña a
una valoración remitida a un comité de riesgos y la que sostiene la pantalla de
explicación de la aplicación descrita en el apartado 10.

Se examinan dos casos, seleccionados mediante criterios calculados sobre el
conjunto de validación y no por elección discrecional: una vivienda de precio
próximo a la mediana dentro del rango operativo, y la situada en el percentil 99
del cociente entre valoración y precio anunciado.

**El primer caso documenta el funcionamiento ordinario.** Un piso de 55 metros
cuadrados en Adelfas parte del valor de referencia de 292.754 euros y se
descuentan 84.484 por una superficie inferior a la típica del conjunto. El modelo
recupera a continuación 34.065 euros porque Adelfas es un barrio de viviendas
pequeñas, en el que 55 metros cuadrados no constituyen una vivienda reducida. Esa
corrección —penalizar por tamaño y compensar según el contexto del barrio— es una
interacción entre dos variables que un modelo aditivo no puede representar, y
aparece en el primer caso examinado sin haberla buscado. La valoración cierra en
261.828 euros frente a los 268.000 anunciados.

**El segundo caso ilustra el uso de la explicación como instrumento de
contraste.** El modelo valora en 288.295 euros una vivienda de 75 metros
cuadrados en el barrio de Colina anunciada en 161.000, con una discrepancia del
79%. La descomposición no revela ninguna atribución anómala: el reparto penaliza
correctamente la superficie y la ausencia de ascensor, y añade valor por el
contexto del barrio, el distrito, la piscina y el garaje. El contraste con el
entorno confirma la lectura: la vivienda se anuncia a 2.147 euros por metro
cuadrado en un barrio cuya mediana se sitúa en 3.787, y el conjunto de las
viviendas de Colina presenta un cociente mediano de 0,993 y un error del 6,5%,
inferior al del conjunto. La discrepancia no procede por tanto de la valoración
sino del precio anunciado.

Ahí reside la utilidad de la explicación individual para el caso de negocio. Un
modelo que emite únicamente una cifra no permite contrastar tasaciones recibidas:
ante una discrepancia no ofrece criterio para decidir si procede desconfiar del
modelo o del importe declarado. La descomposición sí lo ofrece, y convierte una
valoración automatizada en un elemento de juicio para el analista en lugar de en
un número que aceptar o rechazar.

Procede declarar la convención empleada en la conversión a euros. La
descomposición es aditiva sobre el logaritmo del precio y por tanto
multiplicativa sobre la escala monetaria: los efectos porcentuales son
independientes del orden de lectura, pero su traducción a importes no lo es, dado
que un mismo porcentaje produce una cifra mayor aplicado sobre un valor acumulado
mayor. Las cantidades de la figura se obtienen por acumulación sucesiva en orden
decreciente de magnitud.

*Figura 8: descomposición de dos valoraciones individuales.*

## 7.3. Interpretabilidad intrínseca frente a post-hoc

El modelo interpretable expresa el efecto de cada característica mediante un
coeficiente único: el ascensor incrementa el precio un 19% en cualquier vivienda
de Madrid. El modelo de alto rendimiento no dispone de tal parámetro, pero su
equivalente se obtiene comparando la contribución media de las viviendas que
declaran el atributo con la de las que no lo declaran, magnitud que estima lo
mismo y resulta por ello directamente comparable.

**Las dos explicaciones concuerdan.** Sobre los dieciocho atributos binarios
comparables, el signo coincide en el 94% de los casos y la correlación entre
ambas estimaciones alcanza 0,870. La explicación obtenida a posteriori sobre un
modelo opaco recupera por tanto lo que un modelo transparente afirma, que es el
único aval empírico disponible de que describe el comportamiento del modelo y no
un artefacto del procedimiento que la genera. La comprobación no es prescindible:
sin un modelo transparente con el que contrastar, una explicación post-hoc se
acepta por confianza en el método.

La concordancia se refiere no obstante a la dirección y al orden, no a la
magnitud. El modelo interpretable estima efectos sistemáticamente mayores, con
una pendiente de 1,69 entre ambas estimaciones. La explicación plausible es de
atribución: al no poder representar las interacciones, el modelo aditivo carga
sobre cada atributo la parte de valor que corresponde a las características con
las que aparece asociado —el ascensor con la altura del edificio, el distrito y
el tipo de obra—, mientras que el modelo de árboles reparte ese mismo valor entre
todas ellas. La colinealidad documentada en el apartado 6.2, con factores de
inflación de la varianza de ocho a nueve en los indicadores de distrito, resulta
coherente con dicha lectura. Se trata de una interpretación razonada y no de un
extremo contrastado.

**La diferencia de fondo es de naturaleza y no de magnitud.** El coeficiente es
un número; la contribución es una distribución. El efecto del ascensor recorre en
el modelo de árboles desde un 3,4% hasta un 10,1% entre los percentiles quinto y
nonagésimo quinto: vale mucho en un edificio alto y antiguo y casi nada en uno
bajo y reciente. El modelo aditivo no puede expresar esa variación y se ve
obligado a resumirla en un valor único, que es exactamente la restricción que
origina la diferencia de precisión entre ambos modelos.

La comparación arroja finalmente una asimetría que conviene declarar. El modelo
interpretable ofrece inferencia estadística —cada coeficiente dispone de un
contraste de significación— y se describe por completo en una tabla de sesenta y
seis filas que puede entregarse a un validador. El análisis post-hoc no
proporciona ni lo uno ni lo otro: no existe contraste asociado a una
contribución, y la descripción del modelo requiere una explicación por vivienda.
Existe además una tercera limitación, propia del método: el reparto entre
características que comparten información es una convención razonable y no una
división única, de modo que la frontera que se traza entre el distrito y las
variables geoespaciales admitiría otras formulaciones. La explicación post-hoc es
exacta respecto del modelo que describe, pero no es la única explicación posible
del mismo modelo.

*Figura 9: coeficiente único frente a distribución de efectos.*

---

# 8. Discusión del trade-off

*Redactado.*

El trabajo ha estimado dos modelos sobre la misma información, la misma partición
y el mismo preprocesado, y ambos alcanzan resultados que difieren de forma
sustancial. El modelo interpretable sitúa el error relativo mediano en el 14,11%
y el modelo de alto rendimiento en el 8,83%. La proporción de valoraciones que se
desvían menos de un 10% del precio observado pasa del 37,1% al 55,1%. El
coeficiente de dispersión desciende de 19,32 a 12,91, de modo que únicamente el
segundo alcanza el valor de quince que el estándar del sector considera
admisible. Sobre la vivienda mediana del conjunto, 268.000 euros, la desviación
esperada disminuye de 37.800 a 23.664 euros.

**El origen de esa diferencia no es informativo sino estructural.** Ambos modelos
reciben las mismas treinta y cinco variables. Lo que los separa es que el modelo
interpretable está obligado a asignar a cada característica un efecto único,
mientras que el de alto rendimiento puede hacerlo depender del resto de
características de la vivienda.

El apartado 7.3 midió esa restricción sobre el ascensor, cuyo efecto recorre de
un 3,4% a un 10,1% según la vivienda mientras el modelo aditivo debe resumirlo en
un valor único del 19%. La planta ofrece un caso más nítido, porque su efecto no
solo varía en magnitud sino que invierte su signo. Su valor no es absoluto sino
relativo a la altura del edificio: una tercera planta es la posición superior en
un edificio de tres alturas y una posición baja en uno de doce. El modelo de
árboles representa esa dependencia y asigna a la planta contribuciones que van
desde el −1,52% en posiciones intermedias de edificios bajos hasta el +5,50% en
últimas plantas de edificios de nueve alturas o más. El modelo interpretable
estima para ese conjunto de comportamientos un parámetro único de +0,63%,
estadísticamente indistinguible de cero. Los 5,28 puntos de diferencia entre
ambos modelos son la suma de decenas de restricciones de esa naturaleza.

El examen permite además corregir un diagnóstico formulado en el apartado 6.2. La
comparación practicada allí enfrentaba el precio unitario de las últimas plantas
con el de las primeras sin distinguir la altura del edificio, y confundía por
ello dos efectos, dado que los edificios de escasa altura se concentran en la
periferia y presentan precios unitarios inferiores por su localización. El
indicador de ático resulta irrelevante para ambos modelos por una razón distinta
y más simple: únicamente el 24,3% de las viviendas que lo declaran presentan una
planta coincidente con la altura catastral del edificio.

**La cuestión relevante no es cuál de los dos modelos es mejor sino qué se pierde
al renunciar a cada uno.** Renunciar al modelo de alto rendimiento cuesta 5,28
puntos de error, 18,0 puntos de valoraciones dentro del margen del diez por
ciento y un coeficiente de dispersión que no alcanza el estándar. Renunciar al
modelo interpretable cuesta la inferencia estadística y obliga a construir la
explicación mediante un procedimiento adicional, que es el desarrollado en el
apartado 7.

Ese segundo coste ha resultado menor de lo que cabría suponer. La explicación
post-hoc concuerda con la del modelo transparente en el signo del 94% de los
atributos y en su ordenación, y reproduce cada valoración de forma exacta. Es
además suficiente para el uso previsto: el apartado 7.2 documenta que permite
distinguir un error de valoración de un precio de oferta atípico, que es
precisamente lo que exige el contraste de tasaciones recibidas. El primer coste,
en cambio, no es recuperable por ninguna vía.

**La conclusión para el caso de negocio es que el modelo de alto rendimiento
resulta preferible, con una condición.** La condición es que la explicación
acompañe siempre a la valoración. Un AVM que emitiera únicamente una cifra sería
inservible para las finalidades declaradas en el apartado 1.2: ante una
discrepancia con una tasación recibida no ofrecería criterio para decidir de qué
lado está el problema, y ante un comité de validación no permitiría acreditar que
el modelo se apoya en las variables que dice emplear. La aplicación descrita en
el apartado 10 incorpora por ello la descomposición de la valoración como parte
del resultado y no como información complementaria.

Conviene por último acotar el alcance de esta discusión. El modelo interpretable
de este trabajo es una regresión lineal sin términos de interacción ni
tramificación de la superficie, especificación que el apartado 11 identifica como
mejorable. Un modelo aditivo más elaborado reduciría la distancia sin llegar a
eliminarla, dado que el número de interacciones a especificar manualmente crece
con rapidez. La comparación practicada mide por tanto la distancia entre una
especificación aditiva razonable y un modelo sin restricción funcional, no el
límite teórico de la primera.

---

# 9. Análisis de equidad de la valoración

*Redactado.*

Un modelo de valoración puede alcanzar un error agregado reducido y distribuirlo
de forma desigual entre segmentos de la población. La cuestión no es accesoria en
el uso previsto: un procedimiento que sobrevalorase de forma sistemática las
garantías situadas en barrios de renta baja infraestimaría la pérdida esperada
precisamente donde la probabilidad de impago es mayor, y trasladaría ese error a
la cobertura del riesgo.

El análisis emplea la renta neta media por persona del ejercicio 2018, publicada
por el Instituto Nacional de Estadística en el Atlas de Distribución de Renta de
los Hogares con desagregación por sección censal, la unidad territorial de menor
tamaño para la que existe información de renta en España. Se trata de una
variable ajena al modelo y ajena al precio de la vivienda, lo que permite
examinar la distribución del error sin recurrir a una magnitud que el propio
modelo emplea. A cada una de las 6.284 viviendas de validación se le atribuyó la
renta de la sección censal que contiene sus coordenadas, empleando la cartografía
del seccionado vigente en 2018, dado que la delimitación de las secciones se
actualiza anualmente. Las 2.443 secciones de Madrid capital disponen de dato de
renta, con un recorrido que va de 3.719 a 32.242 euros por persona: un factor de
casi nueve entre los extremos, dispersión que otorga contenido al contraste.

**La distribución del error es homogénea por nivel de renta.**

| Quintil de renta | Renta mediana | Precio mediano | Valoración / precio | Error mediano |
|---|---|---|---|---|
| 1 | 9.461 € | 136.000 € | 1,014 | 9,01% |
| 2 | 12.246 € | 184.000 € | 0,997 | 9,46% |
| 3 | 16.328 € | 284.000 € | 0,994 | 8,37% |
| 4 | 20.562 € | 413.000 € | 0,995 | 8,32% |
| 5 | 28.291 € | 682.000 € | 0,993 | 8,86% |

El cociente entre valoración y precio observado se mantiene entre 0,993 y 1,014,
y el error relativo mediano entre el 8,3% y el 9,5%. La diferencia de error entre
los quintiles extremos es de 0,15 puntos porcentuales. El modelo no valora con
menor precisión en los barrios de renta baja.

El único desvío apreciable es una sobrevaloración del 1,4% en el quintil de renta
inferior. Su origen es en buena medida mecánico: todo modelo de regresión
comprime sus predicciones hacia el valor central, de modo que sobrevalorar en el
extremo inferior de la distribución constituye un resultado esperado y no un
hallazgo.

**La comparación lo confirma.** Calculados los mismos indicadores agrupando por
quintiles de precio en lugar de renta, el recorrido del cociente asciende a 0,081
frente a los 0,021 que se obtienen por renta. El sesgo opera sobre el precio, que
es la magnitud sobre la que actúa la compresión, y se diluye al ordenar por una
variable distinta. Renta y precio están asociados —el precio mediano del quintil
superior quintuplica el del inferior— pero no coinciden: existen viviendas
modestas en secciones acomodadas y viviendas caras en secciones de renta media, y
esa falta de coincidencia es la que permite separar ambos efectos.

Procede señalar no obstante que el signo del desvío residual es el desfavorable
para el uso previsto. La sobrevaloración se concentra donde una garantía
sobrevalorada tiene peor efecto sobre la pérdida esperada. Su magnitud es pequeña
—unos 1.900 euros sobre la vivienda mediana de ese tramo— y no justifica corregir
el modelo, pero sí incorporar el seguimiento de este indicador al control
periódico del procedimiento.

**El resultado del análisis es por tanto negativo, y en este contexto un
resultado negativo es favorable.** No se detecta inequidad atribuible al nivel de
renta de la zona, lo que permite sostener ante un órgano de validación que el
procedimiento no penaliza de forma sistemática a ningún segmento de la población.
La comprobación no es prescindible por el hecho de no haber encontrado sesgo: en
un entorno supervisado, la ausencia de discriminación es algo que debe
acreditarse, no presumirse.

Dos limitaciones acotan el alcance de esa afirmación. La primera es de
representatividad de la fuente: la renta mediana de las secciones donde se ubican
las viviendas anunciadas asciende a 16.328 euros frente a los 14.657 del conjunto
de secciones del municipio, de modo que la oferta de portal se concentra en zonas
de renta superior a la media. El análisis se refiere al parque anunciado y no al
parque residencial. La segunda es de granularidad: la renta se atribuye a la
sección censal y no a la vivienda, por lo que el contraste mide equidad entre
zonas y no entre hogares. A ello se añade que el precio empleado como referencia
es de oferta y procede de la misma fuente con la que se entrenó el modelo,
conforme a lo expuesto en el apartado 2.3.

---

# 10. Productivización: aplicación web

*Pendiente.*

# 11. Conclusiones

*Pendiente. Se redacta al final.*

# 12. Bibliografía y referencias

*Máximo media cara.*

Referencia obligada por licencia: Rey-Blanco, D., Arbués, P., López, F. y Páez,
A. (2024). *Environment and Planning B: Urban Analytics and City Science*.
DOI 10.1177/23998083241242844.

Documentación del paquete: `https://paezha.github.io/idealista18/`.

Sobre medidas de equidad en la valoración: IAAO Statistical Tools and Measures
Task Force (2023). *A review of vertical equity measures in property
assessments*. JPTAA 20(2). Y McMillen, D. y Singh, R. (2023). *Measures of
vertical inequality in assessments*. Journal of Housing Economics 61, 101950.

Pendientes de incorporar: referencia sobre modelos hedónicos de precios, sobre
métodos de interpretabilidad, sobre el marco europeo de valoración (European
Valuation Standards de TEGoVA y directrices de la Autoridad Bancaria Europea) y
sobre la diferencia entre precio de oferta y de transacción en el mercado
español.
