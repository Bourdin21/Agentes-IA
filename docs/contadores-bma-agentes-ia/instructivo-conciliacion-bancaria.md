# Conciliación bancaria — instructivo, reglas, recuerdos y prueba

**Qué es este documento.** Los textos **listos para cargar en el portal** de Olvidata Agentes, tal cual, sin reescribir.
No es documentación del proceso: es el contenido de los artefactos. Cada bloque dice en qué pantalla va y con qué alcance.

**De dónde salió.** Ingeniería inversa de tres planillas reales del estudio (EINKAREM SA, cuenta corriente 5632/4 del
Banco Provincia, ejercicio 2024-2025), analizadas el 2026-10-06:

| Archivo | Qué contiene |
|---|---|
| `CONCILIACION BANCO PROVINCIA EINKA 2024-2025.xlsx` | Hoja `MAYOR` (mayor del ejercicio completo, 1.855 filas, con columnas de control) + hoja `CONCILIACION` (el papel de trabajo al 31/08/2024) |
| `07-2024 EXTRACTO JULIO-2024.xlsx` | Extracto de julio 2024 + zona de trabajo abajo donde se arman los asientos del mes |
| `08-2025 EXTRACTO AGOSTO-2024.xlsx` | Ídem agosto 2024 (el nombre del archivo dice 08-2025; la hoja y los datos son 08-2024) |

**En qué difiere del oficio general** (lo que el agente hace hoy, según `conocimiento/35-conciliacion-bancaria.md`):
el cuadro va de contabilidad hacia el banco y no al revés; es acumulativa y no mensual aislada; no se escribe la lista
de emparejados; el mayor se controla contra sí mismo antes de conciliar; y la mitad del trabajo es armar los asientos
del mes agrupando el extracto, que hoy no está en ninguna parte.

> **Dato incómodo verificado.** La hoja `CONCILIACION` cierra en cero porque incluye, entre los ajustes, una línea
> descrita solo como **«ajuste» por $1.139.686,97** (fila 189). Sin esa línea la diferencia no da cero. Es un ajuste sin
> identificar, y es precisamente lo que el agente **no** tiene que aprender a hacer: la regla R6 lo prohíbe de forma
> explícita. Confirmar con Gastón si ese importe tiene un origen conocido que no quedó escrito.

---

## 1. Instructivo

Va en **Instructivos → Nuevo**. Visibilidad: *Toda la empresa*. Es el método del estudio, sirve para cualquier cliente
con cuenta bancaria; lo propio de EINKAREM va en la regla R5 y en los recuerdos.

**Título** (máx. 150)

```
Cómo armamos una conciliación bancaria en el estudio
```

**Para qué sirve** (máx. 300 — es lo único que lee el modelo para decidir si lo carga)

```
Armar la conciliación bancaria mensual de una cuenta de un cliente: el control previo del mayor, los asientos del mes que salen del extracto, la lista de ajustes y el cuadro que cierra en cero.
```

**Pasos** (máx. 8.000 caracteres)

