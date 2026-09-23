# Cuestionario de cierre de Análisis — Contadores BMA

**Fecha:** 2026-09-23 · Para cerrar Análisis y poder abrir Presupuesto.
Estado del proyecto: el **tramo técnico está cerrado** (ver
[research-arca-arba-sos-2026-09.md](research-arca-arba-sos-2026-09.md)). Lo que falta es de negocio y de accesos.

Marcadas con 🔴 las que **bloquean**: sin ellas no se puede cotizar.

---

## A. Modelo y alcance

**A1** 🔴 ¿Se confirma que esto se entrega como **configuración del producto `olvidata-agentes-multirubro`** (BMA es una
organización del sistema, cada usuario releva lo suyo con el analista de automatizaciones y Olvidata solo destraba), y
**no** como la plataforma a medida que estaba planteada en agosto (servidor central + agente por PC)?
☐ Sí, como configuración del producto ☐ No, revisemos

**A2** ¿El alcance de esta primera etapa son las **tres ramas** (Contabilidad, Impuestos, Sueldos) o arrancamos por una?
☐ Las tres ☐ Solo Impuestos ☐ Solo Contabilidad ☐ Otra: ___

**A3** El **conversor de sueldos** ya entregado (`contadores-bma-conversor`) ¿queda como está, o el estudio espera que se
absorba adentro del sistema nuevo?
☐ Queda como está ☐ Se absorbe más adelante ☐ Se absorbe ahora

## B. Gente y volumen — define licencias, costo y cuántos relevamientos

**B1** 🔴 ¿Cuántas personas hay **por rama**? (Contabilidad ___ · Impuestos ___ · Sueldos ___ · alguien que toque varias ___)

**B2** ¿Cuántas **empresas/clientes** atiende el estudio en total? Y de esas, ¿cuántas son de Convenio Multilateral? ___

**B3** ¿Quién es el **Director** en el sistema (el que aplica lo que alcanza a toda la empresa)? ¿Uno o varios? ___

**B4** ¿Quién sería la **persona del piloto** de conciliación bancaria? (Gastón ya figura como candidato en el discovery)
___

## C. Accesos y habilitaciones — define qué se automatiza ya y qué espera

**C1** 🔴 **Delegación de clave fiscal**: ¿los clientes ya le delegaron al estudio el acceso en ARCA, o se entra con la
clave de cada cliente? Sin delegación, ningún servicio de ARCA sirve para consultar por terceros.
☐ Ya está delegado ☐ Se usa la clave de cada cliente ☐ Depende del cliente ☐ No sé

**C2** ¿El estudio tiene **usuario y contraseña de ARBA** para el servicio de consulta de alícuotas? ¿Y **CIT de agente
de recaudación** (para bajar el padrón mensual completo)?
☐ Tengo ambos ☐ Solo usuario ARBA ☐ Ninguno ☐ No sé

**C3** ¿Con qué usuario se usa **SOS Contador**? ¿Hay un usuario del estudio con acceso a todas las CUIT de la cartera, o
uno por cliente? (La API pide un token por CUIT.) ___

**C4** ¿El estudio ya usa la **API de SOS** para algo, o sería la primera vez? ☐ Ya la usa ☐ Primera vez

## D. La tarea nuclear — para escribir bien el agente

**D1** 🔴 **Sobre los duplicados.** La documentación de SOS dice que **deduplica por CAE**, así que Autoimpo no debería
repetir. La hipótesis es que los duplicados aparecen por **mezclar Autoimpo con importación manual del XLS**, o por
comprobantes **sin CAE** (controladores fiscales viejos). ¿Coincide con lo que ven?
☐ Sí, importamos a mano además de Autoimpo ☐ No, aparecen igual ☐ No sé / hay que mirarlo

**D2** ¿Tienen **Autoimpo activado** en SOS para todos los clientes, para algunos, o para ninguno?
☐ Todos ☐ Algunos ☐ Ninguno ☐ No sé

**D3** ¿Cada cuánto hacen hoy el control contra ARCA? ☐ Mensual, al liquidar ☐ Semanal ☐ Solo cuando algo no cierra

**D4** ¿Cuánto tiempo les lleva ese control, por cliente y por mes, aproximadamente? ___

**D5** Cuando detectan una diferencia, ¿qué hacen? ☐ La cargan a mano en SOS ☐ La importan del XLS ☐ Depende

**D6** ¿El control es solo de **comprobantes recibidos** (compras) o también de **emitidos** (ventas)? *(La API de SOS
solo lista recibidos; para emitidos habría que exportar.)*
☐ Solo recibidos ☐ También emitidos

**D7** **Sueldos**: ¿qué datos concretos van a constatar a ARBA? (convenio multilateral, locales, ¿algo más?) ___

## E. Decisiones que son de Olvidata pero necesitan tu visto bueno

**E1** 🔴 **Calendario, alícuotas y escalas.** Hoy el rubro los deja **a propósito sin cargar**, porque un vencimiento
viejo dicho con seguridad es peor que no tenerlo. BMA los necesita. ¿Los cargamos y **Olvidata se compromete a
mantenerlos**, o el agente sigue sin darlos y remite a la fuente oficial?
☐ Cargar y mantener ☐ No cargar, remitir a la fuente ☐ Cargar solo el calendario de vencimientos

**E2** **Tope de gasto** mensual de la organización, y por persona. Con varias personas relevando y programando, conviene
fijarlo antes del primer susto, no después. ¿Qué número? USD ___ /mes

**E3** **Etapa de entrega inicial** del menú. La propuesta es arrancar en *"Tu forma de trabajar"* (Reglas, Instructivos y
Automatizar a la vista; Programaciones/Aprobaciones/Consumo escondidas hasta que el estudio esté listo).
☐ De acuerdo ☐ Arrancar con todo visible ☐ Arrancar más acotado

**E4** ¿Querés que el **rubro contable** (el repo fuente `Agente Contable-IA`) quede **versionado en git**? Hoy es una
carpeta suelta, igual que el de inmobiliario. ☐ Sí, versionarlo ☐ Dejarlo como está

## F. Lo que sigue abierto de Onvio (no bloquea, pero conviene preguntar)

**F1** ¿Alguien le preguntó al **ejecutivo de cuenta de Thomson Reuters** si existe un canal de integración autorizado
para Bejerman Web/Onvio Argentina? (En Brasil existe una API oficial; en Argentina no se encontró.)
☐ Ya preguntamos: ___ ☐ No preguntamos todavía ☐ No nos interesa por ahora

**F2** ¿Tenés a mano el **contrato real** que firmó BMA con Thomson Reuters, para confirmar la cláusula de uso? (Se usó
como referencia la versión global de los *Onvio Full Terms*.) ☐ Sí ☐ No

---

## Lo que ya NO hace falta preguntar (resuelto por research el 2026-09-23)

- ~~Qué web service de ARCA lista los comprobantes recibidos~~ → **no existe ninguno**; se usa el export de Mis Comprobantes.
- ~~Si la API de SOS lista los comprobantes~~ → **sí, los recibidos** (`GET /compra/listado/:periodo`).
- ~~Qué expone ARBA~~ → alícuotas por servicio web y padrón mensual en `.txt`; **Convenio Multilateral va por COMARB**.
- ~~Cómo se complementan Bejerman y SOS~~ → **por rama**, no por cartera.
- ~~Si hay doble carga de sueldos~~ → **no**, sueldos vive solo en Onvio.
