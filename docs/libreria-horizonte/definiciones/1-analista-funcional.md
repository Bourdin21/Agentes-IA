# Memoria - Analista funcional

## Proyecto: libreria-horizonte
## Ultima actualizacion: 2026-09-15

## Definiciones vigentes

### Contexto y problema (Discovery)
- Negocio: Librería Horizonte, local unico en Dr. Tristán Narvaja 1587, Montevideo, Uruguay. Sin web ni mail publico. Contacto por WhatsApp (59898250702, nombre "Equipo").
- Canal: outbound frio (07/09) → respuesta "Si, contame mas" → 15/09 pregunta precio y alcance → escalado a humano.
- Sistema actual: **Fixed** (fixed.uy), plan **Basico** con comprobantes ilimitados y control de stock para **una sucursal**. Se usa para facturar (CFE/DGI).
- Canal online: **MercadoLibre Uruguay**, **67.534 publicaciones**, el cliente **no sabe cuantas estan activas**.
- Proceso actual: el stock en ML lo actualizan **a mano los empleados** de la libreria.
- Dolor declarado (textual): "publicaciones activas sin stock en Fixed que respalde y viceversa".
  - Direccion 1: publicacion activa en ML sin stock real → venta que hay que cancelar → golpe a la reputacion de la cuenta ML.
  - Direccion 2: libro con stock en Fixed sin publicar o con cantidad mal cargada → venta perdida.
- Objetivo de negocio: que lo publicado en ML refleje el stock real, sin carga manual masiva.

### Modulos/features analizados
- **Paso 1 — Limpieza del catalogo ML (servicio unico):** cruzar el stock de Fixed contra las 67.534 publicaciones, pausar las que no tienen stock, corregir cantidades, listar libros con stock sin publicar y reportar.
- **Paso 2 — Sincronizacion diaria (agente, recurrente):** mantener alineados Fixed y ML de forma continua despues del Paso 1.

### Casos de uso principales
- CU-01 (Paso 1): el cliente entrega export de stock de Fixed + export de publicaciones ML.
- CU-02 (Paso 1): el estudio cruza ambos catalogos y clasifica cada publicacion (con stock / sin stock / cantidad distinta / sin cruzar).
- CU-03 (Paso 1): se revisan los casos ambiguos (mismo libro con titulo/edicion distinta) antes de tocar nada.
- CU-04 (Paso 1): se aplican las pausas y correcciones en ML y se verifica una muestra.
- CU-05 (Paso 1): el cliente recibe un reporte de resultados y el listado de libros sin publicar.
- CU-06 (Paso 2): un empleado sube el export diario de Fixed; el sistema propone los cambios en ML.
- CU-07 (Paso 2): un empleado aprueba el lote de cambios y el sistema los aplica en ML.
- CU-08 (Paso 2): las ventas de ML quedan listadas para descontarlas en Fixed.
- CU-09 (Paso 2): los libros que no se pudieron vincular quedan en una bandeja de revision manual.

### Reglas funcionales acordadas
- RF-01: nunca se **borra** una publicacion de ML; solo se **pausa** o se ajusta la cantidad (reversible, conserva historial y reputacion del item).
- RF-02: Fixed no se modifica desde el sistema (no hay API de stock confirmada); toda escritura en Fixed sigue siendo manual.
- RF-03: el cruce va de lo seguro a lo dudoso: ISBN → codigo/SKU → titulo+autor aproximado → revision (IA o manual). Ningun cruce aproximado se aplica sin revision.
- RF-04: una publicacion sin cruzar **no se pausa** automaticamente en el Paso 1: va a revision (evita pausar un libro que si hay).
- RF-05 (Paso 2): ningun cambio en ML se aplica sin aprobacion de un usuario de la libreria.
- RF-06: alcance limitado a **stock/estado**; precios, fotos, titulos y categorias quedan fuera.

### Criterios de aceptacion vigentes
- CA-01 (CU-02): cada publicacion del export ML queda en exactamente una categoria: con stock / sin stock / cantidad distinta / sin cruzar.
- CA-02 (CU-02): el reporte informa cuantas publicaciones cruzaron por cada metodo (ISBN, codigo, titulo, revision).
- CA-03 (CU-04): toda publicacion activa cruzada con stock 0 en Fixed queda pausada en ML.
- CA-04 (CU-04): en una muestra aleatoria de 30 publicaciones modificadas, 30/30 reflejan el estado/cantidad esperado en ML.
- CA-05 (CU-04): ninguna publicacion es eliminada.
- CA-06 (CU-05): el listado de libros con stock en Fixed sin publicacion activa incluye codigo, titulo y cantidad.
- CA-07 (CU-06/07): tras aprobar un lote, cada cambio queda en estado Aplicado o Fallido con motivo visible.
- CA-08 (CU-08): toda venta de ML del periodo aparece una sola vez en la lista de "a descontar en Fixed" y puede marcarse como cargada.
- CA-09 (CU-09): un vinculo manual hecho en la bandeja de revision se respeta en todas las sincronizaciones siguientes.

