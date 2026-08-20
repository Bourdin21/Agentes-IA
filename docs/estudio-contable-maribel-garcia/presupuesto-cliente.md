# Olvidata**Soft**

---

**Propuesta de desarrollo — Conciliación de Banco y Mercado Pago**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

**Qué tipo de sistema es:** una herramienta de conciliación de movimientos financieros — cruza automáticamente los movimientos de tu extracto bancario contra los de Mercado Pago, para que dejes de hacer ese cruce a mano en Excel. Hay dos formas de construirlo, según qué tan integrado a tu operación diaria lo quieras tener. Te las dejamos comparadas, con el costo de cada una, para que elijas.

---

## Opción A — Conversor liviano

Una herramienta simple y directa: subís los dos archivos, el sistema los cruza en el momento, y te muestra el resultado. Sin necesidad de iniciar sesión ni de configuración previa.

**Cómo se usa:**
1. Subís el extracto del banco y el reporte de Mercado Pago.
2. El sistema los cruza al instante por monto y fecha.
3. Ves en pantalla qué se concilió, qué quedó dudoso y qué no encontró par.
4. Descargás el resultado en Excel.

**Qué incluye:**
- Cruce automático por monto y fecha exacta.
- Vista de resultados de esa corrida (conciliado / dudoso / sin conciliar).
- Descarga del reporte en Excel.

**Qué no tiene:** historial entre usos, usuarios/login diferenciado, asistencia por IA en los casos dudosos, ni margen para sumarle funcionalidades más adelante sin rehacerlo. Nace pensado para hacer una sola cosa.

**Para quién es:** si necesitás resolver el cruce puntual cada vez que cerrás el mes, sin que el sistema tenga que "recordar" nada de una vez a la otra.

| Área funcional | USD |
|---|---:|
| Importación de extracto bancario | USD 63 |
| Importación de extracto Mercado Pago | USD 42 |
| Motor de conciliación automática | USD 84 |
| Vista de resultados | USD 42 |
| Descarga de reporte Excel | USD 31 |
| Puesta en marcha | USD 63 |
| **Total Opción A** | **USD 325** |

| Mantenimiento anual | USD/año |
|---|---:|
| STARTER | USD 300 |

*Incluye hosting, actualizaciones de seguridad y soporte por email.*

---

## Opción B — Sistema de gestión profesional

Un sistema con login propio para cada persona del equipo, que guarda el historial completo de conciliaciones y queda como parte permanente de la operación del estudio.

**Cómo se usa:**
1. Cada persona entra con su propio usuario.
2. Importás los extractos — cada importación queda registrada con fecha y quién la subió.
3. El sistema concilia automáticamente lo que coincide en monto y fecha.
4. Los casos dudosos aparecen para que los confirmes o rechaces — queda guardado quién lo hizo y cuándo.
5. Consultás en cualquier momento el historial de conciliaciones anteriores, no solo la última corrida.
6. Exportás reportes por período para el cierre contable.

**Qué incluye:**
- Usuarios y accesos propios por persona del equipo.
- Historial permanente de todas las conciliaciones, con registro de quién confirmó cada caso dudoso.
- Cruce automático por monto y fecha, igual que la Opción A.
- Reportes de conciliación por período.
- Base pensada para crecer: si más adelante quieren sumar otra funcionalidad, se agrega sobre lo ya construido.
- **Etapa 2 — Asistencia por IA en casos dudosos:** el sistema sugiere el candidato más probable en los casos que no calzan exacto, en vez de dejarte comparar todo a mano.

*Sobre la IA: la parte de emparejar por monto y fecha exacto no necesita inteligencia artificial — resuelve sola la mayoría de los casos. La IA se pensó específicamente para el grupo de casos dudosos. Esto suma, además del desarrollo, un costo de uso variable una vez en producción (cada consulta a la IA tiene un costo mínimo) — con el volumen esperado para un equipo de 1-2 personas debería ser marginal, pero lo conversamos en la demo para definir si lo cubre el mantenimiento o una cuenta propia tuya.*

**Para quién es:** si además de resolver la conciliación puntual querés que quede como parte de tu operación diaria, con trazabilidad de quién hizo qué, y con la puerta abierta para sumar más adelante.

| Área funcional (Etapa 1) | USD |
|---|---:|
| Importación de extractos (Banco + Mercado Pago) | USD 147 |
| Motor de conciliación automática | USD 126 |
| Revisión y confirmación de sugerencias | USD 105 |
| Reportes de conciliación | USD 42 |
| Usuarios y accesos | USD 32 |
| Puesta en marcha | USD 42 |
| **Subtotal Etapa 1** | **USD 494** |

| Área funcional (Etapa 2) | USD |
|---|---:|
| Asistencia por IA en casos ambiguos | USD 84 |
| **Subtotal Etapa 2** | **USD 84** |

| Concepto | USD |
|---|---:|
| **Total Opción B** | **USD 578** |

| Mantenimiento anual | USD/año |
|---|---:|
| PRO (hasta 2 usuarios) | USD 400 |

*Incluye hosting, actualizaciones de seguridad, soporte por WhatsApp y 1 ronda de ajuste al año. Si terminan siendo 1 sola persona usando el sistema, el plan STARTER (USD 300/año) también alcanza.*

---

## Diferencias clave

| | Opción A | Opción B |
|---|---|---|
| Usuarios y login | No | Sí, uno por persona |
| Historial entre usos | No | Sí, completo y consultable |
| Auditoría (quién confirmó qué) | No | Sí |
| Asistencia por IA en casos dudosos | No | Sí (Etapa 2, a confirmar alcance) |
| Espacio para crecer a futuro | No | Sí |
| **Total desarrollo** | **USD 325** | **USD 578** |
| **Mantenimiento anual** | **USD 300** | **USD 400** |

---

## Qué incluye el proyecto (ambas opciones)

- Desarrollo funcional del alcance detallado arriba.
- Pruebas funcionales internas y entrega operativa.
- Ajustes menores de puesta en marcha dentro del alcance acordado.

## Qué no está incluido (ambas opciones)

- Asientos contables, libro IVA o presentaciones ante AFIP/ARCA — el sistema concilia movimientos, no reemplaza tu contabilidad.
- Migración de conciliaciones históricas ya hechas en Excel.
- Facturación electrónica.
- Aplicación móvil (se accede desde el navegador, funciona bien en celular).
- Cambios de alcance posteriores al inicio (se cotizan aparte).

---

## Lo que necesitamos de tu parte

- Un ejemplo real (o de prueba) del archivo que exportás del banco, para confirmar que tiene el formato que necesitamos.
- Un ejemplo real (o de prueba) del reporte que exportás de Mercado Pago, por el mismo motivo.
- Cuál de las dos opciones te resulta más útil — o si tenés dudas, lo charlamos en la demo.

---

## Condiciones comerciales

- Forma de pago: 50% al inicio y 50% a la entrega.
- Moneda: USD.
- Cambio de alcance disponible en cualquier momento si el proyecto crece (se cotiza aparte).

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
