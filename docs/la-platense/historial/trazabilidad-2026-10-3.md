<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-06 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (1 bloques archivados)

- 2026-10-06 - implementador-dotnet (HOTFIX de transacciones de ventas, rama de produccion)

---

### 2026-10-06 - implementador-dotnet (HOTFIX de transacciones de ventas, rama de produccion)

- Etapa: Implementacion. **Rama nueva `hotfix-transacciones-ventas`, creada desde el commit
  `2580f7c`** — lo publicado hoy en `ferreterialaplatense.com.ar` — y **NO desde
  `entrega-1-migracion`**, que tiene 7 commits de desarrollo encima que no se pueden publicar.
  **Esto no es parte de las olas**: es un hotfix sobre el estado exacto de produccion, y asi hay que
  leerlo en la memoria del proyecto. Detalle completo en la seccion "Hotfix de transacciones de
  ventas" de `definiciones/5-implementador.md` (v17).
- **Por que existio:** el codigo publicado tenia **cero** `BeginTransaction` en
  `VentaWorkflowService`. `ConfirmarAsync` descontaba stock, posteaba el movimiento de caja y
  debitaba la cuenta corriente del cliente decidiendo sobre una lectura sin lock;
  `FacturarAsync` tenia la misma forma y podia emitir **dos CAE de AFIP por la misma venta**.
  Produccion no tiene daño hecho (cero transacciones reales), pero el riesgo se materializaba en la
  primera venta real del cliente.
- **Reutilizacion (paso 1 del escaneo):** hit en `cat_resumen.txt` → **`PAT-059`**. El mecanismo se
  porto del commit `bdfd99b` del mismo repo (`BloqueoDeFila`: `SELECT ... FOR UPDATE` del documento
  dueño + relectura bajo lock, con la transaccion abierta **antes de LEER**). **Sin entrada nueva al
  catalogo**: `PAT-059` ya documenta el patron y este hotfix es su segundo consumidor.
- **Adaptacion, no copia:** de las 7 constantes de tabla del helper original **solo 3 existen en
  produccion**, y se dejaron las 2 que el hotfix bloquea. Su XML-doc fundamentaba la decision contra
  el indice unico hablando de las **reversiones parciales de `AnularAsync`**, metodo que **no existe
  en la rama publicada** (llego en `59dd715`): copiar ese texto habria plantado un comentario
  prescriptivo que describe codigo ausente, que es el defecto `LP-008`.
- **Dos premisas del brief refutadas EJECUTANDO** (pasada 0 del barrido `LP-002`), las dos escritas
  en el codigo como "lo que NO estaba roto": (a) la falla parcial **ya estaba cubierta** por el
  `SaveChanges` unico mas la transaccion implicita de EF — verificado abortando el INSERT de caja con
  un trigger `SIGNAL`, y el criterio 2 **pasa tambien contra el codigo roto**; el metodo era atomico
  *por accidente*. (b) El stock **no se duplicaba, se perdia**: los dos competidores leian 100 y
  escribian 98, y el resultado coincidia con el correcto **por casualidad** (lost update que se tapa
  solo). Las de plata si se duplicaban, deterministas.
- **Alcance estricto:** `ConfirmarAsync` y `FacturarAsync`. **SIN migracion EF.** Diff aditivo de 3
  archivos (+93/−0), de las cuales 20 son codigo. Cero Controllers, cero vistas, cero interfaces.
- **Evidencia:** build 0 errores (9 advertencias, todas preexistentes). Arnes propio
  `tools/ArnesHotfixTransacciones` con un scope de DI por competidor (conexion MySQL separada,
  abierta antes de la barrera) y `Barrier`: **46 afirmaciones, 46 OK** con N=3 y N=8, contra el clon
  `laplatense_hotfix_tx` (8 migraciones exactas de `2580f7c`). **Lo que mas vale: el arnes se corrio
  contra el CODIGO ROTO y dio 12 fallas** — N=8 da 2 exitos, $ 2.840 de caja y $ 2.000 de CC donde
  correspondian $ 1.420 y $ 1.000, y `FacturarAsync` **emitio 8 comprobantes AFIP**. Un arnes verde
  que no se probo contra el defecto no prueba nada.
- **Atendida la observacion de QA del lote 4:** el arnes de la ronda anterior apuntaba a
  `laplatense_dev` hardcodeado y escribia la base compartida. Este tiene una **guarda que aborta** si
  la cadena de conexion menciona `laplatense_dev`, `laplatense_qa` o `site4now`, es idempotente
  (prefijo `ZZHOTFIX`) y QA lo puede re-correr.
- **Barrido: 7 sitios mas que mueven plata o stock sin lock, RELEVADOS Y NO TOCADOS** por pedido
  explicito del brief. El peor es **`GastoService.AnularAsync`** (misma forma exacta del defecto
  arreglado, dos Ingresos de caja por el mismo gasto, **alcanzable hoy en produccion**), seguido de
  `RegistrarCobroAsync` y de `CancelarBorradorAsync`. Dato transversal: **no hay indice unico sobre
  `CajaMovimientos` ni sobre `MovimientosCCCliente`**, asi que el lock de fila es el unico mecanismo
  disponible en esas dos tablas.
- **Huerfano de AFIP declarado en el codigo, no improvisado:** si el proceso muere entre la respuesta
  de AFIP y el commit, el CAE existe en AFIP y no en el sistema. Pide un estado intermedio persistido
  (columna + enum + migracion), que no entra en un hotfix; AFIP esta deshabilitado, asi que el camino
  no se puede ejecutar en produccion. Queda escrito con la condicion: **resolverlo ANTES de habilitar
  la facturacion**, no despues.
- **Produccion sin tocar** (ni Web Deploy ni `mysql8001.site4now.net`). `laplatense_dev` sin tocar y
  los fixtures `laplatense_qa_l1..l6` y `laplatense_qa_d9` **intactos**. Commit local, **sin push y
  sin deploy**: el deploy lo ejecuta Joaquin despues de la re-verificacion de QA. El repo
  `Agentes-IA` **no se commiteo**.
- **Riesgo de deploy: CERRADO por Joaquin.** Las migraciones de produccion son **exactamente las 8
  de esta rama**; el "5 migraciones atras" de la memoria era de la rama de DESARROLLO. El hotfix no
  necesita ninguna. Tambien descarto el indice unico como refuerzo en
  `CajaMovimientos`/`MovimientosCCCliente`: el lock de fila es el unico mecanismo posible ahi.
