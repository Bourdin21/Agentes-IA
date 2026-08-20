# Olvidata**Soft**

---

**Propuesta funcional — Conciliación de Banco y Mercado Pago**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

**Qué tipo de sistema es:** una herramienta de conciliación de movimientos financieros — no un sistema contable ni un reemplazo de tu Excel para todo, sino algo puntual: cruza automáticamente los movimientos de tu extracto bancario contra los de Mercado Pago, para que dejes de hacer ese cruce a mano.

- Subís el extracto del banco y el reporte de Mercado Pago, y el sistema arma las dos listas de movimientos.
- Lo que coincide en monto y fecha se concilia solo, sin que tengas que tocar nada.
- Lo que no calza exacto pero tiene un candidato razonable te lo muestra aparte, para que lo confirmes o lo rechaces con un clic.
- Lo que no encuentra ningún par queda visible en su propia lista, para que lo revises con calma.
- Al cierre, exportás un reporte con todo separado: conciliado, confirmado a mano y sin conciliar.

---

## Cómo funciona la conciliación — paso a paso

**1. Importar los extractos.** Subís el archivo del banco y el de Mercado Pago (los mismos que ya exportás hoy).

**2. Conciliación automática.** El sistema empareja solo los movimientos que coinciden en monto exacto y fecha cercana — la mayoría de los casos se resuelven acá, sin que intervengas.

**3. Revisión de casos dudosos.** Lo que no calza exacto (una diferencia de días, un monto parecido) te lo muestra como sugerencia con el candidato más probable, para que confirmes o rechaces.

**4. Sin conciliar.** Lo que no tiene ningún candidato queda en su propia lista, lista para investigar aparte.

**5. Reporte final.** Exportás todo a Excel para el cierre.

*Sobre el uso de IA: la parte de emparejar por monto y fecha exacto no necesita inteligencia artificial — es un cruce directo y así lo hace la mayoría de los casos. La IA la pensamos para el grupo de casos dudosos, para que te sugiera el candidato más probable en vez de tener que compararlos vos a mano uno por uno. Es una hipótesis de cómo conviene resolverlo — lo terminamos de definir con vos.*

---

## Rol de usuario

| Rol | Accesos |
|---|---|
| Contador/a | Importa extractos, revisa y confirma/rechaza sugerencias, exporta reportes. |

*Pensado para un equipo chico (1-2 personas) — todos los usuarios tendrían el mismo nivel de acceso, sin roles diferenciados. El alta de usuarios y la configuración inicial las gestionamos nosotros como parte del servicio.*

---

## Funcionalidades principales

- **Importación de extractos** — carga del extracto bancario y del reporte de Mercado Pago.
- **Motor de conciliación automática** — cruce por monto y fecha, sin intervención manual en los casos claros.
- **Revisión y confirmación de sugerencias** — para los casos que no calzan exacto.
- **Reportes de conciliación** — exportación a Excel con todo separado por categoría.
- **Usuarios y accesos** — login para cada persona del equipo.
- **Puesta en marcha** — dominio y hosting del sistema, listo para usar.

## Funcionalidad adicional (a definir)

- **Asistencia por IA en casos ambiguos** — sugerencia automática del candidato más probable cuando el cruce exacto no alcanza. *Esto suma, además del desarrollo, un costo de uso variable una vez en producción (cada consulta a la IA tiene un costo mínimo) — lo conversamos en la demo antes de confirmarlo.*

---

## Qué incluye el proyecto

- Desarrollo funcional del alcance detallado arriba.
- Pruebas funcionales internas y entrega operativa.
- Ajustes menores de puesta en marcha dentro del alcance acordado.

## Qué no está incluido

- Asientos contables, libro IVA o presentaciones ante AFIP/ARCA — el sistema concilia movimientos, no reemplaza tu contabilidad.
- Migración de conciliaciones históricas ya hechas en Excel.
- Facturación electrónica.
- Aplicación móvil (se accede desde el navegador, funciona bien en celular).

---

## Lo que necesitamos de tu parte

- Un ejemplo real (o de prueba) del archivo que exportás del banco, para confirmar que tiene el formato que necesitamos.
- Un ejemplo real (o de prueba) del reporte que exportás de Mercado Pago, por el mismo motivo.
- Confirmar si van a ser 1 o 2 las personas que usan el sistema.

---

Con esto ya tenés el detalle de qué haría el sistema. Coordinamos una llamada o demo de 15 minutos para repasarlo juntos y te paso los números.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
