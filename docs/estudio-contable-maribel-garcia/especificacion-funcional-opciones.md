# Olvidata**Soft**

---

**Especificación funcional — Conciliación de Banco y Mercado Pago**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

**Qué tipo de sistema es:** una herramienta de conciliación de movimientos financieros — cruza automáticamente los movimientos de tu extracto bancario contra los de Mercado Pago, para que dejes de hacer ese cruce a mano en Excel. Hay dos formas de construirlo, según qué tan integrado a tu operación diaria lo quieras tener. Te las dejamos comparadas para que elijas.

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

**Qué no tiene:**
- No guarda historial entre usos — cada corrida es independiente, no queda un registro de conciliaciones anteriores para consultar después.
- No tiene usuarios ni login diferenciado por persona.
- No tiene asistencia por IA en los casos dudosos — la revisión de esos casos queda 100% a tu criterio, sin sugerencia automática.
- No hay margen para sumarle funcionalidades más adelante sin rehacerlo — nace pensado para hacer una sola cosa.

**Para quién es:** si lo que necesitás es resolver el cruce puntual cada vez que cerrás el mes, sin que el sistema tenga que "recordar" nada de una vez a la otra.

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
- Historial permanente de todas las conciliaciones (qué se conciliaba, cuándo, quién confirmó cada caso dudoso).
- Cruce automático por monto y fecha, igual que la Opción A.
- Revisión y confirmación de sugerencias, con registro de auditoría.
- Reportes de conciliación por período, no solo por corrida.
- **Asistencia por IA en los casos dudosos** *(a definir con vos — ver nota abajo)*: el sistema sugiere el candidato más probable en los casos que no calzan exacto, en vez de dejarte comparar todo a mano.
- Base pensada para crecer: si más adelante quieren sumar otra funcionalidad, se agrega sobre lo ya construido, sin rehacer el sistema desde cero.

*Sobre la IA: la parte de emparejar por monto y fecha exacto no necesita inteligencia artificial — resuelve sola la mayoría de los casos. La IA se pensó específicamente para el grupo de casos dudosos. Además del desarrollo, esto tendría un costo de uso variable una vez en producción (cada consulta a la IA tiene un costo mínimo) — lo terminamos de definir con vos.*

**Para quién es:** si además de resolver la conciliación puntual querés que quede como parte de tu operación diaria, con trazabilidad de quién hizo qué, y con la puerta abierta para sumar más adelante.

---

## Diferencias clave

| | Opción A — Conversor liviano | Opción B — Sistema profesional |
|---|---|---|
| Usuarios y login | No | Sí, uno por persona |
| Historial entre usos | No — cada corrida es independiente | Sí — historial completo y consultable |
| Auditoría (quién confirmó qué) | No | Sí |
| Asistencia por IA en casos dudosos | No | Sí (a definir alcance) |
| Espacio para crecer a futuro | No — herramienta puntual | Sí — base para sumar funcionalidades |

---

## Lo que necesitamos de tu parte

- Un ejemplo real (o de prueba) del archivo que exportás del banco, para confirmar que tiene el formato que necesitamos.
- Un ejemplo real (o de prueba) del reporte que exportás de Mercado Pago, por el mismo motivo.
- Cuál de las dos opciones te resulta más útil para cómo trabajan hoy — o si tenés dudas, lo charlamos en la demo.

---

Coordinamos una llamada o demo de 15 minutos para repasar las dos opciones juntos y, una vez que definamos el camino, te pasamos los números.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
