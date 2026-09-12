# Temas para conversar con el cliente al entregar las modificaciones

> Última actualización: 2026-08-13. Acumula los puntos surgidos durante la implementación que **requieren una decisión, un dato o un aviso al cliente**. No es documentación técnica: es la agenda de la reunión de entrega.

---

## 🔴 Requieren acción del cliente (bloquean o generan riesgo)

### 0. ⚠️ Errores de cálculo en el Excel que afectaron resultados ya repartidos

**Este es el punto más delicado de la lista y conviene tratarlo primero.**

Al construir el importador tuvimos que leer el Excel celda por celda, y aparecieron **tres errores de fórmula en la planilla** que hicieron que el Total de Gastos quedara más bajo de lo real en varios meses. Todos verificados directamente sobre las fórmulas del archivo:

| Mes | Qué pasó | Monto no contabilizado |
|---|---|---|
| Diciembre 2024 | La fórmula del total de "Servicios" es `=SUM(C40:C56)`, pero el último concepto del grupo ("Comisiones PedidosYa") está en la fila **57**. Queda fuera de la suma. | $2.142.600 |
| Mayo 2025 | El importe de "Almacén" se cargó como **texto** (`$1.335.352` escrito a mano) en vez de número. Excel ignora los textos al sumar. | $1.335.352 |
| Febrero, Abril y Octubre 2025 | La fórmula del "Total Gastos" no incluye la fila de "Gastos Extras" (suma explícitamente `=C6+C13+C17+C22+C33+C35+C53+C64`, sin esa fila). | $5.275.000 |
| | **Total** | **≈ $8.752.952** |

**Qué implica.** Como el Total de Gastos quedó más bajo de lo real, el **Resultado del Ejercicio quedó más alto** en esos meses, y por lo tanto la **utilidad por punto también** — alrededor de **$87.530 acumulados por punto**. Es decir: en esos meses se repartió algo más de lo que correspondía según los gastos reales.

Además, como el sistema se migró en julio replicando exactamente los totales del Excel, **el sistema hoy arrastra los mismos números**.

**La decisión que hay que tomar** (es contable/comercial, no técnica — la definen ustedes):

- **Opción A — Importar los valores corregidos.** El sistema pasa a mostrar los gastos reales y el resultado correcto. Contra: los meses históricos van a mostrar un resultado menor al que se usó para liquidar en su momento, y las liquidaciones ya pagadas no van a coincidir con él.
- **Opción B — Mantener los números tal como se liquidaron.** El sistema queda consistente con lo que efectivamente se pagó a cada inversor, arrastrando el error de la planilla.
- **Opción C — Corregir e ir compensando.** Se importan los valores reales y la diferencia se ajusta contra repartos futuros.

**No vamos a ejecutar la importación de datos históricos hasta que definan esto**, porque cualquiera de los tres caminos cambia información financiera ya cerrada.

Aparte de esto, hay dos diferencias menores que el sistema va a mostrar antes de confirmar la importación, para que las revisen: en **julio 2026** la fila de VENTAS dice $58.226.922 pero Ventas A + Ventas B suma $61.226.922 (en las hojas de 2024 y 2025 la fila A se calcula sola y siempre cierra; en la de 2026 está escrita a mano), y en **julio 2026** la fórmula de Regalías es distinta a la de los demás meses (`(VENTAS × 0,79) × 3%` en lugar de `VENTAS × 3%`).

### 1. Contraseña del usuario SuperUsuario en producción
Desde el primer despliegue (julio 2026), el usuario SuperUsuario del sistema quedó con **las credenciales por defecto que vienen en el código**. En su momento fue una decisión consciente porque el sitio no estaba publicado.

**Ahora el sistema está publicado en un dominio real y accesible desde internet** (`portaldelinversor.com.ar`), así que esto pasó de ser un pendiente menor a un riesgo concreto de seguridad. Hay que cambiar esa contraseña antes de dar el sistema por entregado.

### 2. Credenciales de la API de Ayres
Las credenciales que nos pasaron (`juani.skare@gmail.com` / `koisucursal9` / ID 9) **son rechazadas por la API** con "acceso no autorizado".

Lo que sí funciona: el servidor responde correctamente (`koi.ayresit.com:8520`), o sea que la conexión y el acceso remoto están bien resueltos — no hace falta ninguna configuración de red adicional. El problema es puntualmente el usuario/clave.

