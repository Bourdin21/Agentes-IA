---
description: Estandares de implementacion derivados del barrido de errores QA cross-proyecto. Obligatorio para el implementador — evita repetir errores ya catalogados.
applyTo: "**/*.{cs,cshtml,js}"
---

# 32 - Estandares derivados de errores QA (obligatorios para el implementador)

Fuente: barrido completo de `docs/qa/regresiones-manuales.yml` y los `6-qa.md` de todos los proyectos (ShowroomGriffin, KOI, delicias-naturales, ganaderia, vinosefue) al 2026-07-03. Cada regla abajo tiene su(s) id(s) de origen entre parentesis — ver el catalogo para el detalle completo del caso.

## Combos select / select-multiple en edicion de entidades (regla nueva, patron recurrente no catalogado hasta ahora)

- **Regla:** toda vista de Editar que expone una relacion configurable por combo (Select2 simple o multiple, tags, catalogo many-to-many) DEBE inicializarse con los valores ya asignados a la entidad. Nunca renderizar el combo vacio en Editar cuando la entidad ya tiene datos cargados.
- **Como implementarlo:**
  - En el `Action Editar(int id)` (GET), poblar la propiedad de IDs/objetos seleccionados del ViewModel a partir de la relacion ya cargada de la entidad (no dejar que arranque vacia esperando que el usuario la re-tipee).
  - En la vista, pre-cargar las `<option value=".." selected>` para cada elemento ya asociado, o pasar la seleccion inicial a la config de Select2 (`data`/JSON embebido), ademas del AJAX de busqueda para agregar nuevos valores.
  - Para selects multiples (tags/many-to-many), el POST de Editar debe reconciliar la seleccion enviada contra la relacion existente (altas y bajas), no solo agregar.
- **Como detectarlo en QA:** abrir Editar de una entidad con la relacion ya cargada → el combo debe mostrar los valores existentes ya seleccionados, no en blanco. Si el combo aparece vacio pese a que la entidad tiene datos, es bug bloqueante de esta regla.

## Select2 / autocomplete AJAX (REG-003, REG-005, REG-007, REG-009)

- El mapeo de `processResults` debe usar los nombres de campos **reales** devueltos por el endpoint — nunca inventar campos (ej. `v.descripcion`) sin verificar el DTO/JSON real.
- Declarar siempre `dataType:'json'` en la config de Select2.
- Combos en cascada (ej. categoria → subgrupo) usan querystring (`?categoriaId=`) matcheando la firma del action — nunca segmento posicional que pueda ligar a `0`.
- Detectar: tipear una letra debe devolver >=1 resultado legible; cambiar el combo padre debe repoblar el hijo.

## RowVersion / concurrencia en MySQL (REG-001)

- MySQL no soporta rowversion store-generated como SQL Server. Toda entidad con control de concurrencia asigna `RowVersion` manualmente en `SaveChanges`/`SaveChangesAsync` del DbContext, con `IsConcurrencyToken().ValueGeneratedNever()` en la configuracion Fluent.

## Campos condicionales de un select de negocio (REG-002, REG-006)

- Cuando una opcion de un select condiciona campos adicionales obligatorios (ej. medio de pago "Cuotas" requiere cantidad + % financiamiento; "Cheque" requiere fecha de vencimiento), esos campos deben existir en Domain + DTO + Service + View, con validacion client-side **y** server-side — nunca solo uno de los dos lados.

## Botones de accion derivados del estado real, no hardcodeados (REG-004, KOI-004, VSF-001, VSF-002)

