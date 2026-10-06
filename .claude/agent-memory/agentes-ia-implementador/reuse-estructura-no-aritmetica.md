---
name: reuse-estructura-no-aritmetica
description: Cuando un brief declara "reuse total" de otro proyecto, lo reutilizable es la estructura; la aritmetica casi nunca se copia y hay que relevarla campo por campo antes de escribir.
metadata:
  type: feedback
---

Un brief que declara **"reuse total"** de otro proyecto del estudio esta hablando de la
**estructura**: la maquina de estados, el flujo de dos pasos, el patron de PDF, los nombres de los
metodos. La **aritmetica** —tipos, precisiones, formulas, que campo es autoridad de que— casi nunca
se copia, porque el modelo de datos del proyecto destino es distinto. Relevarla campo por campo
*antes* de escribir, y escribir en el XML-doc **qué no se pudo copiar y por qué**.

**Why:** en la-platense Entrega 6 los dos modulos venian declarados reuse total de marihogar y el
reuse rindio entero en la estructura. Pero habia que reemplazar cantidad `int` por
`decimal(18,3)`, agregar IVA por linea (marihogar tiene el 21% hardcodeado en dos precios fijos),
cambiar la cascada `base*(1-d)*(1+r)` por la formula no-cascada —que es **el bug que ese mismo
proyecto ya habia corregido**— y meter un gate de precio por rol que en el origen no existe.
Copiar la aritmetica habria reintroducido un defecto cerrado y habria roto los criterios de
aceptacion que pedian numeros exactos. Y en el otro modulo la diferencia *era* el punto de la
entrega: alla el precio de venta se edita a mano, aca es derivado del costo, asi que "aumentar los
precios" son dos operaciones distintas y confundirlas deja el catalogo inconsistente.

**How to apply:** por cada campo del precedente, contestar tres preguntas antes de escribir: (a)
¿existe en el destino con el mismo tipo y la misma precision?; (b) ¿la formula del origen sobrevive
a algun bug que el destino ya corrigio? (buscar en `5-implementador.md` del destino la fecha del
fix, suele estar); (c) ¿el destino tiene una regla de seguridad —gate de rol, dato fiscal que el
cliente no puede imponer— que el origen no tenia? Armar la tabla "que no se pudo copiar y por que"
en el reporte: es lo que convierte un reuse en una decision defendible en vez de un copy-paste.

**Y al revés, que tambien pasa:** a veces el destino ya resolvio algo que el origen tenia que
simular, y entonces el precedente se puede **simplificar**. En el mismo caso, marihogar diferia la
transicion a "convertido" hasta que la venta se confirmara porque alla la venta se crea completa en
una transaccion; en la-platense la venta nace en Borrador, que es justo el carrito precargado que el
origen simulaba, asi que las dos cosas entran en la misma transaccion y el riesgo desaparece.
Declararlo como mejora, no desviarse en silencio.

Relacionado: [[verificar-criterios-contra-produccion]], [[sonda-ef-desechable]].
