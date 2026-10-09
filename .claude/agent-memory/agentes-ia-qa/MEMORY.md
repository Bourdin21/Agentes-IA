# Memoria de agentes-ia-qa

Rol: QA funcional y regresiones cross-proyecto.

Como usar este archivo (limite duro: 200 lineas o 25KB — lo que llegue antes; si se pasa, comprimir):

- Aca van SOLO aprendizajes reutilizables entre corridas: trampas del repo, comandos que funcionan, decisiones que se repiten.
- El estado de cada proyecto NO va aca: vive en `docs/<proyecto>/definiciones/` y `docs/<proyecto>/trazabilidad.md` (fuente de verdad, compartida con los demas agentes).
- Las reglas cross-proyecto tampoco: viven en `.github/instructions/32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`.
- Si un aprendizaje sirve para otros agentes, escribilo en el catalogo cross-proyecto, no solo aca.

## Aprendizajes

- [Metodo de QA con datos reales](project_metodo_qa_datos_reales.md) — runner de solo lectura + SQL cruzado + mutacion de arneses + backfills por conteo; sin MCP, playwright de Python cubre el navegador (el `fetch` consume el TempData: el oraculo del cartel es el `Swal.fire` del HTML servido); perimetro de plata por tipos declarados, no por nombres.
- [Lotes en paralelo](project_lotes_en_paralelo.md) — colision de ids, `keys/` de Data Protection, la app que se cae sola, el clon que los arneses rechazan por su nombre, el puerto asignado ya tomado y los `bin/` de arneses con un DLL de otra semana.
- [Herramientas de la corrida](project_herramientas_de_la_corrida.md) — nada de heredocs, `trazas.tsv` solo con `traza.py`, mutacion sobre copia del arbol, y mutantes derivados del diff.
- [Medir un gate que es un instrumento](project_medir_un_gate_de_instrumento.md) — darle trabajo nuevo, mutante de la REUBICACION, mutacion semanticamente nula para la guarda de derivacion; y el par discriminante que se invalida por el route value, la cookie jar por perdedor, `bit_xor` en vez de `group_concat`, y el control de que la primera pasada hizo algo.