- Los botones de avance de estado en las vistas se derivan de un metodo unico de transiciones validas (`GetTransicionesPermitidas` o equivalente), consultado tanto por la vista (que botones mostrar) como por el controller/service (que transiciones aceptar). Nunca un mapa de botones hardcodeado por estado que pueda desalinearse del service.
- Al definir el diccionario/guard de transiciones validas de una maquina de estados, contrastarlo explicitamente contra la tabla de maquina de estados **aprobada** en `2-disenador-funcional.md`, transicion por transicion — no solo las transiciones "felices". Omitir una transicion documentada (ej. `Borrador -> Cancelada`) es un bug de implementacion, no una decision de alcance.
- Los guards que bloquean una accion por el estado de una entidad **relacionada** comparan contra el conjunto explicito de estados realmente bloqueantes (ej. `[Generada, EnPreparacion, Recibida]`), nunca contra `!= Borrador` u otra comparacion negativa generica que trate estados terminales (Cancelada, Cerrada) igual que estados activos.
- Toda validacion numerica de negocio (ej. consumo <= bruto) requiere bloqueo en JS (`preventDefault` en el submit) **y** en el Service antes de persistir — nunca confiar solo en la validacion de UI.

## Recalculo de UI sin perder foco (REG-008)

- Al recalcular totales/valores derivados en una fila dinamica de un formulario (grilla de pagos, detalle de venta), actualizar solo el/los elementos afectados del DOM. Nunca destruir y re-renderizar todo el contenedor (`tbody`) en cada evento `input`/`keyup` — eso destruye el elemento enfocado y descarrila la escritura del usuario.

## Visibilidad de sidebar vs autorizacion real (REG-010, KOI-003, KOI-005, KOI-006)

- Todo link de sidebar esta respaldado por `[Authorize(Roles=...)]`/policy equivalente en el controller/action de destino (defensa en profundidad) — nunca ocultar un link sin proteger tambien el endpoint, ni agregar un rol a la vista sin agregar su link correspondiente en el sidebar.
- **Pre-merge obligatorio:** antes de dar por terminado un modulo con entrada en sidebar, verificar **por revision de codigo** (nunca ejecutando la app — el Implementador no hace smoke test, ver `00-operativa-global.instructions.md`) que el controller/action referenciado existe, la ruta coincide con el link del sidebar, y el atributo de autorizacion (`[Authorize(Roles=...)]`/policy) es el esperado para cada rol que deberia verlo. No asumir que el link funciona solo porque el proyecto compila. La verificacion en caliente (que efectivamente responda 200 para cada rol) queda a cargo del usuario/cliente de forma manual.

## Confirmaciones SweetAlert2 fuera del `<form>` (KOI-001)

- El handler generico de confirmacion SweetAlert2 (`btn-swal-confirm`) resuelve el form asociado por `data-form-id` / `data-form` / `data-action` como fallback explicito a `closest('form')` — no asumir que el boton de accion siempre esta dentro del `<form>` que debe enviar.

## Listados DataTable server-side con Include de colecciones (DN-001, DN-002)

- En cualquier listado DataTable server-side que combine 2+ `Include` de coleccion + filtro dinamico + `OrderBy` dinamico + `Skip`/`Take`, separar en dos queries: (1) proyectar solo Ids con `Where`/`OrderBy`/`Skip`/`Take` sin Include de coleccion; (2) segunda query con los Include completos filtrando por esos Ids, reordenando en memoria segun el orden de la primera query.
- Aplicar este patron **preventivamente** en todo listado nuevo con Include de coleccion combinado con orden/filtro dinamico — no esperar a que se reproduzca el error 500 para aplicarlo.

## Guards de "al menos un item" sobre listas dinamicas (GAN-001)

- El guard de "debe haber al menos un item" en una lista dinamica bindeada por indice (`Pagos[i]`, `Items[i]`) nunca se basa solo en `Count == 0` — el model binder de MVC preserva el valor por defecto del constructor del ViewModel cuando no llega ningun campo indexado, por lo que `Count` puede ser `>=1` con datos vacios. Validar en cambio que al menos un item tenga datos reales (ej. `!vm.Items.All(p => p.Importe <= 0)`) y mostrar el mensaje de negocio especifico — no solo el error generico de rango del campo.

## Templating JS dentro de Razor (GAN-003)

- Nunca usar `<script type="text/x-template">` con Tag Helpers (`<partial>`, etc.) adentro — Razor no procesa Tag Helpers dentro de elementos `<script>`/`<style>`/`<textarea>`/`<title>` (raw text elements de HTML5, se tratan como texto literal). Usar `<template>` (elemento HTML5 nativo) para plantillas de fila/JS, y leer su contenido con `.innerHTML` (nunca `.textContent`).

