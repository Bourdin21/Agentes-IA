# Plan de implementación — KOI, cierre de pendientes

> Fecha: 2026-08-13. Consolida todo lo conversado y definido durante el día, ordenado por dependencia y riesgo.
> Fuente de las definiciones: `definiciones/1-analista-funcional.md` §12–§14, `2-disenador-funcional.md` §11–§13, `3-arquitecto-mvc.md` §9–§11, `4-presupuestador.md` §17–§19.

---

## Hallazgos de hoy que cambian el planteo

**1. El dominio `/koi/` ya funciona — no hace falta tocar código.** Verificado contra producción con el SSL ya activo: `https://portaldelinversor.com.ar/koi/` sirve la app con **todos los links correctamente prefijados** (`/koi/lib/...`, `/koi/icons/...`). ASP.NET Core resuelve el `PathBase` solo, como aplicación anidada de IIS — el `UsePathBase` que se había dejado como posible ajuste **no es necesario**.
El problema real es otro: el sitio **raíz** (`https://portaldelinversor.com.ar/`) también sirve la misma app, porque el dominio quedó bindeado directo a la carpeta `\KoiDumplings` además del directorio virtual. Hay dos IIS Applications sirviendo los mismos binarios.

**2. Los Excel del cliente NO tienen el formato de la plantilla del sistema.** Ya están disponibles en `KoiDumplings/docs/`:
- `Estado de Resultados KOI (Inversores).xlsx` → hojas `2026`, `2025`, `2024` (matriz rubros × meses, igual al PDF).
- `Reparto de Utilidades Inversores.xlsx` → hojas `Puntos`, `GENERAL` + una por cada uno de los 15 inversores.

En la migración de julio esos archivos fueron **transformados a mano** a la plantilla del importador. Eso significa que el ítem de "importación recurrente" tiene un fork de alcance que antes no estaba visible (ver Fase 5).

---

## Fase 0 — Infraestructura del dominio (acción de panel, sin código)

**Objetivo:** que la app se sirva **solo** desde `/koi/`, dejando la raíz libre para el esquema multi-local futuro (`/xxx/`).

| Paso | Quién | Detalle |
|---|---|---|
| 0.1 | Cliente (panel) | Cambiar la ruta física del **sitio raíz** de `portaldelinversor.com.ar` a una carpeta distinta de `\KoiDumplings` (ej. `\portal-root`), dejando el directorio virtual `koi` → `\KoiDumplings` como está (ya creado y funcionando). |
| 0.2 | Olvidata | Subir a esa carpeta raíz un `index.html` mínimo que redirija a `/koi/` (o una futura portada del portal si se suman locales). |
| 0.3 | Verificación | `https://portaldelinversor.com.ar/` → redirige a `/koi/`; `https://portaldelinversor.com.ar/koi/` → la app. |

**Riesgo:** bajo. Si el panel no permite cambiar la ruta física del sitio raíz, la alternativa es dejar la raíz como está (duplicada) hasta que aparezca un segundo local — no rompe nada, solo queda la app accesible por dos URLs.

---

## Fase 1 — Correcciones rápidas (bajo riesgo, entregables en el día)

| # | Ítem | USD |
|---|---|---:|
| 1.1 | Remitente de correos → "KOI Dumplings" (config, sin código) | 3 |
| 1.2 | Reparto General: ordenar por año y mes, no por nombre de mes | 5 |

Sin dependencias, sin migración. Se pueden commitear y deployar juntos, antes que el resto.

---

## Fase 2 — Mi Inversión: evolución del recupero (USD 34)

- Columna "Recupero acum." por fila del historial (acumulado cronológico, cada mes con el TC de su propio mes cerrado).
- Gráfico de línea con la progresión del recupero acumulado + línea de meta al 100 %.
- **No** se duplica la columna "Renta": ya es exactamente el recupero del mes.

Sin dependencias con las otras fases. Riesgo bajo.

---

## Fase 3 — Catálogo real de rubros + remapeo histórico (USD 67) — RIESGO ALTO

**Esta fase va antes que la 4 y la 5**, porque las dos dependen de que el catálogo esté en su forma definitiva.

Orden de ejecución obligatorio:
1. **Backup de la base de producción.**
2. Snapshot de verificación: total de gastos por período.
3. Alta de los 8 rubros / ~40 subgrupos del PDF de agosto.
4. Remapeo de los 373 gastos históricos (mapeo completo en `3-arquitecto-mvc.md` §11.5).
5. Baja lógica de los subgrupos genéricos ya remapeados.
6. **Verificación**: los totales por período deben quedar idénticos al snapshot del paso 2. Si cambió alguno → revertir con el backup.

**Mejora respecto de lo planteado ayer:** ahora que están los Excel originales, el mapeo se puede **validar contra la fuente** antes de aplicarlo (comparar cómo agrupaba el Excel cada gasto histórico), en vez de decidirlo solo por nombre de subgrupo.

**Bloqueantes antes de ejecutar:**
- Revisión del cliente sobre las filas marcadas ⚠️ del mapeo (el "CMV" genérico que ahora se abre en 4, Expensas, Otros gastos, Honorarios).
- Ventana acordada para el backup + migración.

---

## Fase 4 — Editar meses cerrados (USD 59) — RIESGO ALTO

- Se quitan los guards de período cerrado en `GuardarVentas` y `GuardarConceptoGastoAsync` (NO el de `ConfirmarCierre`).
- Al editar un período cerrado: se recalculan las liquidaciones **Pendientes**; las **Pagadas** quedan intactas y el sistema informa cuáles no tocó.
- Auditoría obligatoria de cada edición sobre un período cerrado (usuario, fecha, valor anterior → nuevo).
- Banner permanente + confirmación SweetAlert2 en la pantalla cuando el período está cerrado.

