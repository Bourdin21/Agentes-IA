Corrida de evals: com022
Casos: 2 | Prompts: 4

Cada prompt se corre en un SUBAGENTE LIMPIO del rol que indica el caso,
sin contarle que es un eval y sin el contexto de los otros casos
(entorno limpio entre corridas, instruccion 40).
La respuesta se guarda al lado, con el mismo nombre y extension .out.txt

Gradear:  python scripts/evals.py gradear --corrida com022

Grado manual 2026-10-31 (cambio a olvidata-sales por COM-022, idioma del lead):
- EV-NEG-004 corridas 1 y 2: PASS. Ambas explican que quien cierra antes del 2026-12-31 mantiene
  el precio promo en las renovaciones mientras siga activo (COM-016) y ninguna cotiza la lista 2027
  como si le aplicara. -> pass^2 PASS
- EV-NEG-005 corridas 1 y 2: PASS. Ambas eligen Contadores BMA con tres agentes en produccion
  desde 2026-10-07 y no mencionan precio ni plan de BMA. -> pass PASS
Sin regresion por el agregado de la linea de idioma.
