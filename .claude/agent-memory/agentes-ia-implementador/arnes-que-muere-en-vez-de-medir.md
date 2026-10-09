---
name: arnes-que-muere-en-vez-de-medir
description: Al medir por mutacion, una afirmacion que indexa o desreferencia sin guard hace MORIR el arnes bajo el mutante y deja las afirmaciones de abajo sin ejecutar: el mutante parece matar menos de lo que mata.
metadata:
  type: feedback
---

Cuando se verifica un fix **por mutacion**, toda afirmacion del arnes tiene que poder evaluarse en el
mundo CON el defecto. Si indexa (`comprobantes[1]`), desreferencia o castea algo que el mutante hace
desaparecer, el arnes **muere con una excepcion** en vez de reportar `FALLA`, y **todas las
afirmaciones de mas abajo quedan sin ejecutar**: el mapa de mutacion sale falseado a la baja y no se
nota, porque la pantalla llena de `FALLA` parece una matanza exitosa.

**Why:** en la-platense LP-040, la afirmacion 8.9 hacia `comprobantes[1].Estado` dentro de un bloque
cuya precondicion el mutante M1 rompia (no emitia ningun comprobante). Primera corrida de M1: 6
afirmaciones FALLADAS y el proceso muerto por `IndexOutOfRange`, sin linea de RESULTADO. Con el guard
(`var nuevo = comprobantes.Count == 2 ? comprobantes[1] : null;`) **el mismo mutante mata 18**. La
diferencia entre "mata 6" y "mata 18" era el reporte entero de la etapa.

**How to apply:** antes de correr los mutantes, releer las afirmaciones nuevas buscando indexaciones y
`!` y preguntarse "¿esto evalua si el codigo no hizo nada?". Dos sintomas de que el arnes murio en vez
de medir: no aparece la linea `=== RESULTADO ===`, o la suma `OK + FALLADAS` no da el total de
afirmaciones. Y un detalle operativo que ya mordio: si el script de mutacion falla, un
`dotnet run --no-build` encadenado con `;` corre **el binario del mutante anterior** y el resultado
parece valido — encadenar con `&&`, o rebuildear siempre.

**Corolario sobre que mutantes correr:** hace falta uno por cada propiedad que se afirma, no uno por
defecto. En LP-040 el mutante obvio (restaurar el metodo viejo) no mataba las afirmaciones sobre las
columnas obsoletas ni sobre el cargo de IVA, porque con la integracion externa apagada ese codigo
tampoco escribia nada. Hubo que escribir un mutante por propiedad (M3: volver a escribir las columnas;
M5: postear el cargo sin que nadie lo vea) para que esas afirmaciones demostraran tener dientes. Y las
que sobreviven a todos los mutantes se **declaran** como precondicion o como control de daño colateral
en el reporte, nunca se cuentan como cobertura.

Relacionado: [[sonda-ef-desechable]] (como ejecutar de verdad sin levantar la app) y
[[verificar-criterios-contra-produccion]].

## Tercera forma, medida el 2026-10-07: el mutante que vuelve EXCEPCIONAL un `return` limpio

Dos mutantes del modulo 16 no fallaron la afirmacion: **mataron al arnes**. `M8` (apagar la guarda de
"ya es una nota de credito") dejaba seguir la emision, que moria mas adelante; `M12` (adelantar el
commit) hacia que el commit final tirara *"transaction has already been committed"*. Los dos
terminaban en exit 3 y se llevaban puestas todas las afirmaciones de abajo.

**La salida es un `try/catch` alrededor de la llamada al Service que convierta la excepcion en un
rechazo.** No es prolijidad: es lo que separa *"esta afirmacion fallo"* de *"el arnes dejo de medir"*.
Para lo que el arnes afirma (que no se escriba) una excepcion es un resultado valido.

**Y el primo que aparece del lado del ARNES, no del codigo:** toda cuenta previa del arnes tiene que
sobrevivir a los datos que el arnes manda **a proposito para que el codigo los rechace**. El arnes
pedia acreditar un item que ese comprobante no facturo (afirmacion deliberada de rechazo) y un
`First` sin guard en el calculo previo lo mataba **antes** de que el Service pudiera rechazarlo.
`FirstOrDefault` + descarte.

**Corolario sobre la limpieza del arnes bajo mutacion:** un mutante puede fabricar estados
IMPOSIBLES que la limpieza no previo. `M8` creo una nota de credito **de** una nota de credito, y la
limpieza —que borraba las NC en una pasada antes de las facturas— murio por FK. La limpieza tiene que
borrar en BUCLE de las hojas a la raiz, o el mapa de mutacion se pierde por el final.

Ver tambien [[mutante-del-importe-y-el-eco-de-ui]].