Hay que confirmar con Ayres/MaxiSistemas:
- Si `juani.skare@gmail.com` es el usuario habilitado **para la API** (puede ser distinto del que usan para entrar al POS).
- La contraseña correcta de ese usuario.
- Si el "9" corresponde al campo `idsucursal` o a `cod_cli` (probamos ambos).

Nota: la clave que nos pasaron (`koisucursal9`) coincide exactamente con el nombre de una de las bases de datos del sistema Ayres, así que puede haberse mezclado un dato con otro.

### 3. Diferencia de $100 en agosto 2026
El total de ventas de agosto 2026 no coincide entre las dos fuentes:
- Excel: **$63.131.109**
- Sistema: **$63.131.209**

Son $100 de diferencia, seguramente un error de tipeo al cargar. Necesitamos que confirmen cuál es el valor correcto antes de importar, porque la importación va a sobrescribir el del sistema con el del Excel.

### 4. Definir quién es el "Encargado"
Se creó un perfil nuevo para el encargado del local, que entra al sistema y **solo ve la pantalla de control de asistencia del personal**, sin acceso a información financiera ni de inversores. Falta que nos digan qué persona va a usarlo para darle de alta el usuario.

### 5. Cámaras: qué equipos se van a comprar
Quedó definida la arquitectura para ver las cámaras dentro del sistema (cámaras nuevas conectadas a la red común del local, sin tocar la red aislada del NVR actual). Para poder avanzar falta:
- Marca y modelo de las cámaras a comprar (cualquiera con RTSP/ONVIF estándar sirve).
- Cuántas y en qué puntos del local.
- Confirmar si reemplazan al sistema actual o conviven con él.

---

## 🟡 Avisos importantes (no requieren decisión, pero hay que contarlos)

### 6. El Excel ya no tiene enero a junio de 2026
La hoja "2026" del Excel que nos pasaron **arranca en julio**. Los meses de enero a junio, que en su momento sí se migraron al sistema desde ese archivo, ya no están en la versión actual.

Qué significa en la práctica: **esos importes están correctos en el sistema**, pero agrupados en categorías generales, sin el desglose fino (Mercadería KOI, Barriles, Verdulería, etc.). No los podemos recuperar con detalle desde el archivo actual.

**Si aparece una versión anterior del Excel**, con la hoja 2026 completa, podemos completar esos 5 meses y la historia queda con detalle de punta a punta.

### 7. Julio 2026 no estaba cargado en el sistema
Está en el Excel pero nunca se había cargado. La importación lo va a dar de alta.

### 8. Los nombres de los rubros cambiaron con los años
Comparando las tres hojas del Excel, la estructura de gastos fue cambiando: en 2024 había "Maxirest", "Limpieza de Canillas", "Bebidas c/alcohol" y "Bebidas s/alcohol" por separado; hoy son "Software de Ventas", "Sanitización de Canillas" y "Bebidas" unificado. En total hay 81 conceptos distintos entre todos los años.

Decidimos **cargarlos todos y respetar cómo estaba cada mes en su momento**: los meses de 2024 van a mostrar los nombres de 2024, y los actuales los de hoy. Los conceptos que ya no se usan quedan ocultos en la pantalla de carga mensual para no estorbar, pero siguen visibles en la historia.

### 9. Corrección de meses ya cerrados: qué pasa con las liquidaciones
Se habilitó poder corregir un mes ya cerrado. Cuando se hace:
- Las liquidaciones **pendientes de pago** de ese mes se recalculan automáticamente con el nuevo resultado.
- Las liquidaciones **ya pagadas no se tocan**, para no alterar plata que ya se le entregó al inversor.

Esto significa que, si corrigen un mes donde ya se pagó, ese mes puede quedar con liquidaciones pagadas que no coinciden exactamente con el resultado corregido. **Es intencional**, y el sistema avisa en pantalla cuáles no modificó. Si hiciera falta ajustar una liquidación ya pagada, se hace a mano, una por una.

Además, toda corrección sobre un mes cerrado queda registrada (quién la hizo, cuándo y qué cambió).

### 10. "Recupero en pesos" va a dar casi igual que el de dólares
En Mi Inversión se agregaron los indicadores de dividendos y recupero en pesos, además de los que ya estaban en dólares.

Con los datos actuales **los dos porcentajes van a dar prácticamente el mismo número**, porque todas las liquidaciones tienen su tipo de cambio cargado y terminan siendo la misma cuenta. No es un error del sistema: la métrica separada tiene sentido si en el futuro alguna liquidación queda sin conversión.

