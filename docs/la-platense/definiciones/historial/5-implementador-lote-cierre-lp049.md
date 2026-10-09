# 5-implementador - bloque archivado: lote de cierre LP-044/LP-045/LP-049 + guarda de MigracionCatalogo (2026-10-07)

Movido de `5-implementador.md` el 2026-10-07 para mantenerlo bajo el techo de 150 KB
(`39-presupuesto-contexto.instructions.md`). Se lee solo si el trabajo lo toca.

## Lote de cierre: guarda de `MigracionCatalogo` + `LP-044`/`LP-045` reabiertos + `LP-049` (2026-10-07)

**Tres commits locales en `entrega-1-migracion`, sin push y sin deploy:** `0624133` (guarda de
`MigracionCatalogo` + barrido de `tools/`), `4246cf7` (`LP-044`/`LP-045`), `99a0732` (`LP-049`).
Sin migraciones EF, sin tocar una linea de logica de negocio, sin tocar vistas mas alla de un
comentario. **Nada se aplico a `laplatense_dev` ni a produccion.**

**Linea base de build, corregida por QA y confirmada por ejecucion:** `0 errores / 9 advertencias`
= 8 `NU1902` + 1 `CS0114` en `HomeController.cs(38,26)`. El `CS0114` **es una advertencia de codigo
y es preexistente de Entrega 1**, no una regresion: la version anterior de este documento decia
"8 advertencias, todas NU1902" y era falsa. Fuera de alcance de este lote.

### 1. `tools/MigracionCatalogo` — la guarda protegia el caso que no hacia falta

El script que **escribe el catalogo entero (112.485 productos)** tenia `laplatense_dev` en una
cadena hardcodeada, **no leia `ConnectionStrings__DefaultConnection`**, y su unica guarda era la de
"catalogo vacio": aborta si el destino YA tiene productos. Eso protege la **carga inicial** y deja
a los **tres modos correctivos** (`--solo-codigo-barras`, `--solo-codigo-propio`,
`--solo-unidad-venta`) sin ninguna proteccion, porque esos modos exigen por definicion un catalogo
**cargado**. La guarda cubria el caso que no hacia falta cubrir y dejaba abierto el que si.

Es la **tercera aparicion de la misma forma**: el arnes del lote 4 que QA observo y por eso no uso,
`ArnesEntrega3Item4c` que la ejecuto de verdad y escribio dev, y esto.

**Lo que se cambio:**

- El destino sale del segundo argumento **o** de `ConnectionStrings__DefaultConnection`, **sin
  default**. Antes, "no nombrar nada" significaba "escribi dev".
- Guarda de **identidad de base** antes de abrir el `DbContext` y **para los cuatro modos**. Lista
  de prohibidas: `laplatense_dev`, `laplatense_qa` (por substring, cubre `_l1`..`_d9`),
  **`db_a7251f_laplaten`** (el nombre de la base de produccion) y `site4now` (su host). Los dos
  ultimos estan porque el host puede cambiar de servidor y el nombre de la base no.
- **Falla cerrado.** Exit **3** si no se puede determinar contra que base se escribe (cadena
  ausente, o sin `Database=`); exit **2** si la base esta prohibida.
- Unica salida: `MIGRACION_CATALOGO_CONFIRMO_BASE` con el **nombre exacto** de la base. No es un
  `--force` ni un `=1`: hay que volver a tipear el nombre. Los correctivos existen para corregir el
  catalogo ya migrado, asi que tienen que poder correr contra la base real — **pero no por omision**.
- El comentario del guard de "catalogo vacio" ahora dice **que nunca fue una proteccion contra la
  base equivocada**, para que nadie lo vuelva a leer como tal.

**Evidencia por ejecucion** (fixture desechable `laplatense_qa_descartable`: 18 migraciones y un
producto centinela en `UnidadVenta = Metro`, que es justo lo que `--solo-unidad-venta` reescribe;
**no se uso `laplatense_dev`**):