```
Una conciliación por cliente, por cuenta y por mes. Si el cliente tiene dos cuentas, son dos conciliaciones: no se mezclan.

1. Juntá los tres papeles.
   - El mayor de la cuenta bancaria del ejercicio completo, no solo del mes: lo exporta el sistema contable con fecha, comprobante, detalle, debe, haber y saldo.
   - El extracto del banco del mes, con el saldo anterior en la primera fila y el saldo final en la última.
   - La conciliación del mes anterior. Sin ella no arranques: nuestra conciliación es acumulativa y las partidas pendientes vienen de ahí.
   Si falta alguno de los tres, decí cuál falta y pedilo. No lo reemplaces por lo que puedas deducir del otro lado.

2. Controlá el mayor antes de conciliar.
   Recorré el mayor fila por fila recalculando el saldo: saldo de la fila anterior, más el debe, menos el haber. Comparalo con el saldo que el mayor informa en esa fila. Donde no da, hay una fila faltante, duplicada o fuera de orden.
   Las diferencias se listan con el número de fila, el comprobante y los dos saldos, y se avisan antes de seguir: conciliar sobre un mayor que no cierra consigo mismo es trabajo perdido.
   Verificá también que el saldo anterior del extracto sea el saldo final del extracto del mes pasado. Si no coincide, el problema es del mes anterior: decilo y no sigas como si nada.

3. Armá los asientos del mes desde el extracto.
   Esto va antes de conciliar, porque la mitad de lo que falta registrar sale de acá. Agrupá los movimientos del extracto y dejá cada grupo con su total:
   - Gastos del banco: comisiones (mantenimiento, transferencia y giro, Datanet, compromiso de fondos), liquidación de préstamos, impuesto a los ingresos brutos percepción, impuesto al débito y crédito de la ley 25413, ingresos brutos SIRCREB e intereses cobrados del período. El total de ese grupo es el asiento de gastos bancarios del mes.
   - Sueldos: los débitos de lote de haberes, de aguinaldo y de fondo de desempleo, sumados por fecha de débito. Cada fecha es un asiento.
   - Servicios y pagos recurrentes: los pagos de servicios y las transferencias que se repiten todos los meses al mismo destino, listados aparte con fecha e importe.
   El impuesto al débito de un movimiento va en el grupo de gastos del banco, nunca pegado al movimiento que lo generó.

4. Emparejá, sin escribir lo emparejado.
   Emparejá el extracto contra el mayor en este orden: importe y fecha exactos; número de cheque, de transferencia o CBU; importe exacto con la fecha corrida unos días, porque los cheques se compensan después del registro; y por último un movimiento contra varios, dejando escrito cómo lo agrupaste.
   Un débito del banco se empareja contra un pago registrado y una acreditación contra un cobro. Un movimiento ya emparejado no se vuelve a usar, y dos del mismo importe se distinguen por su referencia, nunca por el orden en que aparecen.
   Lo que cerró no va a ninguna lista: nuestro papel no lleva la lista de emparejados. Lo que importa es lo que no cerró.

5. Armá la lista de ajustes, de contabilidad hacia el banco.
   Arrancá copiando los ajustes de la conciliación del mes anterior que todavía no se resolvieron, y saca los que sí. Después agregá los del mes.
   - Lo que el banco debitó y no está registrado va con el importe en negativo, descrito con el texto literal del concepto del extracto: por ejemplo "CHEQUE DE CAMARA 004597288" o "AYSA SA RE.004265291850 ID.0000231934".
   - Lo que está registrado y el banco no debitó va con el importe en positivo, descrito con el texto literal del detalle del mayor, con el código de proveedor incluido: por ejemplo "(00445) -CESAR AGUERO" o "GASTOS CACHO".
   El texto literal es lo que permite que otra persona encuentre el movimiento en el papel original sin volver a buscarlo. No lo reescribas, no lo abrevies y no lo interpretes.

6. Dejá los cuatro renglones de partidas en tránsito, cada uno con su detalle de período, número e importe: cheques diferidos no debitados y depósitos no acreditados, que están en contabilidad y no en el banco; depósitos no contabilizados y cheques diferidos debitados, que están en el banco y no en contabilidad.

7. Cerrá el cuadro, en este orden:
   Saldo según contabilidad al corte, que es el saldo del mayor en la última fila del mes y no un número tipeado.
   Más el total de ajustes, da el saldo ajustado.
   Más los cuatro renglones de partidas en tránsito, da el saldo contable.
   Menos el saldo según banco, que es el saldo de la última fila del extracto, da la diferencia.
   La diferencia tiene que dar cero. Las cuentas las hacés con la calculadora, una por una.

8. Si la diferencia no da cero, buscala antes de informarla: el importe exacto en los dos lados; dividido por dos, porque si da un movimiento que existe está duplicado o con el signo al revés; divisible por nueve, que son dígitos transpuestos al tipear; el corte de mes, el último día y el primero del siguiente; y la otra cuenta del mismo banco, si el cliente tiene dos. Si igual no aparece, se informa con el importe exacto.

9. Entregá la planilla, con una hoja por cosa: el control del mayor, los grupos de asientos del mes con sus totales, la lista de ajustes, las partidas en tránsito y el cuadro final. Encabezado con estudio, cliente, banco, número de cuenta y período.

Lo que no se hace: no se redondea para que cierre, no se inventa una tolerancia, no se corrige el mayor —los errores se señalan con los dos valores y los corrige quien registró—, y un débito que lleva el nombre de un proveedor no es por eso el pago de su factura: si no hay respaldo, va como a confirmar.
```

---

## 2. Reglas

Van en **Reglas → Nueva**. Las de método con alcance **Agente → Conciliación bancaria** (así entran solo en las tareas de
ese agente, no en el prompt de todos). La R5 con alcance **Cliente + Agente**. Todas en modo **Obligatoria**.

### R1 — La conciliación arranca en el saldo de contabilidad
*Alcance: Agente → Conciliación bancaria. Modo: Obligatoria.*

