# Memoria - Documentador

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

## Definiciones vigentes

### Alcance entregado al cliente

## Entrega 2026-10-01 — Finanzas y contadores de máquinas

Resolvimos los cinco puntos que nos pasaste. Esto es lo que vas a ver distinto:

**1. El saldo acumulado ahora cierra con el saldo de la cuenta.**
Cuando había varios movimientos cargados el mismo día, el listado no los mostraba en el orden real en que se cargaron. Por eso el acumulado de la última línea no coincidía con el saldo de la cuenta. Los números siempre estuvieron bien: lo que estaba mal era el orden en que se mostraban. Ya quedó ordenado de forma consistente.

De paso, esto corrigió algo que todavía no habías notado: al pasar de página en un listado largo, alguna línea podía repetirse o quedar sin mostrar. Ya no pasa.

**2. Los movimientos de cuentas propias arrancan en "Egreso".**
Como el 99% de lo que se carga desde ahí son egresos, ahora viene preseleccionado. Si necesitás cargar un ingreso o una transferencia, lo cambiás como siempre.

**3. Después de cargar un movimiento volvés a la cuenta donde estabas.**
Antes te mandaba a una pantalla general de movimientos que era confusa y pedía elegir una cuenta entre todas. Ahora, si cargaste un gasto en Efectivo, volvés a Efectivo y ves el movimiento recién cargado ahí mismo.

**4. El número de comprobante ya se ve en los listados.**
Lo agregamos al lado de la fecha, en los listados de cuentas propias, de cuentas corrientes de clientes y en el listado general. Los movimientos sin comprobante muestran un guion.

**5. El sistema ya no deja cargar un contador menor al anterior.**
Esta era la causa de los contadores en cero. Cuando alguien cargaba un contador y dejaba el campo vacío, el sistema lo guardaba como cero sin avisar nada, y eso rompía el cálculo de copias de esa máquina. Revisamos el historial completo: **hay 110 registros con contador en cero, 69 de ellos claramente mal, repartidos en 58 máquinas**, concentrados sobre todo en abril y mayo.

De ahora en adelante el sistema lo rechaza y te dice cuál es el valor mínimo que podés cargar, por ejemplo: *"El contador B/N debe ser mayor o igual a 4.018.041"*.

> **Importante para el día a día:** si venías cargando contadores dejando algún campo vacío, ahora el sistema te lo va a rechazar. Es intencional. Una máquina recién instalada sí puede arrancar en cero, porque todavía no tiene historial con el cual comparar.

### Pendientes o fuera de alcance

**1. Los 69 registros mal que ya están cargados.** La corrección que hicimos evita que se sigan generando, pero **no corrige los que ya están**. Quedamos en corregirlos con los valores reales. Te pasamos una planilla con los **69 registros sobre 39 máquinas**, donde para cada uno te mostramos la última lectura real anterior y la primera posterior, para que puedas acotar el valor en lugar de buscarlo a ciegas. Solo hay que completar las dos últimas columnas (contador B/N y Color reales).

En 28 de los 69 casos tenés lectura anterior **y** posterior, así que el valor correcto está en un rango cerrado. En los 41 restantes no hay lectura posterior, así que dependemos del registro real que tengas.

**2. ~~La pantalla de ajuste de contadores acepta negativos sin límite.~~ RESUELTO.** Ahora el sistema calcula cuánto se puede descontar como máximo en esa máquina y rechaza el ajuste si lo pasa, diciéndote el mínimo admitido. El ajuste negativo sigue estando disponible, que es un caso legítimo; lo que ya no se puede es dejar los contadores en negativo.

**3. ~~Varias columnas parecen ordenables y no ordenan.~~ RESUELTO.** Importe, Comprobante, Cuenta, Tipo, Motivo y Notas ahora ordenan de verdad, ascendente y descendente. Las únicas que quedan sin ordenar son Saldo Acumulado y Acciones, a propósito: el saldo acumulado se calcula siempre en orden cronológico, así que ordenarlo por pantalla no tendría sentido.

**5. Hay 441 movimientos que no aparecen en el listado general.** El contador al pie dice 9.748 pero se muestran 9.307. Son movimientos cuya cuenta fue dada de baja. Es el mismo problema que ya corregimos en agosto con los alquileres. Lo detectamos revisando, no lo tocamos en esta entrega y queda señalado.

**4. La pantalla general de "Movimientos" sigue existiendo.** Ya no vas a aterrizar ahí, pero no la eliminamos. Si querés que la saquemos del todo, decinos.

### Beneficios comunicados
- La conciliación de cuentas vuelve a ser confiable: el acumulado cierra contra el saldo.
- Menos clics y menos errores en la carga diaria de egresos.
- El comprobante a la vista en el listado, sin tener que abrir cada movimiento — sobre todo en cuentas corrientes de clientes.
- La facturación por copia deja de ensuciarse con contadores en cero cargados por error.

### Proximo paso sugerido
1. **Antes de publicar:** avisarle al equipo que carga contadores que el formulario ahora puede rechazar, y por qué.
2. **Definir qué hacer con los 69 registros mal** (corregir con valores reales o dar de baja).
3. **Decidir si entra la pantalla de ajuste de contadores** (punto 2 de pendientes) en una próxima entrega.

## Historial de ajustes
- 2026-10-01: Documentación de la entrega de 5 ítems (4 de Finanzas + contadores de máquinas). Es la primera entrega de este proyecto que pasa por el ciclo completo con QA en 3 pasadas (2 por lote + 1 de re-verificación de fixes).