| caso | exit | efecto medido |
|---|---|---|
| carga inicial | 2 | centinela intacto |
| `--solo-codigo-barras` | 2 | centinela intacto |
| `--solo-codigo-propio` | 2 | centinela intacto |
| `--solo-unidad-venta` | 2 | centinela intacto |
| sin variable y sin argumento | 3 | **antes escribia dev** |
| cadena sin `Database=` | 3 | nada |
| `CONFIRMO_BASE` nombrando otra base | 2 | centinela intacto |
| `CONFIRMO_BASE` con el nombre exacto | 0 | **ESCRIBE**: Metro -> Unidad |

La ultima fila es la que importa: **la guarda era lo unico que frenaba la escritura**, medido en las
dos direcciones y no solo en la que da verde. Y el **control positivo** cierra el otro extremo:
contra `laplatense_gate_broken` (no prohibida) pasa la guarda de identidad, imprime *"Base de
destino verificada"* y recien ahi choca con la guarda de **estado** (exit 1). Las dos guardas son
distintas y ahora estan ordenadas.

### 2. Barrido de `tools/` — la misma forma con otra cara, en los seis arneses

Los seis arneses **si** leian la variable de entorno (eso se arreglo en la ronda de CR-04), pero
caian a un **default hardcodeado**: `laplatense_item4c`, `laplatense_cr04`, `laplatense_recon_tx`,
`laplatense_seis`, `laplatense_tarjetas`, `laplatense_cr12`. Ninguna es dev, pero todas son "una
base que nadie nombro": con el nombre de la variable **mal tipeado** (un solo guion bajo) el arnes
corre en silencio contra el default y el operador mide contra una base distinta de la que cree haber
nombrado. Los seis ahora **abortan con exit 2**, medido en los seis.

Segundo hallazgo del barrido: las listas de prohibidas tenian **solo el host** de produccion
(`site4now`), no el **nombre** de la base. Un restore local de produccion pasaba. Se agrego
`db_a7251f_laplaten` a las seis y se verifico por ejecucion con `Server=localhost`.

**Dato operativo que casi me hizo medir el codigo viejo:** `tools/` **no esta en la solucion**
(`grep -c tools FerreteriaLaPlatense.slnx` = 0), asi que `dotnet build` de la raiz **no los
compila**. Un `dotnet run --project tools/X --no-build` corre un **binario viejo** y no avisa: la
primera corrida de este barrido dio exit 0 y la base del default, con el arnes ya corregido en
disco. Hay que buildear cada tool aparte.

**`tools/ArnesHotfixTransacciones` es un directorio huerfano**: tiene `bin/obj` y **no tiene
fuente** (ni en el arbol ni en la historia de git). Su `.dll` referencia
`ConnectionStrings__DefaultConnection` y **no** contiene ningun `laplatense*` hardcodeado, asi que
no es la forma del defecto; pero es un ejecutable que nadie puede auditar. Esta gitignoreado, no
viaja. **Recomendado borrar el `bin`/`obj`** — no se hizo en este lote (es basura local, fuera del
diff).

### 3. `LP-044` y `LP-045` — por que el barrido por lectura los dejo vivos

Los dos partes se reabrieron porque **cada uno dejo viva una copia de la misma afirmacion falsa que
vino a borrar**, y las dos estaban **al lado del codigo que las desmiente**. Un barrido que **lee y
clasifica** deja pasar justamente esas. Este se hizo **por patron**, verificando cada comentario
contra la linea siguiente.

