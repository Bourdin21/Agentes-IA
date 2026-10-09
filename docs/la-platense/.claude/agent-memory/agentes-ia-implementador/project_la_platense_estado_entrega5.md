---
name: la-platense-estado-entrega5
description: Estado de La Platense al 2026-10-07 tras el lote 2 de la Entrega 5 — alcance comprometido CERRADO salvo AFIP real, nada deployado, y la linea base de los cuatro arneses
metadata:
  type: project
---

Al **2026-10-07**, en la rama `entrega-1-migracion`: **el alcance comprometido esta CONSTRUIDO Y
MEDIDO COMPLETO salvo AFIP real.** CR-01 a CR-05, el modulo 16 (notas de credito) y el flujo 16
(devoluciones) estan en commits locales **sin push y sin deploy**. Produccion esta **10 migraciones
atras** (8 aplicadas de 20), por pedido explicito de Joaquin.

**Why:** el acumulado local no se despliega hasta que Joaquin lo decida; cada ronda cierra con commit
local y lo declara. Lo que queda es **un gate externo** (el certificado `.p12` y el CUIT real del
cliente) y **el deploy**, que ademas esta bloqueado por una credencial de FTP/Web Deploy rotada.

**How to apply:** al retomar este proyecto, antes de planificar nada:

- **AFIP sigue deshabilitado** y es el **unico** gate funcional. Los comprobantes y las notas de
  credito nacen en `Pendiente` sin CAE y eso es el estado **normal**, no una anomalia.
- **RIESGO QUE HAY QUE RESOLVER *ANTES* DE HABILITAR AFIP, declarado en el lote 2 y hoy
  inalcanzable:** `FacturacionParcialService.ObtenerYaFacturadoPorItemAsync` **SI** cuenta los
  comprobantes en `Error` (su filtro es solo de soft delete) y el planificador de notas de credito de
  `DevolucionService` **NO** (usa el criterio de habilitacion, que los excluye por R17). Con un
  comprobante en `Error`, un item apareceria como "facturado" en el pendiente y **no generaria NC al
  devolverse**. Es una asimetria **preexistente** y hoy ningun servicio produce un `Error` — el dia
  del certificado deja de ser teorica.
- **`LP-052` y `LP-053` estan APLICADOS y PENDIENTES DE RE-VERIFICACION** (commits locales `001d983`
  y `5382fb6`). `LP-054` fue una falla de metodo de QA y quedo **adoptada como regla**: la base de
  prueba se arma con `dotnet ef database update`, **nunca** con `mysqldump --no-data`, que borra las
  filas que siembran las migraciones y deja dos arneses sanos dando numeros distintos.
- **`LP-037`, `LP-041` y `LP-039` siguen aplicados y pendientes de re-verificacion** desde los
  commits `408b814`, `41ec1b2` y `f05cc92`. El cierre de un defecto lo declara QA, nunca el
  implementador.
- **EL MECANISMO UNICO DE HABILITACION ES AHORA LA FORMA DE CONSTRUIR, no un fix.**
  `FerreteriaLaPlatense.Domain/Reglas/HabilitacionDeAccion.cs` devuelve **la razon por la que NO se
  puede** (`null` = se puede) y la consumen **las tres puntas**: la vista, el `GET` y el `POST`. Si un
  criterio de habilitacion aparece en dos archivos, **se mueve ahi**. Cuatro apariciones del mismo
  defecto (`LP-039`, `LP-040`, el combo de Editar de una compra y `LP-052`) lo justifican. Lo que NO
  entra: las guardas de concurrencia (son la segunda mitad de la relectura bajo lock) y los topes por
  item.
- **LINEA BASE DE LOS CUATRO ARNESES, medida el 2026-10-07 y todos idempotentes:**
  `tools/ArnesReconciliacionTx` → **153 OK / 0**; `tools/ArnesSeisSitiosRestantes` → **32 OK / 0**;
  `tools/ArnesNotaCredito` → **63 OK / 0** (era 45 antes de `LP-053`);
  `tools/ArnesDevoluciones` → **63 OK / 0** (nuevo). Cualquier otro numero es una regresion o un arnes
  corriendo en condiciones distintas. **`tools/` NO esta en la solucion: hay que compilar cada uno
  explicitamente** (`dotnet build tools/ArnesX`, uno por invocacion — `dotnet build` con dos
  proyectos da `MSBUILD : error MSB1008`) o se corre el binario viejo sin aviso.
- **La guarda de identidad de los arneses es por SUBSTRING.** Una base llamada `laplatense_dev16`
  **aborta con exit 2** porque contiene `laplatense_dev`. Es la guarda funcionando: el nombre de la
  base desechable no puede **empezar** con el de una prohibida.
- **Techo de 150 KB:** `5-implementador.md` quedo en **147 KB** y `trazabilidad.md` en **122 KB**. La
  proxima entrada del primero lo cruza: archivar **antes** de escribir. `archivar_memoria.py` no lo
  flaggea por debajo de 150 KB y **ya fallo dos veces** en ese archivo, asi que se archiva a mano
  moviendo el bloque de sprint mas viejo a `historial/` y dejando un puntero.
- **`traza.py` NO tiene modo "reemplazar".** Si se registra la traza sin `--nota`/`--reintentos`
  queda una fila degenerada en `trazas.tsv` **para siempre**, porque ese archivo se toca **solo** con
  el script (editarlo a mano le costo una corrida entera a QA). Hay que llamarlo **una vez, con todos
  los flags**. Y el bloque markdown que deja en `trazabilidad.md` tiene un encabezado que **se repite**
  (hay varios "Traza de corrida -- <fecha> / etapa implementacion"): borrar por encabezado se llevo
  puesta la traza equivocada una vez, asi que se borra **por posicion verificando el contenido exacto
  de cada linea**.
- **Fuera de alcance y sin construir:** los impuestos de v2. **Y no queda ningun CR pendiente.**
- Produccion tiene **2.990 clientes** y **112.485 productos** con actividad real: toda migracion se
  piensa aditiva. El deploy esta bloqueado por la credencial de FTP/Web Deploy (`530`, rotada) y la
  regla es **base y sitio en la misma ventana**.

Las bases a no tocar nunca al verificar: `laplatense_dev`, los fixtures de QA (`laplatense_qa*`,
`laplatense_gate*`) y produccion (`site4now`). Los arneses abortan solos si la cadena las menciona.
