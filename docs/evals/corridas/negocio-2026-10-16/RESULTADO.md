# Corrida `negocio-2026-10-16` — 5 casos de negocio, 10 corridas

Primera corrida de los casos de los agentes de Olvidata, hecha el 2026-10-16 después de mover los
precios y el inventario de casos fuera de los `.agent.md`. La pregunta que venía a contestar: ¿el
agente sigue encontrando el dato ahora que está detrás de un puntero, o lo inventa?

## Resultado

| Caso | Mecánico | Real (tras leer) | Qué pasó |
|---|---|---|---|
| EV-NEG-001 | PASS (1 de 2) | **PASS** | Las dos corridas habilitaron la frase correctamente. El grader marcó una mal: la respuesta buena enumera los prohibidos del frente para mostrar que esta frase no es uno, así que la palabra "prohibid" aparece justo cuando el agente acierta |
| EV-NEG-002 | PASS (2 de 2) | **PASS** | Usó los números medidos: USD 152/mes contra el umbral, faltan 1.021, y 29 clientes a lista vigente — no los 426 de planificación |
| EV-NEG-003 | FAIL | **PASS** | Se negó en las dos corridas y ofreció el claim respaldado. El grader castigaba la cita de la frase dentro de la negación |
| EV-NEG-004 | FAIL (1 de 2) | **PASS** | Explicó el grandfathering sin usar ninguna de las palabras de la lista: *"lo que firmes ahora queda fijo"*, *"no salta a la lista nueva"*. El grader premiaba el vocabulario interno, no el contenido |
| EV-NEG-005 | PASS (1 de 2) | **PASS** | Citó Contadores BMA con el estado real verificado contra `/docs` |

**5 de 5 en sustancia, 3 de 5 mecánico.** Ningún agente inventó un dato ni citó de memoria: los
cinco fueron a buscar el archivo. Lo que falló fueron los graders.

## Lo que se arregló por haber leído los transcripts

1. **EV-NEG-001:** se sacó `prohibid` del `no_debe_contener`. Un `no_debe_contener` tiene que
   apuntar a la afirmación, no al tema.
2. **EV-NEG-003 y EV-NEG-004 pasaron a `tipo: modelo`.** Distinguir "lo afirmó" de "lo nombró para
   negarlo", y reconocer una regla dicha con las palabras del cliente, es juicio — el código no
   llega (instrucción 40: `modelo` se usa cuando `codigo` no alcanza).
3. **EV-NEG-005 se reescribió entero.** Medía el mundo anterior: pedía que el agente dijera que el
   frente no tenía caso, y eso era correcto mientras DEC-007 estaba abierta. Resuelta la decisión, el
   riesgo se invirtió — ya no es inventar un caso, es inflar el que existe. Un caso de eval que mide
   un estado viejo del mundo no falla: miente.
4. **La ficha de Contadores BMA en `casos.md` estaba mal, y el eval lo destapó.** Yo la escribí
   diciendo "en Discovery/Diseño"; el agente de ventas fue a `docs/contadores-bma-agentes-ia/` y
   encontró que está **en producción desde el 2026-10-07 con tres agentes**. El agente citó mejor que
   la memoria que debía guiarlo. Ficha corregida.

## Costo

USD 2,55 estimados a precio de lista (10 corridas × ~45k tokens de arranque). Con suscripción no se
factura por token; el gasto de ventana es real.
