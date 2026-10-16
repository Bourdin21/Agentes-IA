Corrida de evals: negocio-2026-10-16
Casos: 5 | Prompts: 10

Cada prompt se corre en un SUBAGENTE LIMPIO del rol que indica el caso,
sin contarle que es un eval y sin el contexto de los otros casos
(entorno limpio entre corridas, instruccion 40).
La respuesta se guarda al lado, con el mismo nombre y extension .out.txt

Gradear:  python scripts/evals.py gradear --corrida negocio-2026-10-16