- **`LP-045` — `OrdenCompraService.EtiquetaEstado`** decia *"Sin `_ =>`: un estado nuevo en el enum
  lo denuncia el compilador (mismo criterio que el switch exhaustivo de PAT-051)"* **dos lineas
  arriba de su `_ => estado.ToString()`**. Las **dos mitades** eran falsas: con `_ =>` presente no
  hay `CS8509`, y **PAT-051 no es un patron sobre switch exhaustivos** (es "medio/cuenta como
  dimension de un ledger de caja unico"). **Medido sobre este mismo enum**, no heredado de la
  medicion de CR-05: con `EstadoOrdenCompra.MUTANTE_Prueba = 99` agregado, Infrastructure compila
  con **0 errores y las mismas 4 advertencias**. Se corrige el **comentario, no el codigo**: esto
  devuelve una **etiqueta** para un mensaje de error y degradar al nombre crudo del enum es feo pero
  inocuo. El `_ =>` que decide **comportamiento** ya esta cubierto aparte (la guarda de recepcion
  compara contra el conjunto explicito `EstadosRecibibles`, asi que un estado nuevo nace **no
  recibible**). Queda escrito que el barrido de un estado nuevo es **a mano**, con su grep.
- **`LP-044` — `InteresesTarjeta.cshtml:233`** seguia diciendo *"un `<form>` hijo de `<tr>` lo saca
  el parser"*, la misma frase que el parrafo grande del mismo archivo ya habia borrado. Ahora dice
  lo que **QA midio** en tres motores Chromium: el form queda como hijo del `<tr>` y el submit
  postea **la fila completa**, que el servidor guarda; **lo que rompe es la variante sin
  `</form>`**, donde una fila postea **todas** con la clave duplicada — **dato cruzado**, no fila
  vacia. El mecanismo **no se repite**: se remite al parrafo grande, porque tener dos copias es
  exactamente como nacio este defecto.
- **Tercera instancia, que el grep encontro y no estaba en el parte:**
  `OrdenCompraViewModels.PlanEcheqFormViewModel` afirmaba que *"un `<form>` dentro de otro es
  invalido y el parser descarta el interno"*. Es una afirmacion de parser **no medida**, o sea
  exactamente la clase de frase que origino `LP-044`. El **veredicto** se queda (los dos forms son
  hermanos, nunca anidados); la afirmacion sobre el parser **se saca**, con la nota de que si alguna
  vez hace falta, se mide en navegador.

**Los numeros del barrido, con sus greps:**

- `grep -rn "^\s*_ =>" --include=*.cs --include=*.cshtml`: **46 switch con rama de descarte en 31
  archivos**. Verificado el comentario adyacente de cada uno. **Una sola afirmacion falsa viva**: la
  de `EtiquetaEstado`. Confirma el parte.
- `grep -rni "compilador\|no compila\|CS[0-9]\{4\}\|parser\|exhaustiv"`: **3 falsas** (las de
  arriba) y el resto son **correcciones que citan el texto viejo** u **honestas**
  (`OrigenCCEmpleado`: *"no hay enum que el compilador pueda chequear aca"* — es cierto, son
  constantes `string`; `MedioPagoCajaMapper`; el arnes de tarjetas).
- **La unica afirmacion verificable de esta familia que resulto VERDADERA, y ahora esta medida:**
  `Views/Dashboard/Index.cshtml` dice que sin su `@using Microsoft.AspNetCore.Authorization` la
  vista no compila. Se saco el using y el build dio **4 errores `CS1501`**. Queda como esta. Vale
  anotarla: el barrido no es "todo comentario que promete al compilador es falso".
- **Chequeo estructural de las tres variantes de `LP-044` sobre TODAS las vistas**, ignorando
  comentarios (que es lo que ensuciaba la primera pasada: el propio texto del fix contiene
  `<form>`): **0** `<form>` como hijo de `<tr>`, **0** anidados, **0** sin cerrar.

### 4. `LP-049` — el delta, el par de control y el mutante

`ArnesEntrega3Item4c` verificaba *"no quedan filas de prueba"* con
`OrdenesCompra.CountAsync() == 0`, o sea exigiendo que **la base entera** estuviera vacia de
compras. La equivalencia entre "todas las compras" y "las que sembre" es una propiedad del
**fixture**, no de la afirmacion. Mismo defecto que `LP-048` corrigio en
`ArnesSeisSitiosRestantes`; **volvio porque ese barrido se hizo dentro del archivo y no
cross-archivo**.

Ahora se toma una **foto base despues de la limpieza inicial** (lo que la limpieza no borro es, por
definicion, ajeno al arnes) y la afirmacion compara el **delta**. Se imprimen **los dos numeros**,
porque miden cosas distintas: el delta es lo que la afirmacion exige, y el absoluto es la linea base
del fixture, util para notar si alguien **mas** la movio entre corridas. Los contadores pasan a
`LongCountAsync`.

**Par de control de QA, reproducido** contra `laplatense_gate_4c` (que ya traia sembrada la orden
`#8800` del proveedor `SIBON`):

- **antes** del fix: `91 OK / 1 FALLA / exit 1`, y la fallada es *"no quedan filas de prueba"* con
  *"OrdenesCompra restantes: 1"* — el numero exacto del parte.
- **despues**: `92 OK / 0 FALLA / exit 0`, imprimiendo *"OrdenesCompra: 1 (base 1, delta 0)"*.

**Y medido que la afirmacion sigue discriminando**, que es la mitad que un arreglo de instrumento
suele saltearse: mutante `M-LP049` (limpieza final apagada) -> **FALLA** con `delta compras=+4,
pagos=+3, movsCC=+3, movsCajaPagoOC=+2, proveedores ZZTEST=1, productos ZZTEST=1`, exit 1.

**Barrido del patron sobre los 7 tools, afirmacion por afirmacion:** las otras seis limpiezas y los
invariantes de reconciliacion **ya eran relativos** — por prefijo
(`EF.Functions.Like(Prefijo + "%")`), por `VendedorId` o por `VentaId`. **4c era la unica instancia
absoluta del repo.** (`ArnesVentaSinFacturaYParcial` 8.18 filtra por `VentaId`;
`ArnesReconciliacionTx` mide via `LeerEstadoAsync(ventaId, productoId)`.)

### Fixtures: estado al cierre

- `laplatense_gate_4c`: **restaurado al estado de control de QA** (1 orden de compra ajena, 112.485
  productos). El mutante dejo filas y se limpiaron con una corrida del arnes ya corregido.
- `laplatense_gate_cr04`: `ArnesPlanEcheqs` corrio verde (`49 evaluadas / 0 falladas / exit 0`) para
  confirmar que tocarle la lectura de la cadena no le rompio el camino feliz.
- `laplatense_qa_descartable`: **creada y borrada en la ronda.** Se borro tambien el CSV de
  candidatos que dejo la corrida con confirmacion.
- Intactos: `laplatense_dev`, produccion, `laplatense_qa_l1`..`l6`, `laplatense_qa_d9`,
  `laplatense_gate_fix`.

### Pruebas minimas para QA

1. **Re-verificar los tres partes** (`LP-044`, `LP-045`, `LP-049`): aplicados, **pendientes de
   re-verificacion**. El cierre lo declara QA.
2. **La guarda de `MigracionCatalogo`, en los cuatro modos**, contra una base desechable con nombre
   prohibido **y catalogo cargado** (si esta vacia, la guarda de estado podria tapar la de
   identidad y dar un falso positivo). Verificar exit 2 y que no se escribio una fila.
3. **El fallo cerrado**: sin la variable de entorno, los 7 tools tienen que abortar, no elegir una
   base. Ojo con `--no-build`: `tools/` no esta en la solucion.
4. **`ArnesEntrega3Item4c` sobre un fixture con filas ajenas** — tiene que dar `TODO OK` y mostrar
   el delta en 0, no exigir la base vacia.
5. **No hay nada que probar por navegador en este lote**: no cambio una linea de comportamiento.

### Checklist de merge

- [x] Build `0 errores / 9 advertencias` contra la linea base corregida; cero advertencias nuevas
      (ninguna `CS` en los 7 tools).
- [x] Sin migraciones EF; **nada aplicado a `laplatense_dev` ni a produccion**.
- [x] Un commit por item, sin push y sin deploy.
- [x] Evidencia **por ejecucion** de cada guarda nueva, con su exit code y en las dos direcciones.
- [x] Fixtures de QA devueltos a su estado; lo creado en la ronda, borrado.
- [ ] Re-verificacion de QA de `LP-044`, `LP-045` y `LP-049`.
- [ ] Decision de Joaquin: aplicar migraciones a dev y deploy (fuera de alcance de este lote).


