# Guión — Reunión de relevamiento para configurar el portal · Contadores BMA

**Fecha del documento:** 2026-09-23 · **Etapa:** entrega progresiva, pasaje de Etapa 1 a **Etapa 2 "Tu forma de trabajar"**
**Contexto:** BMA ya está en producción en `agentes.olvidata.com.ar`, plan Rubro estándar contable (presupuesto 2026-09-22,
pendiente de aprobación de los opcionales). Esta reunión **no vende**: configura.
**Complementa:** [cuestionario-configuracion-portal.md](cuestionario-configuracion-portal.md) — si Gastón lo devolvió
completo, los bloques 1 a 3 se recorren leyendo y confirmando, y la reunión baja a 60 minutos.

## Supuestos (corregir antes de mandarla)

- Participan **Gastón** (usuario piloto, usa Bejerman y SOS) y **un Director** del estudio. Sin un Director en la sala no
  se pueden dejar aplicadas las reglas de la empresa.
- **90 minutos, con el portal proyectado.** Se configura en vivo, no se toma nota para configurar después: lo que no queda
  cargado en la reunión no queda cargado nunca.
- Modalidad remota con pantalla compartida, o presencial en el estudio. Si es remota, que Gastón tenga a mano los archivos
  reales de un cliente (un mayor de SOS y un extracto del mes).

## Objetivo de la reunión, en una línea

Que al terminar el estudio tenga **cartera cargada, reglas de la empresa aplicadas, un instructivo escrito y una tarea real
corriendo sobre un cliente real**, y una fecha de revisión a dos semanas.

## Antes de la reunión (Joaquín)

- [ ] Confirmar que el tenant de producción tiene el rubro contable publicado y los 10 agentes visibles.
- [ ] Crear las cuentas de los que van a entrar (Director/Empleado, área) para no gastar tiempo de reunión en altas.
- [ ] Revisar `Consumo`: límite mensual de la organización cargado antes de que alguien pida la primera tarea.
- [ ] Tener abierta la pestaña **Reglas → Sugerencias de Olvidata** (las reglas del rubro contable listas para activar en un clic).
- [ ] Tener a mano un cliente de prueba del propio estudio, por si alguien se suma tarde y no conviene mostrar datos reales.
- [ ] Repasar qué **no** hace el producto (§7 del manual): no presenta ni paga ante ARCA, no tiene clave fiscal, no entra a
      Onvio. Si sale el tema en la reunión, se contesta de una y se sigue.

---

## Agenda

### 0 · Encuadre — 5 min

Qué es esta reunión y qué se lleva el estudio al final. Tres frases:

> El portal ya funciona y ya sabe del oficio contable. Lo que no sabe todavía es **cómo trabaja BMA**: sus clientes,
> sus criterios y sus pasos. Eso es lo que salimos a cargar hoy. Nada de lo que carguemos sale del estudio ni lo ve
> otra organización.

### 1 · Cartera de clientes — 15 min

Se carga en vivo. Alcanza con **5 a 10 clientes del piloto**, no la cartera entera.

- ¿Con qué clientes querés empezar? ¿Por qué esos — los más pesados, los más prolijos, o los que más consultan?
- Razón social, CUIT, condición (RI / Monotributo / Exento / Sociedad), actividad, responsable, si tiene empleados.
- ¿Cómo los identifican internamente: por CUIT, por número de Bejerman, por apodo? *(Eso define con qué se busca después.)*

**Queda configurado:** `Cartera de clientes` → *Nuevo cliente*, uno por uno. El CUIT valida dígito verificador.

### 2 · Documentos de un cliente — 10 min

El bloque más importante de la reunión, porque es donde aparecen las sorpresas.

- Subir en vivo **el material real de un cliente del piloto**: un mayor exportado y un extracto bancario del mismo mes.
- Mirar juntos el **estado de lectura** de cada archivo y explicarlo ahí mismo:
  *El agente lo puede leer · lee solo una parte · no puede leerlo (escaneado) · no se pudo leer.*

> **El error más caro del producto:** subir un extracto escaneado y suponer que el agente lo leyó. Mostrarlo en vivo vale
> más que explicarlo diez veces.

- ¿De dónde sale cada archivo hoy — se exporta de Bejerman, de SOS, se baja del home banking? ¿En qué formato?
- ¿Alguno de los que usan llega escaneado o como foto? *(Si sí, ese circuito hay que cambiarlo antes, no después.)*

**Nota técnica para Joaquín, no para la sala:** el `.xls` de SOS Contador **no es un Excel, es HTML con una tabla adentro** —
el portal ya lo reconoce por contenido y lo lee. Los PDF del Credicoop son de texto y entran, pero el encabezado extraído
puede atribuirle al titular un CUIT que en realidad es del banco: **no citar un CUIT ni un importe de esos PDF sin mirarlo**.

### 3 · Los criterios del estudio — 20 min

El bloque que convierte la charla en configuración. **Se hace con "Configurar conversando"** (solo Director): se le cuenta
cómo trabaja el estudio y propone reglas; nada se aplica hasta apretar el botón de cada tarjeta.

Preguntas que abren, en este orden (de lo que más cambia el resultado a lo que menos):