**Depende de Fase 3**: si se corrige un mes cerrado con el catálogo viejo y después se remapea, se hace el trabajo dos veces.

---

## Fase 5 — Importación de Excel recurrente — **RE-ESTIMAR, hay un fork**

El ítem estaba presupuestado en USD 42 asumiendo "agregar un flag de actualizar al importador que ya existe". Con los Excel a la vista, aparecen dos caminos distintos:

| Opción | Qué implica | Esfuerzo | USD |
|---|---|---|---:|
| **A — Plantilla del sistema** | Se agrega el flag "actualizar los que ya existan" al importador actual. El cliente debe volcar sus datos a la plantilla que el sistema genera, cada vez. | M 2.5 h | **42** |
| **B — Parsear el Excel nativo del cliente** | El sistema lee directamente `Estado de Resultados KOI (Inversores).xlsx` (hojas por año, matriz rubros × meses) y `Reparto de Utilidades Inversores.xlsx` (Puntos + GENERAL + 15 hojas). El cliente sube su propio archivo, sin transformar nada. | M 5.0 h | **84** |

**Recomendación: opción B.** El pedido fue "no van a dejar de usar el Excel y quieren poder importarlo" — con la opción A siguen teniendo que hacer a mano la transformación que en julio hizo el equipo, así que en la práctica no se usaría. Además, **después de la Fase 3 el parser se simplifica mucho**: los nombres de las filas del Excel van a coincidir 1:1 con los subgrupos del catálogo, que es justo lo que hoy no pasa.

**Depende de Fase 3.**

---

## Fase 6 — API de Ayres (E2-01): implementar hasta el límite de las credenciales

Research ya completo (`1-analista-funcional.md` §10.1.1): los 9 KPIs salen todos de `GET /ventas`.

**Se puede construir y probar sin credenciales:**
- `IAyresService` + cliente HTTP tipado, con **login y renovación automática de token** (el token expira ~1 h, a diferencia de QuickPass).
- DTOs mapeados de `/ventas` (`facturaMontoTotal`, `cantidadConsumidores`, `items[]`, `sectorTipo`, `fechaContable`).
- **Chunking de 10 días**: partir cualquier rango mensual en 3-4 llamadas encadenadas y agregar del lado nuestro (límite duro de la API).
- Cálculo de los 9 KPIs + desglose por canal (`sectorTipo`).
- Botón "Importar desde Ayres" en la pantalla de Estado de Resultados, con preview antes de confirmar.
- Manejo de errores y de la config (`appsettings`).
- Pruebas con respuestas mockeadas del formato documentado.

**Queda bloqueado hasta que lleguen las credenciales:**
- Smoke test real contra la API viva.
- Ajuste del mapeo si la respuesta real difiere de la documentación (mismo gatillo que se aplicó en QuickPass, donde el contrato real trajo sorpresas).
- **Acceso de red**: la API corre en el servidor local del restaurante. Se resuelve con el mismo gateway + Cloudflare Tunnel ya diseñado para las cámaras — un solo túnel sirve para ambos.

**Pendiente del cliente:** email, password e `idsucursal` de la API de Ayres.

*(Sin estimar hasta definir si entra en esta tanda — es un módulo aparte, no parte del sprint de USD 263.)*

---

## Fase 7 — Definiciones pendientes (no estimadas, esperando respuesta)

| Tema | Estado |
|---|---|
| Leyenda del TC en Estado de Resultados | Verificado que el TC **no bloquea** la carga de gastos (nunca lo hizo). Queda ofrecida una leyenda aclaratoria, sin respuesta. |
| Carga de gastos on-demand con autosave (en vez del modal) | Evaluado: viable, ~1–1.5 h, el backend ya guarda de a un concepto. Sin confirmación. |
| Completar históricos con datos de Ayres | Propuesta: usar Ayres para llenar el desglose Salón/Delivery y los cubiertos de los períodos migrados (hoy en 0 / sin dato), **sin pisar** los importes ya conciliados. Sin respuesta. |
| Cámaras E2-03 | Arquitectura definida (cámaras nuevas en la red normal + MediaMTX + Cloudflare Tunnel). Falta: marca/modelo, cantidad y ubicación de las cámaras a comprar. |

---

## Resumen económico

| Fase | USD |
|---|---:|
| 1 — Correcciones rápidas | 8 |
| 2 — Mi Inversión: evolución del recupero | 34 |
| 3 — Catálogo real + remapeo | 67 |
| 4 — Editar meses cerrados | 59 |
| 5 — Importación Excel (opción B recomendada) | 84 |
| **Subtotal desarrollo** | **252** |
| Tokens IA (25 %) | 63 |
| **Total** | **315** |

*(Con la opción A de la Fase 5 el total sería USD 263, tal como se presupuestó ayer.)*

Fase 0 no tiene costo de desarrollo (acción de panel + un archivo estático). Fase 6 (Ayres) se cotiza aparte cuando se defina si entra ahora.

---

## Orden de ejecución recomendado

```
Fase 0 (panel, en paralelo)
    │
Fase 1 ──► deploy inmediato (bajo riesgo)
    │
Fase 2 ──► deploy
    │
Fase 3 ──► BACKUP + migración + verificación  ◄── requiere OK del mapeo
    │
    ├──► Fase 4 (editar cerrados)
    └──► Fase 5 (importación Excel)
              │
         Fase 6 (Ayres) ◄── requiere credenciales
```