```
El cuadro de conciliación de este estudio va de contabilidad hacia el banco: arranca en el saldo según contabilidad al corte, le suma el total de ajustes y las partidas en tránsito, y termina restando el saldo según banco. La diferencia tiene que dar cero, sin tolerancia. No armes el cuadro al revés, del extracto hacia la registración, aunque sea la forma más común del oficio. Los dos saldos de partida se toman del papel: el de contabilidad es el saldo del mayor en la última fila del mes, y el del banco es el saldo de la última fila del extracto.
```

### R2 — La conciliación es acumulativa: sin la del mes anterior no arranca
*Alcance: Agente → Conciliación bancaria. Modo: Obligatoria.*

```
Las partidas pendientes se arrastran de mes a mes. Antes de conciliar un mes, conseguí la conciliación del mes anterior y partí de sus ajustes: saca los que se resolvieron y agregá los nuevos. Si no la tenés, decilo y pedila antes de empezar. Una conciliación armada de un mes aislado muestra como pendiente del mes lo que ya venía pendiente de antes, y el cuadro no cierra.
```

### R3 — Las partidas se describen con el texto literal del papel original
*Alcance: Agente → Conciliación bancaria. Modo: Obligatoria.*

```
En la lista de ajustes, cada partida se describe copiando el texto tal como está en el papel de donde salió: el concepto completo del extracto para lo que debitó el banco, y el detalle del mayor con el código de proveedor entre paréntesis para lo que está registrado. No lo reescribas, no lo abrevies, no lo traduzcas y no lo interpretes. Ese texto es lo único que permite encontrar el movimiento en el original sin volver a buscarlo.
```

### R4 — El papel no lleva la lista de movimientos emparejados
*Alcance: Agente → Conciliación bancaria. Modo: Obligatoria.*

```
La planilla de conciliación del estudio no incluye la lista de los movimientos que cerraron. Lo que se entrega es el control del mayor, los grupos de asientos del mes, la lista de ajustes, las partidas en tránsito y el cuadro final. Si hace falta mostrar un emparejamiento puntual —uno que agrupó varios movimientos contra uno, o uno que quedó ambiguo— va como nota en esa partida, no como hoja aparte.
```

### R5 — La cuenta que conciliamos de EINKAREM
*Alcance: Cliente EINKAREM SA + Agente → Conciliación bancaria. Modo: Obligatoria.*

```
De EINKAREM se concilia la cuenta corriente 5632/4 del Banco Provincia, que en el plan de cuentas es la 1110502 "BANCO PCIA BS AS CTA CTE 5632/4". El corte es el último día de cada mes y el ejercicio cierra el 30 de junio. El mayor se pide por el ejercicio completo y el extracto del banco viene por mes, en un archivo por mes.
```

### R6 — Una diferencia sin identificar se informa, no se ajusta
*Alcance: Agente → Conciliación bancaria. Modo: Obligatoria.*

```
Nunca agregues a la lista de ajustes una línea sin descripción, llamada "ajuste", "diferencia" o parecido, para que el cuadro cierre. Si después de buscar la diferencia no la encontraste, el cuadro se entrega con la diferencia a la vista y su importe exacto, y decís qué probaste para buscarla. Una conciliación que cierra con un ajuste sin identificar tapa el problema y lo hereda el mes siguiente. Si en la conciliación del mes anterior encontrás una línea así, no la copies: señalala y preguntá de dónde salió.
```

**Presupuesto de caracteres.** R1 a R4 y R6 suman ~2.400 contra el tope de 20.000 del alcance Agente; R5 ~400 contra los
8.000 del alcance Cliente. Sobra lugar.

---

## 3. Recuerdos a sembrar

Van en **Memoria → Nuevo**, alcance **Cliente EINKAREM SA**. Son hechos de la cuenta, no instrucciones: por eso van acá
y no como reglas. Solo lo verificado en los tres archivos; lo que no, está marcado abajo.

