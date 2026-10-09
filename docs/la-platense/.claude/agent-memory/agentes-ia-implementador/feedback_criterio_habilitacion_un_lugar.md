---
name: criterio-habilitacion-un-lugar
description: En La Platense todo criterio de habilitacion de una accion se escribe UNA vez y devuelve la razon por la que NO se puede; "hay guarda" se ve igual que "hay LA guarda" y por eso la revision por lectura no encuentra la divergencia
metadata:
  type: feedback
---

**Todo criterio de habilitacion de una accion se escribe UNA vez, en el dominio o en el Service, y
devuelve LA RAZON POR LA QUE NO SE PUEDE (`null` = se puede). Lo consumen las TRES puntas: el `GET`
que abre la pantalla, el `POST` que ejecuta, y la vista que decide si muestra el boton.**

Vive en `FerreteriaLaPlatense.Domain/Reglas/HabilitacionDeAccion.cs`. La regla completa esta en
`3-arquitecto-mvc.md` v13, seccion *"El criterio de habilitacion vive en UN lugar"*.

**Why: cuatro apariciones del mismo defecto.** `LP-039` (anular con comprobante vivo), `LP-040`
(facturar por el camino legado), el combo de Editar de una compra y `LP-052`. Y el agravante de
`LP-052` es lo que convierte esto de prolijidad en necesidad: **el boton guardaba TRES condiciones y
el `GET` guardaba UNA.** No faltaba la guarda — **habia guarda, pero no la misma** — asi que un
chequeo de *"¿el GET esta protegido?"* **daba VERDE** mientras `GET /NotasCredito/Emitir/5` sobre una
nota de credito devolvia **200** con el formulario armado, rotulando la NC como "factura".

**El chequeo correcto no es "hay guarda" sino "hay LA MISMA guarda"**, y la unica forma de que valga
es que no haya dos listas de condiciones que comparar.

**How to apply:**

- **Si una condicion de habilitacion aparece en dos archivos, se mueve a `HabilitacionDeAccion`.** No
  se "sincronizan" dos copias: ya sabemos que la revision por lectura no encuentra la divergencia.
- La vista usa la razon tambien **como leyenda**: decir POR QUE no esta el boton es la mitad que evita
  el ticket de soporte, y sale gratis porque el texto ya existe.
- **El Service la evalua UNA vez y con los datos releidos bajo lock**, que es la unica evaluacion que
  autoriza. Si hace falta un rechazo barato antes de abrir la transaccion, **que sea la misma funcion
  con otra foto** — y si despues el metodo se parte y las dos llamadas terminan leyendo las mismas
  filas, **se borra una**: dos evaluaciones identicas obligan al proximo lector a compararlas para
  descubrir que no se diferencian.

**Lo que NO entra, y declararlo es parte de la regla:**

1. **Las guardas de concurrencia.** *"¿la fila se dio de baja mientras preparabamos la pantalla?"* es
   la segunda mitad de la relectura bajo lock, solo existe dentro de una transaccion y la vista no
   puede evaluarla. Vive en el Service, al lado de su lock. Ver
   [[relectura-bajo-lock-soft-delete]].
2. **Los topes por item.** El criterio contesta *"¿se puede entrar a esta pantalla?"*; el tope
   contesta *"¿esta cantidad es valida?"*. El segundo necesita el dato releido bajo lock y no tiene
   sentido en un boton.
3. **La aritmetica.** Estos metodos no calculan pendientes ni saldos: los **reciben**. Que haya UN
   lector de cada hecho es el otro problema (el barrido), no este.

**Y la trampa que la mutacion destapo, porque es la que se repite:** el mutante que apaga la tercera
condicion del criterio **sobrevive** si las unicas afirmaciones son de integridad de datos. El tope
por item frena la emision igual, con otro mensaje, asi que **el dato no se corrompe — pero la puerta
se abre.** Se mide **por la RAZON y no por el dato**: que el `GET` conteste un motivo, y que el `POST`
rechace con **el mismo texto, comparado como string**. Ver [[arnes-falla-del-instrumento]].
