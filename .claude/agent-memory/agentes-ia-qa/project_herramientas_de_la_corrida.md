---
name: herramientas-de-la-corrida
description: Trampas del instrumental de QA en este repo — heredocs de bash que revientan con el texto de un item de catalogo, trazas.tsv que solo se toca con traza.py, driver de mutacion sobre copia del arbol, y mutantes que hay que derivar del diff y no de las afirmaciones del arnes
metadata:
  type: project
---

Cuatro cosas del instrumental que ya costaron tiempo en corridas distintas, y que conviene tener resueltas antes de empezar a medir.

**1. Nada de heredocs de bash para texto largo.** Un `cat >> archivo <<'YAML'` con el cuerpo de un item del catalogo, o un `python3 - <<'PY'` con el texto de una nota de traza, revienta con `unexpected EOF while looking for matching "'"` aunque el delimitador este entre comillas simples. Pasa por las comillas, los backticks y los `!` del propio contenido.

**Why:** ya me paso en tres corridas seguidas (lotes de QA del 2026-10-06 y el modulo 16 del 2026-10-07) y cada vez perdi dos o tres intentos antes de acordarme.

**How to apply:** el contenido va con la herramienta `Write` a un archivo del scratchpad, y despues `cat archivo >> destino` o un script `.py` escrito tambien con `Write` que lo lea. Para pasarle un texto largo a un script, un archivo aparte y `io.open(...).read()`, nunca un argumento inline.

**2. `docs/trazas/trazas.tsv` se toca SOLO con `scripts/traza.py`.** Reescribirlo con python para borrar una fila le cambia los fines de linea de CRLF a LF y git lo lee como un rewrite completo del archivo (`16 insertions / 22 deletions` cuando yo habia tocado una linea).

**Why:** lo hice en el modulo 16 para limpiar una fila que habia quedado vacia por registrar sin `--nota`, y tuve que restaurar con `git checkout --`. Una traza es observabilidad; el entregable es el reporte, y arreglar la primera a mano pone en riesgo el segundo.

**How to apply:** `traza.py registrar` se invoca UNA vez con todos los campos (`--reintentos`, `--criterios-fallados`, `--reglas-releidas`, `--arranque-kb`, `--nota`) en la misma llamada. Si queda un bloque vacio en `trazabilidad.md` (ese si es editable), el ancla segura es el final del archivo, con `assert` antes de borrar — hay varios bloques con el encabezado identico. Si `traza.py` falla, se reporta que la traza no se registro y se sigue.

**3. La mutacion va sobre una COPIA del arbol, no sobre el repo.** `git archive <commit> | tar -x -C <scratchpad>` y `md5sum` contra el original para probar que la copia es fiel. El repo del sistema es read-only para QA, y ademas el fix del implementador puede estar sin commitear: un `git checkout` para revertir un mutante lo borraria.

**How to apply:** driver con falla-cerrado — si el patron no aparece exactamente 1 vez, o el arbol mutado no compila, no corre y lo declara. Y siempre un control negativo (mutacion semanticamente nula, tipo pasar una expresion-cuerpo a bloque) que tiene que dar cero tumbadas: sin el, un driver roto se lee como "ningun mutante sobrevive".

**4. Los mutantes se derivan del DIFF, no de la lista de afirmaciones del arnes.** Una condicion, un filtro o una guarda que el diff agrega = un mutante. Si se derivan de las afirmaciones, el conjunto hereda el punto ciego que venia a detectar.

**Why:** en el modulo 16 el implementador declaro 21 mutantes con cero sobrevivientes, y 13 mutantes mios derivados del diff encontraron TRES sobrevivientes — entre ellos el filtro que el propio commit presentaba como su hallazgo principal. Esta catalogado como `LP-053`.

**How to apply:** el fix que el commit destaca en su mensaje es candidato de riesgo ALTO a quedar sin mutante (el autor ya "lo sabe correcto" y su atencion esta en narrarlo). Y una declaracion de "esto no se puede discriminar" acota de menos por defecto: si la razon es un invariante del sistema, hay que barrer todas las lineas que ese invariante desactiva, no solo la que el autor estaba mirando.

**5. Dos clones, no uno, cuando hay que mutar Y levantar la app.** El driver de mutacion recompila la solucion una vez por mutante, y la app corriendo **bloquea** `<Proyecto>.Infrastructure.dll` (MSB3027). Con un solo arbol hay que elegir: o se mide por mutacion o se prueba por HTTP. Con dos (`C:/qaE5` para mutar, `C:/qaE5w` para servir) las dos cosas corren en paralelo sin tocarse.

**How to apply:** los dos por `git archive HEAD | tar -x`, nunca por `tar` del arbol completo — la copia del arbol se trae carpetas ignoradas (un volcado de migracion dejo **16 GB** y se comio dos minutos antes de que la matara). El `git archive` del mismo repo pesa 15 MB. Ojo que `git archive` **normaliza los fines de linea** (deja CRLF donde el arbol de trabajo tiene LF): la fidelidad se prueba con `diff <(tr -d '' < a) <(tr -d '' < b)`, y los anclas de las mutaciones se adaptan al EOL real leyendo con `newline=''`, porque `io.open` sin eso traduce todo a LF y el ancla con `
` no matchea nunca.