1. **¿Qué no se hace nunca en este estudio?** ("no se presenta nada sin que lo mire el responsable", "ningún número sin respaldo").
2. **¿Qué necesita sí o sí que lo revise una persona antes de salir?**
3. **¿Cómo se le habla al cliente?** Tuteo o usted, con jerga o sin jerga, firma del estudio, por mail o por WhatsApp.
4. **¿Qué se hace distinto por área?** Impuestos, Sueldos, Balances.
5. **¿Hay clientes con una particularidad que todos en el estudio ya saben de memoria?** Eso es una regla de cliente.

**Queda configurado:** las dos primeras en modo **Siempre**; el resto en *Salvo que se indique otra cosa*. Activar además las
**Sugerencias de Olvidata** del rubro contable que el estudio reconozca como propias.

### 4 · Áreas y quién es quién — 10 min

- ¿Qué áreas existen de verdad — Impuestos, Monotributo, Sueldos, Balances, Atención? ¿O trabajan todos de todo?
- ¿Quién entra como Director y quién como Empleado? *(Director configura y aprueba; Empleado usa.)*
- ¿Quién responde por el resultado de una liquidación cuando la arma otro?

**Queda configurado:** áreas, miembros y el área de cada uno. Si el estudio es chico y no hay áreas reales, **no inventarlas**.

### 5 · Un instructivo, escrito en la reunión — 15 min

Uno solo, el que más se repite. Candidato natural: **la conciliación bancaria mensual** (es lo que Gastón ya venía
sistematizando y el opcional cotizado).

- Contámelo como si se lo explicaras a alguien que entra mañana al estudio: paso 1, paso 2…
- ¿Qué decide que dos movimientos son el mismo? ¿Tolerancia de días, de importe?
- ¿Qué hacés con lo que no concilia?
- ¿Cuánto tarda hoy y cuántas veces por mes lo hacés? *(Es el número que después mide si el portal sirvió.)*

**Queda configurado:** `Instructivos` → de la empresa. Y acto seguido **se pide la tarea real** sobre el cliente del bloque 2,
con ese instructivo y esas reglas. Mirar juntos *«Esto es lo que el agente va a tener en cuenta»* antes de enviar, y
`Ver pasos` cuando termine.

### 6 · Lo que debería correr solo — 8 min

- ¿Qué cosa se les pasa siempre y no debería depender de que alguien se acuerde?
- Candidatos del rubro: vencimientos de la semana (lunes 8:00), control de monotributistas (día 5), avisos de
  recategorización.
- ¿Quién recibe el resultado?

**Queda configurado:** `Programaciones` → una sola, la que más duela. Sin autonomía.

### 7 · Límites y qué necesita aprobación — 5 min

- Límite de gasto mensual por persona (el Director lo fija; siempre ≤ el de la empresa).
- ¿Qué **no** puede hacer un agente sin que un Director lo apruebe antes?
- Aclarar: todo lo que salga hacia afuera ya requiere aprobación por diseño, y la aprobación vence a las 72 horas.

*Conexiones a sistemas externos queda para Etapa 3: se menciona, no se configura hoy.*

### 8 · Cierre — 7 min

- **Piloto:** quiénes prueban las próximas dos semanas y con qué clientes.
- **Revisión de 30 minutos** agendada en el momento, con día y hora.
- Repasar en voz alta lo que quedó cargado (es corto y se siente bien).
- Qué queda pendiente del lado del estudio: la lista completa de clientes, los manuales internos, los modelos de mail.

---

## Checklist de cierre — la reunión sirvió si al final hay

- [ ] Entre 5 y 10 clientes en la cartera.
- [ ] Al menos un cliente con documentos subidos y **estado de lectura verificado**.
- [ ] 3 o más reglas de la empresa aplicadas, con al menos dos en modo *Siempre*.
- [ ] Miembros dados de alta con su rol y su área.
- [ ] 1 instructivo escrito por el estudio, no por Olvidata.
- [ ] 1 tarea real corrida de punta a punta, mirada entre todos.
- [ ] 1 programación activa.
- [ ] Límites de gasto cargados.
- [ ] Fecha y hora de la revisión a dos semanas.

## Lo que hay que evitar decir

- Que el portal "se conecta con Bejerman/Onvio". **No se conecta**: los Onvio Full Terms lo prohíben sin autorización de
  Thomson Reuters. El circuito es por archivos exportados.
- Que "presenta" o "paga". Prepara; presenta el estudio.
- Prometer los agentes a medida (conciliación, Impuestos BMA, balances) como si estuvieran incluidos: son los **opcionales
  del presupuesto**, todavía sin aprobar. Si el bloque 5 entusiasma, es el momento natural para retomarlos — pero como
  conversación aparte, después de la reunión, no adentro.

## Después de la reunión (mismo día)

- [ ] Mandar por mail el resumen de lo que quedó configurado, el enlace al portal y los accesos de los nuevos miembros.
- [ ] Anotar en [trazabilidad.md](trazabilidad.md) qué se configuró y qué decisiones tomó el estudio.
- [ ] Volcar a `definiciones/1-analista-funcional.md` lo que salga del bloque 5 (el instructivo es insumo directo del
      agente a medida de conciliación, si se aprueba).