## Autocomplete: Select2 sobre `<datalist>` nativo (GAN-004)

- No usar `<input list>` + `<datalist>` nativo para autocomplete — tiene quirks de refresco de desplegable no confiables entre navegadores tras poblar asincronicamente. Usar siempre Select2 (ya establecido en el design system, `25-frontend-design-system.instructions.md`) para cualquier campo de autocomplete/sugerencias.

## Backfills que no filtran por el estado de la entidad relacionada (VSF-001)

- Scripts de backfill/migracion que propagan FK o estado desde una entidad padre a sus hijos filtran/validan contra el estado **actual** de la entidad relacionada en el momento del backfill — nunca copian el valor ciegamente sin considerar que la entidad de destino puede estar en un estado terminal (Cancelada, Cerrada) que cambia el comportamiento esperado.

## Venta con IVA + pago dividido en multiples metodos (patron nuevo, PAT-003)

- **Regla:** el IVA es una propiedad de las lineas de producto de la venta (VentaDetalle/VentaItem: PorcentajeIVA, ImporteIVA por linea), nunca del pago. El pago es independiente y puede dividirse en N lineas (VentaPago: MedioPago, Importe, + campos condicionales segun medio — CantidadCuotas/PorcentajeFinanciamiento para Cuotas, FechaVencimiento para Cheque, etc., ver seccion "Campos condicionales de un select de negocio" arriba).
- **Validacion obligatoria (bloqueante, client-side Y server-side):** la suma de `VentaPago.Importe` de todas las lineas de pago de una venta debe ser exactamente igual al `Total` de la venta (Total = suma de subtotales + IVA de todas las lineas de producto). Nunca permitir guardar una venta con pagos que no cierran contra el total, ni de mas ni de menos.
- **Como implementarlo:**
  - En el ViewModel/JS de Crear: recalcular en vivo la diferencia pendiente (`Total - Σ Pagos`) cada vez que se agrega/edita/quita una linea de pago; bloquear el submit (`preventDefault`) mientras la diferencia sea distinta de 0.
  - En el Service, antes de persistir: repetir la misma validacion de suma server-side — nunca confiar solo en el bloqueo de UI (mismo criterio que "Campos condicionales" y los guards de GAN-004 arriba).
  - Redondeo: si la division de centavos no cierra exacto (ej. total con 2+ decimales repartido en 3 pagos), definir explicitamente el criterio de redondeo (normalmente: el ultimo pago agregado absorbe el centavo de diferencia) y dejarlo documentado en el analisis funcional del modulo — no dejarlo implicito en el codigo.
  - No confundir con el guard de "al menos un item" (GAN-001 arriba) — ese guard evita una lista de pagos vacia; esta regla nueva valida que la lista, aunque no este vacia, efectivamente sume el total correcto.
- **Como detectarlo en QA:** crear una venta con producto(s) con IVA, agregar 2+ lineas de pago (ej. efectivo + tarjeta + transferencia) cuya suma sea distinta al total → debe bloquear con mensaje claro, nunca guardar. Agregar lineas de pago cuya suma sea exactamente el total → debe guardar sin error.
- **Origen:** formalizado 2026-08-15 a partir de un caso de negocio planteado por el usuario (venta con % IVA y pago repartido en mas de un medio) — no hay bug reproducido todavia en `regresiones-manuales.yml`, es una regla preventiva derivada del patron ya existente (ShowroomGriffin, ganaderia via GAN-001) que le faltaba esta validacion explicita. Aplica a **todo proyecto con modulo de venta de productos**, no solo a los que ya lo tienen.

## Mantenimiento de este catalogo

- Cuando el agente QA confirma un bug funcional nuevo y su fix (ver `30-qa-regresiones.instructions.md`), evaluar si el patron de causa raiz es generalizable (no especifico de un solo proyecto). Si lo es, agregar una seccion nueva a este archivo ademas del item en `docs/qa/regresiones-manuales.yml` — este archivo es el que efectivamente lee el implementador en cada implementacion nueva, el YAML es el catalogo de deteccion/reproduccion de QA.
