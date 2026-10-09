<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-09 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M29 (1 bloques archivados)

- M29 - Re-verificacion: el chip del hilo nombra al cliente, y la rama que nunca corrio (OLV-041)

---

# M29 - Re-verificacion: el chip del hilo nombra al cliente, y la rama que nunca corrio (OLV-041)

Estado: **implementado 2026-10-02; 1 commit local, sin push y sin deploy. SIN MIGRACION.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `1e71bed`. Entrada: el parte **OLV-041 (minor)** de la ronda de
re-verificacion de M29 en `6-qa.md` (M29 quedo **apto con reparos, liberable**; OLV-038/039/040 **cerrados**) y el
analisis de QA de la **rama muerta** en `Detalle.cshtml`. Diseno: **D-02** y **D-04** de «Diseno M29».

## OLV-041 (minor) - El hilo tenia la mitad de la comparacion

El diagnostico de QA es exacto y es la **tercera vez de la misma clase** (OLV-030, OLV-038/039, esta): el arreglo
anterior le dio al DTO los campos que necesitaba la **accion** (`SinCliente`, `Version`) y no el que necesita la
**lectura** (`NombreCliente`). D-02 pide *«solo en esta conversacion»* **contra el nombre del cliente**, y en el hilo
habia un solo lado de esa comparacion: el compositor decia «unico-uno.txt | Cliente Beta QA» y el hilo solo el nombre
del archivo.

- `AdjuntoMensajeDto` suma **`NombreCliente`** (nullable, default null: ninguna llamada existente cambio).
- `ServicioTareas.ObtenerDetalleAsync` lo proyecta en la **misma consulta** que ya traia el estado y el token, con
  `NombresClientesAsync` (que ya existia y ya incluye a los dados de baja). Un documento que no se encontro no tiene a
  quien nombrar; uno dado de baja **si** lo nombra (el chip dice «(dado de baja)» y en que carpeta quedo sigue siendo lo
  que la persona vino a leer).
- `_Conversacion.cshtml` gana el `else if` del `@if (a.SinCliente)`, con la **misma clase** (`ov-chip-adjunto__destino`)
  y el mismo renglon que usa el JS. Solo tokens `--ov-*`; **sin fecha ni cuenta regresiva** (D-04 intacto).

## Comparacion de los dos chips, campo por campo (lo que pidio Joaquin)

Es MH-041 aplicado a los **dos renderizadores del mismo objeto**: `ovChipsAdjuntos` (JS, el compositor) y
`_Conversacion.cshtml` (Razor, el hilo).

| Campo | JS (compositor) | Razor (hilo) | Veredicto |
|---|---|---|---|
| clase `--transitorio` | `a.transitorio` | `a.SinCliente` | igual |
| nombre del archivo | texto | texto, enlazado a `Documentos/Ver` si vigente y miembro | **diferencia deliberada**: en el compositor el archivo todavia se esta componiendo y el enlace se llevaria el borrador |
| leyenda «solo en esta conversacion» | si | si | igual, mismo texto del Diseno |
| accion «Guardar en un cliente» | si (marcada, la atiende el camino unico) | si, con `SePuedeGuardar && esMiembro` | igual: el compositor solo existe donde `PuedeAdjuntar` (autor y miembro) |
| **nombre del cliente** | `a.cliente` | **faltaba** | **ERA LA DIFERENCIA.** Cerrada |
| clase `--baja` / «(dado de baja)» | no tiene | si | deliberada: un archivo recien subido o recien elegido de la lista es vigente por construccion |
| boton «quitar» | si | no tiene | deliberada: un turno ya enviado no suelta sus adjuntos |

**Y habia una segunda, que el arreglo ingenuo abria al reves.** El JS saca el nombre de `DocumentoOpcionDto.Cliente`,
que es **null cuando la lista ya esta filtrada por un cliente** (una tarea de trabajo): ahi el compositor **no** nombra
al cliente. Proyectar el nombre siempre en el servidor habria dejado el hilo diciendo algo que el compositor no dice:
**la misma clase de defecto, invertida.** Asi que la regla quedo escrita **una sola vez y valiendo en los dos lados**:
el chip nombra al cliente **solo cuando la conversacion no es de un cliente**, que es donde conviven un transitorio y
uno guardado y la comparacion de D-02 tiene sentido; con cliente en la tarea, el encabezado ya lo nombra y repetirlo en
cada chip es ruido. Con eso, **no queda ninguna otra diferencia** entre los dos chips.

## La rama muerta de `Detalle.cshtml`

QA probo que el caso del **miembro no autor no existe**: `Visibles()` filtra `UsuarioId == usuarioId`, asi que ningun
no-autor abre ninguna tarea (404, candado aislado), y los otros dos caminos a `PuedeAdjuntar = false` tampoco encienden
la rama. El `else if (ViewBag.PuedeNuevaTarea is true && Model.HayAdjuntosParaGuardar)` que metia
`_ModalGuardarEnCliente` suelto **nunca corrio**.

- Se **borro** la rama y en su lugar quedo **un comentario** que dice por que no hace falta, para que el proximo no la
  reponga «por si acaso»: `chip-ofrece => modal-presente` ya lo garantiza la condicion compartida
  (`AdjuntoMensajeDto.SePuedeGuardar`), y con `PuedeAdjuntar` true el modal entra por `_ModalDocumentos`.
- Se borro tambien **`TareaDetalleDto.HayAdjuntosParaGuardar`**, que existia **solo** para alimentar esa rama y cuyo
  comentario («es la condicion que decide que el modal este en la pagina») ya era falso. Dejar la condicion viva habria
  sido dejar el codigo muerto una capa mas abajo. Cero referencias restantes (`src/` y `tests/`).
