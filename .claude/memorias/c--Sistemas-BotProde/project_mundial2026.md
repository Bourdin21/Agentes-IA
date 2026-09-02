---
name: project-mundial2026
description: Estado del bot predictor del Mundial 2026 - qué está actualizado y qué falta
metadata: 
  node_type: memory
  type: project
  originSessionId: 860a48fd-06d0-40f7-b5ab-0bfb5a5e79c1
---

Bot predictor de resultados para el Mundial 2026 (FIFA World Cup 2026).

El archivo principal de predicción actualizada es `predecir_actualizado.py`.

**Arquitectura del sistema:**
- `predecir_actualizado.py` — script principal con JUGADOS (resultados reales), PTS (standings), BAJAS y PARTIDOS (fixture)
- `predecir_con_bajas.py` — versión anterior sin lógica de "ya jugados"
- `predecir_todos.py` — versión sin bajas ni standings
- La predicción usa Dixon-Coles + XGBoost + MLP ensemble con 5 factores contextuales

**Estado al 17 junio 2026 (última actualización):**
- JUGADOS tiene 20 partidos completos (jornadas 1 de grupos A-J)
- Grupos K y L (Portugal/DR Congo/Uzbekistan/Colombia y England/Croatia/Ghana/Panama) jugando hoy 17/6
- Messi confirmado disponible (hat-trick vs Algeria), removido de BAJAS

**Por qué el bot cometía errores:**
- JUGADOS no incluía: Saudi Arabia 1-1 Uruguay, Iran 2-2 New Zealand (15/6), France 3-1 Senegal, Iraq 1-4 Norway, Argentina 3-0 Algeria, Austria 3-1 Jordan (16/6)
- PTS de grupos G, H, I, J estaban en 0 en vez de los pts reales tras jornada 1
- Messi figuraba como baja cuando ya había jugado

**Why:** El archivo se actualizaba manualmente y quedó desactualizado 2 días.
**How to apply:** Recordar actualizar JUGADOS, PTS y BAJAS en predecir_actualizado.py cada vez que se juegan partidos nuevos.

**Arreglos aplicados el 20 junio 2026 (objetivo del bot: ≥15/24 en el prode; venía de 9/24):**
1. **Resultado exacto coherente con el favorito 1X2** (el bug grande). `predict_enriched.py` exponía como "Res" la celda más probable a secas (`top_resultados[0]`), que en partidos parejos es un empate (0-0/1-1) aunque el favorito por probabilidad fuera un equipo. Pasaba en 21% de los partidos → se cargaba un empate en partidos que el modelo daba ganador, perdiendo resultado Y signo. Ahora `predecir_enriquecido` devuelve `resultado_sugerido` = celda más probable DENTRO de la región del favorito 1X2, y `predecir_actualizado.py` lo usa.
2. **Días de descanso**: `predecir_actualizado.py` no pasaba `dias_local/dias_visita` → default 7 → factor fatiga 0.97 → −3% a TODOS los marcadores. En grupos el descanso es ~5 días (factor 1.0). Ahora pasa `dias_local=5, dias_visita=5`.
3. **Umbral de importancia (Factor 3)** en `contexto.py`: el umbral `pts < 6 - restantes*3` era matemáticamente imposible en J1/J2 → los PTS no influían hasta J3. Recalibrado a "ritmo objetivo" = (4/3)*partidos_jugados; magnitud moderada (1.08/0.95 en vez de 1.15/0.92) para no inflar marcadores y bajar el acierto del resultado exacto.
4. **Factor 2 (xG real)** está muerto para selecciones (`EQUIPO_UNDERSTAT` solo mapea clubes). NO se activó proxy porque players_stats.parquet solo cubre 8/48 selecciones (nombres en español: España/Francia/Alemania/...) con 1-7 partidos → sesgo asimétrico. Se deja neutral. Pendiente: fuente real de xG de selecciones.

**Nota entorno:** correr con `PYTHONIOENCODING=utf-8` o terminal UTF-8; la consola cp1252 de Windows revienta con los caracteres ═/⚽.

**Arreglos/experimentos 20 junio 2026 (tarde):**
5. **Localía de anfitriones** (`predecir_actualizado.py`, `_es_local_en_casa`): USA/México/Canadá juegan `neutral=False` (gamma) cuando la sede está en su país. Backtest 18-19/6 vs resultados reales: subió de 10/24 → 13/24. México en Guadalajara pasó de fallo a 1-0 exacto. Sedes MX={Guadalajara,Mexico City,Monterrey}, CA={Vancouver,Toronto}, resto USA. LIMITACIÓN: si el anfitrión es VISITANTE en su país (ej. Switzerland vs Canada en Vancouver, J3) no recibe la ventaja.
6. **Dataset**: `dataset_raw.parquet` cubre 2020→2025. Tiene SOLO el Mundial 2022 (64 partidos, liga="FIFA World Cup"), NO el 2018. tipo_competencia: liga_domestica + selecciones (4151). El modelo entrena con `selecciones` y decay `exp(-dias/365)`, SIN ponderar por competencia. Entrenamiento en `src/match_predictor.py` (DixonColesSelector.fit) y versión vectorizada en `src/ensemble/validation.py`.
7. **Reentrenamiento ponderado por competencia: EVALUADO Y RECHAZADO.** `retrain_dixon_coles.py` existe pero backtest out-of-sample (entrenar pre-Mundial-2022, predecir los 64 partidos) dio PEOR que el plano (signo 50%→44%, RPS peor en decays 365/540/1095). Sobreponderar torneos reduce muestra efectiva → más varianza. NO usar hasta tener más Mundiales en el dataset. El verdadero cuello de botella es CANTIDAD de datos de torneos (conseguir Mundial 2018+), no la ponderación.

**Esquema de puntaje del prode (asumido, falta confirmar con el usuario):** 3 pts resultado exacto / 1 pt acierto de signo (8 partidos × 3 = 24). El modelo acierta bien el signo (~75%) y poco el exacto (~25%).