### Permisos, estados y validaciones
- Paso 1: sin usuarios (servicio). Paso 2: rol unico "Operador" de la libreria + cuenta interna del estudio (superusuario, no se documenta al cliente).
- Estados (Paso 2): Lote de cambios (Propuesto → Aprobado → Aplicando → Aplicado / Aplicado con errores / Descartado); Venta ML (Pendiente de descontar → Cargada en Fixed).
- Validaciones: archivo de Fixed con las columnas minimas (codigo, descripcion, stock); cuenta ML conectada y vigente antes de aplicar.

### Banderas tempranas
- Requiere migracion EF: **no** en Paso 1 (sin base) / **si** en Paso 2 (base nueva, migracion inicial).
- Integracion externa: **si** — MercadoLibre API en ambos pasos (confirmada viable). Fixed solo por archivo (sin API de stock, confirmado).
- Maquina de estados: **si** en Paso 2 (lote de cambios).

### Clasificacion de perfil de cliente
- **B2C**, comercio minorista, **chico** en estructura (1 sucursal, plan Basico de Fixed, carga manual) pero con **catalogo online grande** (67.534 publicaciones, probablemente catalogo de distribuidor).
- Sin señal de restriccion de pago ni de capacidad de pago fuera de lo comun (zona comercial consolidada, vende por dos canales). `olvidata-ceo` consultado (2026-09-15): **sin descuento agresivo de entrada**.
- Primer cliente fuera de Argentina: cobro en USD sin conversion a ARS — metodo de cobro a definir por Joaquin.

### Supuestos y dependencias
- S-01 (hipotesis a validar, **bloqueante**): Fixed permite exportar articulos con stock a Excel/CSV desde el panel del plan del cliente. **Confirmado por research: Fixed NO tiene API de stock** (su unica API es de facturacion electronica, plan aparte, "No incluye control de stock").
- S-02 (**confirmado por research**): el catalogo de ML se lee y modifica por API oficial (scan + multiget, PUT de stock/estado); ya no depende del Excel masivo.
- S-03 (hipotesis a validar): una sola cuenta de MercadoLibre.
- S-04 (hipotesis a validar): el stock fisico real es un orden de magnitud menor que las publicaciones (cientos a pocos miles de titulos).
- S-05: el Paso 2 depende de que el cliente autorice una aplicacion del estudio sobre su cuenta ML.
- Dependencia critica: sin export de stock de Fixed no hay Paso 1 ni Paso 2 (bloqueante).

### Preguntas abiertas (con ejemplos, hipotesis a validar)
1. **¿Los libros tienen ISBN cargado en ambos lados?**
   - Opcion A: Fixed usa el ISBN como codigo del articulo y ML lo tiene en el atributo ISBN → cruce casi automatico.
   - Opcion B: Fixed usa un codigo interno (ej. "LIB-00123") y ML no tiene ISBN → cruce por titulo, mas revision.
2. **¿De donde salen las 67.534 publicaciones?**
   - Opcion A: las cargo la libreria una a una a lo largo de los años.
   - Opcion B: vienen de un catalogo de distribuidor/editorial subido en masa (y quiza el distribuidor las actualiza).
3. **¿Una publicacion puede corresponder a varios articulos de Fixed?**
   - Opcion A: una publicacion = un libro (lo mas comun).
   - Opcion B: publicaciones con variantes (tapa dura/blanda, packs, colecciones).
4. **¿Venden libros que no estan en Fixed (a pedido, por encargo)?**
   - Opcion A: no, todo lo que se vende esta en Fixed → sin stock = pausar.
   - Opcion B: si, trabajan "a pedido" con demora → esas publicaciones no deben pausarse aunque el stock sea 0 (necesitan una marca de excepcion).

### Exclusiones confirmadas
- Reemplazar Fixed o escribir en Fixed automaticamente.
- Publicar en ML los libros que no estan publicados (se entrega el listado, la carga no).
- Sincronizar precios, fotos, titulos, descripciones o categorias.
- Integracion con distribuidores/editoriales.
- Mas de una cuenta de ML o otros marketplaces.

## Historial de ajustes
- 2026-09-15: Discovery + Analisis inicial a partir de la conversacion del CRM y las respuestas de calificacion (plan Fixed, 67.534 publicaciones, carga manual); perfil consultado con olvidata-ceo.
- 2026-09-15: Research de integraciones: Fixed sin API de stock (S-01 sigue bloqueante por export manual); ML API confirmada (S-02 cerrado).
