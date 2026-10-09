---
name: mutante-del-importe-y-el-eco-de-ui
description: Cuando el Service verifica "el usuario vio este importe", un mutante del importe rechaza TODAS las operaciones y lo que se mide es una cascada; y como disenar el fixture para que el numero correcto y el incorrecto difieran de verdad.
metadata:
  type: feedback
---

**Si el Service verifica que el importe confirmado por el usuario coincida con el que el recalcula
(el patron del "eco" de UI), un mutante que cambie ese importe hace que el Service RECHACE TODAS las
operaciones.** El arnes, que replica la formula para poder mandar el valor correcto, deja de medir la
propiedad del mutante y mide una cascada. **Un mutante del importe tiene que apagar TAMBIEN el eco.**

**Why:** en la-platense modulo 16, `M2` ("la NC no devuelve nada del cargo de IVA") tumbaba **21**
afirmaciones — y casi ninguna por la propiedad que el mutante rompe: tumbaba las de los totales, las
del tipo de comprobante, las de concurrencia y las de atomicidad, porque ninguna emision llegaba a
pasar. Peor: dejaba `3.6` (la afirmacion del remanente, la mas importante del lote) en **NO MEDIDA**,
porque su precondicion es que la nota de credito se haya emitido. Con el eco apagado el mismo mutante
tumba **11**, y las 11 son del importe. Es la regla general dicha en concreto: *una afirmacion
condicional no se puede matar con un mutante que rompe su precondicion*.

**How to apply:** marcar en el driver que esos mutantes llevan un segundo cambio, el del eco, y
dejar escrito por que. Y correr un mutante que apague **solo** el eco, para que esa verificacion
tambien quede medida por si misma. Dos sintomas de que el mutante rompio la precondicion en vez del
invariante: la cantidad de tumbadas es desproporcionada, y aparecen `NO MEDIDA` justo en las
afirmaciones que el mutante deberia matar.

## El fixture se DISENA para que el numero correcto y el incorrecto difieran

La primera forma de falso verde (la afirmacion que pasa con y sin el fix) casi nunca se evita
mirando la afirmacion: se evita **eligiendo los datos**. Dos casos medidos en esta corrida:

- Una afirmacion `[DISCRIMINA]` sobre "el precio es el EFECTIVO y no el de LISTA" miraba una linea
  **sin descuento ni recargo**, donde los dos precios son el mismo numero. El mutante que congela el
  precio de lista la dejaba en verde. La linea que discrimina es la que tiene descuento **y** recargo
  (lista 1000 / efectivo 900), y hay que sembrarla a proposito — el camino facil es cargar la venta
  con descuento 0.
- Para medir una regla de **redondeo** hay que FABRICAR la deriva, porque con numeros redondos las
  dos implementaciones dan lo mismo. Receta: un precio con centavos que no dividan bien
  (`100,01`), facturado por `3`. El impuesto del comprobante es `round(300,03 x 21%) = 63,01`, pero
  partido en `1 + 2` da `21,00 + 42,00 = 63,00`: **un centavo**, que es exactamente lo que separa
  "devolver el remanente" de "devolver la proporcion redondeada". Sin ese producto en el fixture, la
  regla entera queda sin medir y el arnes igual sale 45/45.

## Y una afirmacion puede PASAR POR EL MOTIVO EQUIVOCADO

`5.7` afirmaba "un importe de devolucion distinto rechaza la emision" forzando un importe malo sobre
un comprobante que, a esa altura de la corrida, **ya estaba acreditado por completo**: el rechazo que
llegaba era el del **tope de cantidad**, no el del eco. La afirmacion decia OK y el mensaje probaba
otra cosa; un mutante que borrara el eco la habria dejado en verde.

**Solo se ve leyendo el TEXTO del rechazo que el arnes imprime** — razon suficiente para imprimirlo
siempre, y para que la afirmacion **exija que el mensaje hable de lo que se esta midiendo** y no solo
que haya fallado. Y el fixture de cada guarda conviene que sea **propio**, no el que quedo del paso
anterior.

## Dos detalles operativos del mismo dia

- **`ServiceResult.CreateError` tiene dos sobrecargas**: la de un mensaje llena `Message` y deja
  `Errors` vacio; la de lista llena `Errors` y deja `Message` en null. Afirmar sobre uno solo de los
  dos produce un **falso ROJO** (una guarda que funciona reportada como falla), que es la cara menos
  conocida del problema y la que manda a "arreglar" codigo sano. Un helper que concatene los dos.
- **Un archivo de mutantes se escribe ENTERO, no se parchea.** Parcheé la lista con `str.replace`
  **sin assert** y el ancla no matcheo: dos mutantes corrieron sin el cambio que yo creia haberles
  puesto, y "sobrevivieron" por no haber mutado. Y el segundo intento uso `re.sub`, que **interpreta
  las secuencias de escape del REEMPLAZO**: convirtio los `\n` de los anclas en saltos de linea
  reales y dejo el driver sin compilar. Si hay que generar codigo con `re.sub`, el reemplazo va como
  `lambda _m: texto`.

Ver tambien [[arnes-que-muere-en-vez-de-medir]] y [[sonda-ef-desechable]].
