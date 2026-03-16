 Fortalezas de la idea

  - Novedad metodológica: Combinar análisis de políticas públicas con deep learning en economía municipal es relativamente poco explorado en España/Latinoamérica.
  - Datos ricos: Las ordenanzas municipales son texto público, lo que abre la puerta a NLP (procesamiento de lenguaje natural) combinado con indicadores económicos.
  - Relevancia práctica: Resultados aplicables a política pública real.

Preguntas clave que debes definir

  1. ¿Qué economías municipales? ¿España? ¿Un país concreto? ¿Tamaño mínimo de municipio?
  2. ¿Qué indicadores económicos como variable dependiente? — PIB municipal, desempleo, renta media, actividad empresarial (IAE), recaudación fiscal...
  3. ¿Cuál es la unidad de análisis? — ¿Municipio-año? ¿Mandato político completo?
  4. ¿Qué partido gobierna vs. qué ordenanzas aprueba? — La causalidad aquí es compleja.

Arquitectura metodológica sugerida

  Inputs:
        - Partido en el gobierno (embeddings o dummies)
        - Texto de ordenanzas → vectores via NLP (BERT, TF-IDF)
        - Variables de control: tamaño municipio, región, año

    Red neuronal:
        - Modelo mixto (tabular + texto)
        - Posiblemente LSTM si modelas series temporales

    Output:
        - Indicador económico t+1 o t+k

Riesgos / desafíos
  - Endogeneidad: Los partidos ganan en municipios con ciertas condiciones económicas previas — difícil separar causa y efecto.
  - Datos: Las ordenanzas municipales no siempre están digitalizadas ni en formato uniforme, especialmente en municipios pequeños.
  - Tamaño muestral: Si usas muchos municipios pequeños, el ruido económico puede dominar la señal política.

Sugerencia para enfocar la tesis

  Podrías delimitar el análisis a municipios de un tamaño concreto (p. ej. >10.000 habitantes) en un país específico, con un horizonte temporal de 2-3 mandatos (2011-2023 en España, por
  ejemplo), y usar el texto de ordenanzas como proxy de orientación ideológica real más allá de la etiqueta de partido.
