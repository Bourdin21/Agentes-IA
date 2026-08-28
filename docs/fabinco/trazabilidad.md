# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-26 - orquestador (Discovery + Analisis + Diseno + Arquitectura + Presupuesto — con consulta estrategica a olvidata-ceo)
- Etapa: Discovery, Analisis, Diseno, Arquitectura, Presupuesto (pasada consolidada).
- Cambio: creado el proyecto `fabinco` (FABINCO - Soluciones en vestimenta laboral, Balvanera CABA) a partir de la calificacion outbound. Discovery limpio (pain point "Stock talle/color", "otro sistema" ya en uso, 3 personas). Hecho research del sitio web (fabinco.com.ar): empresa B2B de 50 años, fabricante/distribuidor de indumentaria laboral y EPP, venta a empresas de 9 sectores por sistema de presupuesto, produccion propia (corte y confeccion), multi-marca, cumplimiento IRAM/ISO. Escaneado `docs/*/definiciones/`: identificado **el match de dominio y codigo mas fuerte del historial completo del estudio — ShowroomGriffin** (indumentaria/calzado con variantes, codigo real en produccion), con reutilizacion real confirmada en 7 de 11 items del WBS (R=81.8% por calculo objetivo).
- Dado el perfil de cliente marcadamente distinto de los leads recientes (dietéticas chicas de ticket bajo), se consulto explicitamente al agente `olvidata-ceo` antes de fijar precio. Recomendacion recibida y aplicada integramente: (1) NO aplicar el descuento de expansion agresiva pese a calificar objetivamente por R (override en sentido inverso a los usados con las dietéticas — aca se pisa un R alto para NO bajar el precio, no un R bajo para subirlo); (2) sondear en la demo, no asumir, dos posibles modulos de alto valor (presupuestos/cotizaciones B2B, trazabilidad de produccion propia) — dejados explicitamente fuera del alcance base; (3) mantenimiento en PREMIUM (USD 500/año) desde el arranque, sin año gratis, porque 3 usuarios ya exceden el tope de PRO y el cliente no necesita el incentivo de precio para cerrar.
- Total del proyecto: **USD 1.155** (sin descuento, precio de lista completo con Tokens IA plegado) — el presupuesto de mayor valor cotizado en el historial reciente del estudio. Mantenimiento: **PREMIUM USD 500/año, sin promocion de año 1.**
- Motivo: pedido explicito del cliente, con input estrategico de `olvidata-ceo` solicitado explicitamente via `/olvidata-ceo`.
- Impacto en capas: ninguno de codigo — documento de propuesta. Sin repo creado todavia.
- Riesgos/supuestos: alta probabilidad de que el alcance real cambie tras la demo si se confirma necesidad de presupuestos/cotizaciones B2B o produccion propia — en ese caso, NO es un ajuste menor sino una reclasificacion de "catalogo indumentaria estandar" a "sistema a medida B2B/industrial", con reestimacion completa. Tambien pendiente confirmar si hace falta facturacion electronica AFIP (no incluida en el alcance base, se asume resuelta en el "otro sistema" actual del cliente hasta que se diga lo contrario). **Gate cliente pendiente**: propuesta lista para revision de Joaquin antes de enviarse al lead real.

## Historial de ajustes
- 2026-08-26: primera version.
