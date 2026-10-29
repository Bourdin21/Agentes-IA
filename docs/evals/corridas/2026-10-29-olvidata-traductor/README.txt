Corrida de evals: 2026-10-29-olvidata-traductor
Casos: 1 | Prompts: 2

Cada prompt se corre en un SUBAGENTE LIMPIO del rol que indica el caso,
sin contarle que es un eval y sin el contexto de los otros casos
(entorno limpio entre corridas, instruccion 40).
La respuesta se guarda al lado, con el mismo nombre y extension .out.txt

Gradear:  python scripts/evals.py gradear --corrida 2026-10-29-olvidata-traductor

Grado manual 2026-10-29 (rubrica EV-NEG-006): corrida 1 PASS, corrida 2 PASS -> pass^2 PASS.
Ambos captions conservan la venta por kilo y por unidad, no afirman integracion con balanza y
sacan AFIP sin reemplazarla por e-invoicing. Corridas en subagente general-purpose cargando
.claude/agents/olvidata-traductor.md (el tipo de agente nuevo no se registra hasta la sesion siguiente).
Hallazgos que se corrigieron en posicionamiento-nl.md: dietetica health/specialty food store
unificado; "a granel -> bulk" agregado al glosario.
