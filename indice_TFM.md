# Índice del TFM

**Título provisional:** Modelo de valoración automatizada de inmuebles (AVM): interpretabilidad, equidad y productivización

**Opción:** 1) Análisis de un dataset
**Dataset:** idealista18 (Madrid, Barcelona y Valencia, 2018)

---

## 1. Introducción y motivación
- 1.1. Contexto: la valoración automatizada de inmuebles (AVM) en el sector financiero e inmobiliario
- 1.2. Caso de negocio: aplicaciones del AVM (con foco en la tasación de garantías hipotecarias y la gestión de riesgo) y otros usos sectoriales
- 1.3. Objetivos del trabajo y preguntas de investigación

## 2. El conjunto de datos
- 2.1. Descripción del dataset idealista18 (Madrid, Barcelona y Valencia, 2018)
- 2.2. Variables disponibles y licencia de uso
- 2.3. Limitaciones de partida (precio de oferta vs. transacción, antigüedad temporal)

## 3. Análisis exploratorio de datos (EDA)
- 3.1. Análisis descriptivo y distribución de precios
- 3.2. Análisis por ciudad y por barrio
- 3.3. Detección de valores atípicos y calidad del dato

## 4. Enriquecimiento geoespacial
- 4.1. Fundamento: la localización como driver del precio (modelos hedónicos)
- 4.2. Información geoespacial disponible en el dataset y generación de variables propias a partir de distancias a puntos de interés

## 5. Preparación de datos y feature engineering
- 5.1. Transformaciones y tratamiento de variables
- 5.2. Conjunto final de variables

## 6. Modelización
- 6.1. Estrategia de validación y métricas de evaluación
- 6.2. Modelo interpretable
  - 6.2.1. Resultados y rendimiento
  - 6.2.2. Interpretabilidad intrínseca: lectura directa de coeficientes y efectos
- 6.3. Modelo de alto rendimiento
  - 6.3.1. Resultados y rendimiento
- 6.4. Comparativa de rendimiento: ¿cuánta precisión se gana con el modelo caja-negra?

## 7. Interpretabilidad post-hoc del modelo caja-negra
- 7.1. Importancia global de variables
- 7.2. Explicación de predicciones individuales
- 7.3. Interpretabilidad intrínseca vs. post-hoc: alcance y limitaciones de cada enfoque

El 7.1 enfrenta dos medidas: atribución SHAP y aportación al acierto por
permutación. El 7.2 descompone tres valoraciones individuales. El 7.3 contrasta
el coeficiente del modelo interpretable con su equivalente post-hoc.

## 8. Discusión del trade-off: precisión frente a calidad de la interpretabilidad

## 9. Análisis de equidad de la valoración
Diagnóstico del sesgo: cruce del error del modelo con la renta de la sección
censal (Atlas de Distribución de Renta de los Hogares, INE). Sin subdivisión: el
análisis territorial por barrio con índice de Moran se descartó por no aportar
evidencia adicional al contraste renta/precio.

## 10. Productivización: aplicación web de valoración
- 10.1. Arquitectura de la solución
- 10.2. Flujo de uso: entrada de una vivienda, estimación y explicación

## 11. Conclusiones
- 11.1. Principales hallazgos (orientados a negocio)
- 11.2. Limitaciones del trabajo
- 11.3. Líneas de mejora futuras

## 12. Bibliografía y referencias

---

## Anexos
- A. Código desarrollado (notebooks y aplicación)
- B. Estudios detallados del EDA y resultados ampliados de los modelos