- Codigo que nunca corre no se prueba, y lo que no se prueba **miente sobre la cobertura**.

## Cambios por capa

- **Application** (`Motor/IMotorAgentes.cs`): `AdjuntoMensajeDto.NombreCliente` nuevo (nullable, al final, con default);
  `TareaDetalleDto.HayAdjuntosParaGuardar` eliminado; el XML de `SePuedeGuardar` actualizado (ya no cita la propiedad
  borrada).
- **Infrastructure** (`Services/Motor/ServicioTareas.cs`): la proyeccion de adjuntos pasa de `ToDictionaryAsync` a
  `ToListAsync` + diccionario en memoria para poder resolver los nombres de cliente en una consulta aparte, con la
  compuerta `tarea.ClienteCarteraId is null`. **Una consulta mas, y solo en las conversaciones sin cliente.**
- **Web** (`Views/Tareas/_Conversacion.cshtml`): el `else if` del nombre del cliente. `Views/Tareas/Detalle.cshtml`: la
  rama muerta reemplazada por el comentario.
- **Tests** (`ChipDelTransitorioEnElHiloTests.cs`): 2 facts nuevos; `SembrarHiloAsync` gana el parametro
  `conClienteEnLaTarea`.
- **Migraciones EF: ninguna.** No se toco ninguna entidad.

## Prueba de mutacion (hecha, no supuesta)

Los dos tests nuevos se probaron **rompiendo una cosa cada vez**, con rebuild (una vista no se recarga sola):

| Mutacion | Resultado |
|---|---|
| `else if (false && !string.IsNullOrEmpty(a.NombreCliente))` en `_Conversacion.cshtml` | **1 falla**, y es `El_chip_del_guardado_en_el_hilo_dice_en_que_cliente_quedo_y_el_del_transitorio_no`. Los otros 5 verdes |
| sin la compuerta `tarea.ClienteCarteraId is null` (nombres de cliente siempre) | **1 falla**, y es `En_una_conversacion_que_ya_es_de_un_cliente_el_chip_no_lo_repite`. Los otros 5 verdes |

La segunda mutacion importa: ese test es un `DoesNotContain` y **pasaria verde con la guarda rota** si no se verificara
por mutacion. Lleva ademas control positivo (el nombre del cliente **si** esta en la pagina, en el encabezado), para que
lo que se mida sea el chip y no «la pagina no habla de Panaderia».

Detalle de tecnica: Razor **escapa el no-ASCII** (no hay `WebEncoderOptions` configurado), asi que los asserts comparan
contra `HtmlEncoder.Default.Encode("Panaderia Norte")` y no contra el literal: un `Contains` con la «i» acentuada cruda
habria fallado por el encoder y no por el defecto.

## Evidencia

- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta, 0 errores** (15 advertencias, todas preexistentes:
  NU1902 de ImageSharp, NU1510 y tres de analizadores xUnit en tests viejos).
- `dotnet test tests/OlvidataAgentes.Tests` (sin pipe, leyendo el resumen completo) -> **Con error: 0, Superado: 1223,
  Omitido: 0, Total: 1223**. Se partio de 1221; los 2 nuevos son los de OLV-041.

## Pruebas minimas para QA (re-verificacion)

1. **OLV-041 - aplicado, pendiente de re-verificacion.** En un hilo **sin cliente** (chat libre o configuracion) con un
   adjunto de cliente y un transitorio: el chip del guardado muestra el nombre del cliente en los **dos temas**, y el del
   transitorio sigue diciendo «solo en esta conversacion» **sin fecha ni cuenta regresiva**.
2. **El repintado.** Guardar el transitorio desde el chip del hilo y leer el chip repintado **sin recargar**: tiene que
   aparecer el cliente elegido (lo rehace el servidor, que es a quien avisa `ov:adjunto-guardado`).
3. **La compuerta, a proposito.** En una tarea de **trabajo con cliente**, el chip del hilo **no** nombra al cliente - y
   el del compositor tampoco. Es la regla, no un residuo: si se califica como defecto, lo que hay que discutir es la
   regla en los dos lados, no el hilo solo.
4. **La rama muerta.** Con `PuedeAdjuntar` true el modal «Guardar en un cliente» sigue en la pagina (entra por
   `_ModalDocumentos`): el chip no puede ofrecer la accion sin que el modal este.
5. **Nada de lo cerrado se afloja:** CA-02.4 (el transitorio sigue afuera de todo listado), B-07, CA-03.1, OLV-038,
   OLV-039 y OLV-040.

## Riesgos y supuestos

- **La compuerta por cliente de la tarea es una decision, no un olvido.** Esta escrita en tres lugares (el XML del DTO,
  el comentario de la consulta y el test), justamente porque es lo que un re-test ingenuo leeria como el defecto sin
  arreglar.
- **Se borro una propiedad publica del DTO** (`HayAdjuntosParaGuardar`). Cero referencias en `src/` y `tests/`, y el
  build lo confirma; si alguien la agrega de nuevo, el comentario que quedo en su lugar explica por que no hace falta.
- **Una consulta mas** en el detalle de las conversaciones sin cliente, acotada a los ids de los documentos del hilo.

## Checklist de salida para merge

- [x] Build limpio y **1223** tests verdes (se partio de 1221).
- [x] **Un test que falla sin el arreglo**, verificado por mutacion en los dos tests nuevos.
- [x] **Sin migracion EF** (no se toco ninguna entidad).
- [x] Solo tokens `--ov-*`; sin fecha ni cuenta regresiva (D-04).
- [x] Ningun valor de M6 tocado; no se publico ni se desplego nada; la app no se levanto.
- [x] Commit local, sin push.
- [ ] **OLV-041: aplicado, pendiente de re-verificacion.** El cierre lo declara QA en contexto nuevo.