### 11. El recupero acumulado cuenta solo lo cobrado
El nuevo gráfico y la columna de recupero acumulado suman **solo las liquidaciones ya pagadas**. Una liquidación pendiente aparece en la tabla pero no mueve el acumulado hasta que se marca como pagada. A confirmar si es el criterio que esperaban.

### 12. Nueva dirección del sistema
El sistema pasa a estar en **`https://portaldelinversor.com.ar/koi/`**. La dirección anterior sigue funcionando y redirige sola, así que nadie pierde el acceso, pero conviene que actualicen el enlace que tengan guardado y el que les pasen a los inversores.

La estructura quedó preparada para que, si en el futuro suman otro local, sea `portaldelinversor.com.ar/{nombre-del-local}/` sin rehacer nada.

---

## ✅ Resuelto durante esta ronda (para mencionar como valor entregado)

- **Corrección en los puntos de inversión**: uno de los inversores figuraba con más puntos de los que tiene asignados, por un error de cálculo del sistema (contaba dos veces un cambio histórico de puntos). El total ahora muestra correctamente 95 puntos asignados. **Ningún dato histórico fue modificado** y ninguna liquidación estaba mal calculada.
- **Importes cortados**: los montos ya no se parten en dos líneas en ninguna pantalla.
- **Orden de los meses**: tanto en Historial de Resultados como en Reparto General los períodos ahora se ordenan cronológicamente (antes se ordenaban alfabéticamente por el nombre del mes).
- **Fichador de empleados**: pantalla nueva de control de asistencia integrada con QuickPass.

## Integración con Ayres POS (E2-01) — Septiembre 2026

**1. Pedido de seguridad a Ayres / MaxiSistemas (ya NO es bloqueante).** La conexión quedó resuelta habilitando la salida al puerto 8520 desde el panel del hosting, sin depender de nadie. Lo que queda es una cuestión de seguridad: la API se sirve por **`http://` sin certificado**, así que el usuario y la contraseña viajan **en texto plano** por internet en cada llamada. Pedido concreto: **exponer la API en el puerto 443 con certificado TLS**. No frena el proyecto, pero conviene planteárselo.

**2. Los datos de ventas cargados a mano tienen errores (verificado).** Comparando agosto 2026 contra lo que registró el sistema de ventas del local:

| | Cargado a mano | Real (Ayres) |
|---|---|---|
| Ventas totales | 63.131.209 | **63.131.109** |
| Salón | 54.837.560 | 52.404.760 |
| Mostrador | 100 | 2.432.500 |
| Cantidad de ventas | 2.000 | **1.018** |

El **total** está bien (diferencia de $100 sobre $63 millones). Lo que está mal es el detalle: Mostrador se cargó dentro de Salón, y la cantidad de ventas está al doble — lo que hace que **el ticket promedio que se muestra hoy sea menos de la mitad del real** ($31.566 contra $62.015).

Aclaración a favor de quien carga: los **comensales estaban bien** (1.678). Se verificó que ya venía excluyendo las ventas anuladas, que el sistema de Ayres informa aparte.

**3. Decisiones pendientes del cliente:**
- ¿Se corrigen los períodos históricos con los datos reales de Ayres, o se dejan como están? Los **totales no cambian**, así que **no afecta ningún reparto ya liquidado** — solo mejora los indicadores por canal y el ticket promedio.
- ¿Confirma que en Ayres "ME" es Salón, "PE" es Pedidos y "MO" es Mostrador?

---

## ⚠️ Pendientes antes de cerrar la Entrega 1 (2026-09-10)

El detalle completo está en **`pendientes-entrega-1.md`**. Los dos que **bloquean** y necesitan una reunión con el cliente:

1. **Agosto 2026 no cierra** — $99,9 M de gastos contra $63,1 M de ventas, porque el mes tiene cargados los dos catálogos a la vez. Hay que definir con Juani, para los 4 meses abiertos (2026-01, 07, 08 y 09), qué filas quedan. Sin cierre no hay reparto a inversores.
2. **Seis subgrupos históricos sin destino** — entre ellos **"Otros gastos" ($212,7 M)** y **CMV ($442,2 M**, que el catálogo nuevo abre en cuatro). Los totales históricos son correctos; lo que falta es el mapeo, y no corresponde que lo decidamos nosotros.

Y uno para validar: **"Mercadería KOI" de agosto se corrigió de $111.396.734 a $11.139.654** (error de tipeo de un dígito, con backup). Conviene que Juani confirme el número.

