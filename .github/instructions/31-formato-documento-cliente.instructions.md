---
description: Formato y estilo obligatorio para TODO documento entregado al cliente (presupuestos y documentos funcionales/resumen de sprint). Basado en el estilo de documentacion de OlvidataSoft (Julio 2026).
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# 31 - Formato de documento para cliente (estilo OlvidataSoft)

Aplica a **todo documento que se entrega al cliente**: presupuesto (`presupuesto-cliente.md`), resumen de sprint del documentador, y cualquier propuesta comercial. NO aplica a las memorias internas de los agentes (`docs/<proyecto>/definiciones/*.md`), que siguen su propio formato tecnico interno.

Este formato define **estilo y estructura de secciones**, no el modelo de precios: para proyectos de desarrollo a medida facturados por horas, el contenido de precios sigue siendo Etapa 1 / Etapa 2 / Tokens IA / Mantenimiento anual segun `27-presupuesto-parametros.instructions.md` — solo cambia el envoltorio visual y el orden de secciones descripto aca. La seccion "Planes disponibles" de este formato (planes anuales por tier) es especifica de ofertas productizadas tipo SaaS; para desarrollo a medida esa seccion se reemplaza por las tablas de Etapa 1/Etapa 2/Total del proyecto ya definidas.

## Encabezado obligatorio

1. Wordmark de la empresa en la primera linea: `# Olvidata**Soft**` (o el nombre de marca vigente).
2. Linea divisoria corta (imagen o regla simple) debajo del wordmark.
3. Titulo del documento/proyecto en negrita, como titulo principal.
4. Subtitulo: `**OlvidataSoft · <Mes> <Año>**`.

## Orden de secciones

1. **`## Sobre el sistema`** (o `## Sobre el proyecto` para el resumen de sprint del documentador): parrafo breve (1-2 lineas) de que resuelve el sistema y para quien, seguido de una lista de bullets que recorre el ciclo/flujo completo en lenguaje llano y en 2da persona (vos/tu equipo) — no una lista tecnica de modulos, sino una narrativa de que hace el sistema en la practica.
2. **`## Como funciona <flujo/feature> — paso a paso`** (una seccion por cada flujo no trivial que amerite explicacion detallada — chatbots, workflows con estados, procesos multi-paso). Estructura:
   - Pasos numerados con frase inicial en negrita (`**1. Nombre del paso.** Descripcion...`).
   - Tabla cuando haya variantes por categoria (ej. tipo de consulta, tipo de usuario).
   - Aclarar explicitamente en italica cuando un detalle es una **hipotesis a validar con el cliente** antes de implementar (no asumir cerrado lo que no fue confirmado).
   - Subseccion `**Casos especiales contemplados:**` cuando aplique (bullets).
3. **`## Rol de usuario`**: tabla `Rol | Accesos`. Nota en italica aclarando que gestiona el proveedor (altas, configuracion) vs. que gestiona el cliente — igual que la regla ya vigente de no exponer el rol de super usuario interno en la documentacion entregada.
4. **Seccion de inversion/pricing** (nombre segun el tipo de oferta):
   - Ofertas productizadas / SaaS por plan: `## Planes disponibles` — tabla `Plan | Capacidad incluida | Plan anual | Equivalente mensual | Unidad economica`, con nota en italica de fine print debajo (ej. descuento por pago anual, que es pago unico y que no).
   - Desarrollo a medida por horas (la mayoria de los proyectos del estudio): mantener las tablas ya definidas en `27-presupuesto-parametros.instructions.md` — `Etapa 1 (MVP)`, `Etapa 2`, `Total del proyecto` (con linea Tokens IA explicita al 10% del total, ver regla vigente), y `Mantenimiento anual` como tabla separada. Se envuelven con el mismo estilo visual (headers, italics de fine print) pero el contenido numerico no cambia por este formato.
5. **`## Que incluye <el plan/el proyecto>`**: bullets de lo incluido.
6. **`## Que no esta incluido`**: bullets de exclusiones (se mantienen las exclusiones fijas del estudio, ver `27-presupuesto-parametros.instructions.md` seccion "Exclusiones fijas").
7. **`## Lo que necesitamos de tu parte`**: bullets en 2da persona de requisitos/dependencias del lado del cliente antes de arrancar (equivalente a "Dependencias del cliente", pero redactado de forma directa y accionable: que debe tener listo el cliente, cuanto puede tardar cada tramite si aplica).
8. **`## Condiciones comerciales`**: bullets — forma de pago, renovacion/entrega, moneda, que pasa si el alcance crece. Mantiene las reglas vigentes (50/50 por etapa para desarrollo a medida; sin clausula de validez de oferta).
9. **Pie de firma obligatorio** al final del documento: `**Olvidata Soft — <email de contacto> — <sitio web>**`.

## Estilo y tono

- Voseo consistente (vos, tu equipo, tu sistema) — nunca "usted" ni "tú" con tilde.
- Tono profesional y calido, sin tecnicismos ni nombres de clases/frameworks/capas.
- Negrita para numeros clave (montos USD, nombres de plan) y para la frase inicial de cada paso numerado.
- Italica para fine print, aclaraciones legales/comerciales y para marcar hipotesis pendientes de validar con el cliente.
- Tablas con columnas numericas alineadas a la derecha.
- Emojis SOLO dentro de copys de ejemplo (mensajes de chatbot, notificaciones) que el sistema efectivamente envia — nunca en titulos ni texto del documento en si.
- Parrafos cortos; preferir bullets a parrafos largos.

## Aplicacion por tipo de documento

- **Presupuesto al cliente** (`presupuesto-cliente.md`): aplica el formato completo, secciones 1-9. La seccion de pricing usa Etapa1/Etapa2/Tokens IA/Mantenimiento para desarrollo a medida, o Planes disponibles para ofertas productizadas.
- **Resumen de sprint del documentador** (salida del agente `documentador`): aplica encabezado, `## Sobre el proyecto` (breve), cambios entregados como bullets, beneficio para el cliente, pendientes si aplica, y pie de firma. No requiere las secciones de pricing/condiciones comerciales (ya se acordaron en el presupuesto) ni "Como funciona paso a paso" salvo que el sprint haya introducido un flujo nuevo que valga la pena explicar al cliente.
- Los pasos de Discovery/Analisis/Diseño/Arquitectura (memorias internas de agentes) **no** usan este formato — son documentos tecnicos internos del estudio.
