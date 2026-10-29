Corrida de evals: 2026-10-29-olvidata-revisor-en
Casos: 1 | Prompts: 2

Cada prompt se corre en un SUBAGENTE LIMPIO del rol que indica el caso,
sin contarle que es un eval y sin el contexto de los otros casos
(entorno limpio entre corridas, instruccion 40).
La respuesta se guarda al lado, con el mismo nombre y extension .out.txt

Gradear:  python scripts/evals.py gradear --corrida 2026-10-29-olvidata-revisor-en

Grado 2026-10-29: EV-NEG-007 pass^2 PASS (mecanico). Transcripts leidos: ambos rechazan por R3,
R5 y R8 sin reescribir el caption. Corrida 2 detecto que "pallet->box" del posicionamiento NL no
coincide con casos.md (caja->unidad, rollo->metro): corregido en posicionamiento-nl.md § 4.