**6. `sed -i` sobre un script que contiene JSON o SQL lo rompe calladamente.** Dos veces en esta corrida: un `sed` de un nombre de campo se llevo las comillas escapadas de un payload JSON, y un reemplazo de `\"` por `'` destruyo los `--data-binary` de curl. Los sintomas se leen como defectos del sistema (el POST vuelve 200 "rechazado", la consulta devuelve vacio).

**How to apply:** si un script de prueba necesita mas de un ajuste, **se reescribe entero con `Write`**, no se parchea. Y para las pruebas HTTP conviene Python con `subprocess` + `curl` desde el principio: los payloads van a archivo (`--data-binary @file`) y las consultas SQL tambien (`mysql < file`), asi no hay una sola capa de comillas que pelear. `PYTHONIOENCODING=utf-8` es obligatorio o el castellano de los mensajes mata el script con `UnicodeEncodeError` de cp1252.

**7. Antes de publicar un defecto apoyado en una tabla sembrada a mano, confirmar que es LA tabla que el guard lee.** Sembre el cierre de caja en `CandadosPeriodoCaja`, el POST entro, y la firma era un blocker perfecto. El guard leia `CierresCajaDiarios`. Lo destapo mirar **como siembra el fixture el arnes que ya cubre ese caso**, en vez de volver a leer mi propia medicion. Es la forma de tabla del aprendizaje 16: el oraculo no era el dato, era mi eleccion de donde escribirlo.

**8. Los arneses de la-platense ABORTAN si la cadena de conexion contiene `laplatense_qa`** (guarda de "solo contra un clon desechable", `return 2`). El clon de un lote llamado `laplatense_qa_lN` cae justo adentro de ese patron, asi que ningun arnes existente corre contra el. Si hace falta correrlos, el clon va con otro nombre (`lp_l2_arnes`); si no, se construye un runner propio — que de todos modos conviene, porque el arnes propio se escribe contra los criterios del lote y no contra los del sprint que lo motivo.

**9. Un oraculo de "desglose por medio de pago" se escribe enumerando TODAS las filas que llevan ese medio, incluidas las REVERSIONES.** Afirme que el bruto de Transferencia de un dia era 850 (la venta con descuento) y el sistema devolvio 1.000,50: le faltaba el Ingreso de 150,50 de la reversion del gasto, que tambien es Transferencia. Se lee exactamente como un defecto de agregacion.

**Why:** al armar el fixture uno piensa en filas por CONCEPTO ("la venta con descuento", "el gasto", "la reversion") y al escribir la afirmacion piensa en filas por MEDIO, y la reversion cambia de grupo entre las dos pasadas.

**How to apply:** antes de afirmar un total por medio, recalcularlo por SQL agrupando por `(MedioPago, Tipo)` sobre el fixture sembrado — es la misma consulta que valida y cuesta una linea. Y dejar en el texto de la afirmacion la cuenta explicita (`850 + 150.50 de la reversion = 1000.50`), que es lo que hace evidente el error en la lectura siguiente.

Relacionado: [[metodo-qa-datos-reales]], [[lotes-en-paralelo]].

**8. Un indice unico sobre una columna GENERADA esconde el nombre de la columna base, y eso rompe cualquier introspeccion de `information_schema.STATISTICS`.** El unico figura como `UX_T_Campo_Vivo (CampoVivo)`: `Campo` **no aparece nunca** en STATISTICS. Un generador de fixtures que pregunta "que columnas participan de otro indice unico de esta tabla" para darles valores distintos por fila no ve `Proveedores.Nombre` ni `Productos.Codigo`, les repite el relleno, y el 1062 llega **del indice hermano y no del medido**: dos casos de 16 se leen como FAIL del sistema. El mapeo es una linea (`if x.endswith("Vivo"): add(x[:-4])`) y sin ella la tabla de resultados esta mal justo en las tablas con dos unicos.

Dos mas del mismo armado de fixtures, las dos con la misma moraleja (si el insert no entra, el caso se lee como defecto):

- **El relleno de una columna NOT NULL tiene que respetar el ANCHO, no solo el tipo.** Un `700000+seed` para "que sea distinto por fila" desborda `tinyint(1)` (los `Activo`/`TemaOscuro`) y `decimal(5,2)` (`PorcentajeIVA`), y los 16 casos vuelven con `ERROR 1264 Out of range`. La variacion por fila hay que darsela **solo** a las columnas que la necesitan; al resto, una constante segura por tipo.
- **Falla-cerrado en el generador de inserts, con `assert`.** Una lectura de `information_schema` que vuelve vacia (pasa con muchas conexiones seguidas de `mysql.exe`) produce `insert into T () values ()`, el caso falla con `Field 'X' doesn't have a default value` y parece el sistema. Dos `assert` lo cierran: que la lista de columnas tenga largo razonable, y que los inserts A/B/C tengan **la misma lista de columnas**. Mas un cache de las consultas de introspeccion, que ademas lo hace cinco veces mas rapido.

**9. Al levantar la app con el puerto asignado del lote, el puerto de https (el +1) puede estar tomado por otro lote.** `ASPNETCORE_URLS` con `http://localhost:<mio>;https://localhost:<mio+1>` murio con `Failed to bind to address https://127.0.0.1:7252: address already in use` — otro lote tenia 7252..7257. `netstat -ano | grep LISTENING` antes de lanzar, y para https un puerto alto propio (`1<mio>`). Para bajarla, el PID sale del mismo `netstat` filtrando por el puerto propio, nunca `taskkill //IM`.