| Título | Cuándo sirve | Texto |
|---|---|---|
| El período de gastos del Banco Provincia va del 29 al 28 | Al armar el asiento de gastos bancarios del mes de la cuenta 5632/4 | Las comisiones, los intereses y las percepciones de la cuenta 5632/4 se liquidan por período del 29 de un mes al 28 del siguiente, no por mes calendario, y se debitan al cierre de ese período. En el extracto de agosto 2024 figuran como "COM. MANT. POR 098 MOV. PERIODO (29-07-2024/28-08-2024)" e "INTERESES COBRADOS PERIODO DESDE 29-07-2024 HASTA 28-08-2024". |
| Los cuatro asientos de cierre de mes de EINKAREM | Al cerrar el mes de la cuenta 5632/4 | El mayor de la cuenta 5632/4 cierra cada mes con cuatro asientos de ajuste contable fechados el último día: Gastos Banco Provincia, Plazos Fijos, Fondo Común de Inversión y Transferencias entre cuentas. El de Gastos Banco Provincia es el que sale de agrupar los gastos del extracto; en agosto 2024 fue de 2.979.979,92 y coincidió exacto con el agrupado. |
| Dos códigos de ente del extracto del Banco Provincia | Al identificar un pago de servicio "P.SERV ... -ENTExxx" de EINKAREM | En los pagos de servicio del extracto, el código de ente ENTEFKP es UOCRA y ENTE569 es IERIC. Los dos están anotados a mano en el extracto de julio 2024 por quien lo trabajó. Los demás códigos de ente no están identificados: se preguntan, no se adivinan. |

**A confirmar con Gastón antes de sembrar** (no verificable desde los archivos): cuántos días tarda en compensar un
cheque de esta cuenta; si hay tolerancia aceptada y de cuánta; qué significan los conceptos "GASTOS CACHO",
"GASTOS HERNAN" y "CAJA CHICA Y GASTOS MAXI" del mayor; y el origen de la línea «ajuste» de $1.139.686,97.

---

## 4. Documentos a cargar

Los tres archivos van como **documentos del cliente EINKAREM SA**, así el agente los puede abrir con `documento_leer`
y usarlos de modelo. Sin ellos, el instructivo describe el papel pero el agente no lo vio nunca.

- `CONCILIACION BANCO PROVINCIA EINKA 2024-2025.xlsx` — es el modelo del papel terminado **y** el insumo del mes
  siguiente: la hoja `MAYOR` es el mayor del ejercicio y la hoja `CONCILIACION` es la conciliación al 31/08/2024.
- `07-2024 EXTRACTO JULIO-2024.xlsx` y `08-2025 EXTRACTO AGOSTO-2024.xlsx` — los extractos, con la zona de trabajo
  abajo que muestra cómo se agrupan los asientos del mes. **Es la parte que más enseña y la que no estaba escrita.**

---

## 5. La prueba

No va como evaluación del núcleo: es contenido de un cliente, y las evaluaciones del rubro no llevan datos de clientes.
Va como **prueba de la organización** (tarea de trabajo marcada como prueba, que no cuenta como trabajo hecho).

**Caso:** conciliar la cuenta 5632/4 de EINKAREM al 31/08/2024, con el mayor del ejercicio, el extracto de agosto 2024
y la conciliación al 31/07/2024 como punto de partida.

**Resultados esperados, verificables contra el papel real:**

| Qué | Valor |
|---|---|
| Saldo según contabilidad al 31/08/2024 | 26.178.859,42 |
| Saldo según banco al 31/08/2024 | −7.939.520,56 |
| Total de ajustes | −34.118.379,98 |
| Diferencia | 0 |
| Asiento de gastos bancarios de agosto (agrupado del extracto) | −2.979.979,92 |

El total de ajustes del papel real **incluye** la línea «ajuste» de 1.139.686,97. Un agente que cumple la R6 va a llegar
a −35.258.066,95 de ajustes identificados, a un saldo contable de −9.079.207,53 y a informar una diferencia de
−1.139.686,97 sin explicar. **Ese es el
resultado correcto**, no el del papel: la prueba se califica a favor del agente si informa la diferencia, y en contra si
la cierra con una línea sin descripción.

---

## 6. Lo que queda abierto

**`planilla_armar` no puede reproducir ese papel tal cual.** La herramienta arma hojas tabulares —columnas tipadas y una
fila de totales `=SUM(...)`— y no admite fórmulas libres ni links entre hojas. El papel real usa las dos cosas: el saldo
de contabilidad es `=+MAYOR!H356` y el del banco es un link al archivo del extracto, y el control del mayor son dos
columnas de fórmula por fila. El paso 9 del instructivo está escrito para la variante tabular, que conserva toda la
información y pierde los links. Decisión pendiente de Joaquín: dejarlo así, o agregar a M19 la posibilidad de rellenar
una plantilla que sube el cliente, que es feature nueva.

**El control del mayor es oficio general, no método de BMA.** El recálculo del saldo fila por fila para cazar filas
faltantes o fuera de orden le sirve a cualquier estudio y hoy no está en
`C:/Sistemas/Agente Contable-IA/conocimiento/35-conciliacion-bancaria.md`. Ahí sí corresponde agregarlo, como versión
nueva del rubro `contable` con su evaluación.
