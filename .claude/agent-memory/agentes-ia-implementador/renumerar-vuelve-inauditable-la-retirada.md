---
name: renumerar-vuelve-inauditable-la-retirada
description: Al reescribir una familia de afirmaciones, las nuevas van con numeros NUEVOS: si se renumera, los mismos ids existen en las dos versiones con sentidos distintos y una auditoria por id no puede distinguir "retirada" de "renumerada".
metadata:
  type: feedback
---

Cuando una familia de afirmaciones de un arnes **se reescribe** porque lo que medía dejo de existir,
las afirmaciones nuevas van con **numeros nuevos**, aunque queden con huecos y aunque la numeracion
pierda prolijidad. Nunca se reusa un numero viejo para un sentido nuevo.

**Why:** en la-platense (fase 1 del token de submit) reescribi la familia 9 del arnes de CR-02 y
renumere desde `9.1`. Resultado: `9.3`–`9.7` y `9.9` **existian en las dos versiones con sentidos
distintos**. Cuando QA fue a auditar mis 15 retiradas declaradas, **una auditoria por id era
imposible** —no podia distinguir "esta retirada" de "esta renumerada"— y tuvo que hacerla **por
texto**, afirmacion por afirmacion. Encontro que **una de las 15 estaba mal clasificada**: la vieja
`9.10` no medía el mecanismo retirado, medía que dos tandas de cantidades distintas **SUMARAN** la
cantidad exacta, y la nueva que la "reemplazaba" solo medía que las dos **entraran**. Un bug que
acepte las dos y sume mal pasaba en verde.

**How to apply:**

- Al reescribir una familia, numerar las nuevas **despues** del maximo viejo (si la vieja llegaba a
  `9.22`, arrancar en `9.23`), o restaurar una afirmacion perdida **al final y con numero nuevo** en
  vez de intercalarla.
- Al declarar retiradas, listar cada una **con su texto**, no solo con su id: el texto es lo unico que
  sobrevive a una renumeracion y es lo que hace la lista auditable.
- Y revisar cada retirada preguntando **"¿que medía esto, aparte del mecanismo que saque?"**. Una
  afirmacion puede estar en una familia por historia y medir otra cosa; esa otra cosa es la que se
  pierde en silencio. El filtro es: si la afirmacion seguiria siendo VERDADERA y UTIL con el mecanismo
  retirado, no era del mecanismo — hay que conservarla.
- Conviene tenerlo presente desde antes de reescribir: la renumeracion no es cosmetica, es lo que
  decide si alguien puede auditar el cambio despues. Relacionado:
  [[verificador-de-perimetro-y-su-calibracion]].
