---
name: medir-un-gate-de-instrumento
description: Como se mide un verificador/gate que el implementador escribio para medirse a si mismo (agregarle trabajo nuevo, mutacion semanticamente nula, mutante de la REUBICACION), mas las cinco trampas de oraculo que ya publicaron un verde falso en esa clase de corrida
metadata:
  type: project
---

Cuando el entregable a probar es un **instrumento** (un verificador de cobertura, un gate, un
detector de perimetro), leerlo no sirve y correrlo tampoco: hay que **darle trabajo nuevo** y ver si
lo encuentra.

**1. El mutante del TRABAJO NUEVO, escrito en el estilo del repo y sin declararlo en ninguna parte.**
Si el instrumento dice "detecto X por una propiedad del dato", se le siembra una X nueva (entidad
nueva + Service nuevo + POST nuevo, en una copia del arbol) y se mide si falla. Lo decisivo es
escribirlo **como lo escribiria un dev normal**, no como el detector lo espera: ahi aparecen los
falsos negativos. En el gate del token de La Platense (2026-10-09) el detector encontro el caso
canonico, y las dos variantes que un dev tambien escribiria no: una clase de Service que **comparte
archivo** con otra (la clave del registro sale de `Path.GetFileNameWithoutExtension`, asi que el
POST queda invisible) y un POST que escribe la entidad **directo desde el Controller**. Son `LP-129`
y `LP-130`.

**2. El mutante de la REUBICACION, que es una familia aparte.** Mover codigo **sin cambiarlo** (una
clase a otro archivo, un metodo a otra carpeta) rompe a cualquier analizador de texto que use el
nombre del archivo o la carpeta como nombre de simbolo. Aisla la causa en una medicion: con las dos
clases en un archivo el perimetro salio 36 y el POST no estaba; partiendo la clase a su propio
archivo, **sin tocar una linea**, salio 37 y el POST aparecio.

**3. Para probar una guarda de "si la derivacion da 0, aborta", la mutacion tiene que ser
SEMANTICAMENTE NULA.** Reemplazar `public decimal` por `public Decimal` en las 27 entidades: el
dominio sigue lleno de plata, **el proyecto compila con 0 errores**, y solo deja de matchear el
regex del detector — que es exactamente el modo de falla que la guarda dice atrapar. Si en cambio se
borran las entidades, se prueba otra cosa (un dominio vacio) y la guarda queda sin medir.

**4. Para probar "no imprime un verde que no midio", se rompe su capacidad de producir evidencia, no
su entrada.** El verificador se compila su propio Razor; agregarle una linea que no compila al Web
lo deja sin evidencia y hay que confirmar **las dos cosas**: exit 3 **y** que la afirmacion no se
imprimio. Al restaurar, no preservar el mtime (ver instruccion 33).

Las cinco trampas de oraculo de esta clase de corrida, todas medidas:

- **Una huella/token atado a una RUTA esta atado al PATH, route values incluidos.** El form de
  `/FacturacionParcial/Emitir/1` emite la huella de `/facturacionparcial/emitir/1`; postear a
  `/FacturacionParcial/Emitir` (sin el id) lo rechaza **con razon**, y eso **invalida el par
  discriminante**: el control positivo tambien cae y el resultado se lee como "rechaza todo" (el
  mutante M21). El par se postea **a la URL que el `action` del form declara**, leida del DOM.
- **Los perdedores de una prueba de concurrencia necesitan COOKIE JAR PROPIA.** `TempData` es por
  sesion: con una sola jar, el cartel del perdedor se pierde o lo pisa el ganador, y la pregunta
  "¿que ve el operador?" queda sin respuesta. Cuatro logins independientes + `curl -L` por hilo (asi
  cada uno sigue su propio redirect) y recien ahi se lee el mensaje de cada uno.
- **Un cartel de TempData se distingue del `Swal` propio de la pantalla por el `title`.** Tomar el
  primer `icon:` del HTML engancha el dialogo de confirmacion de la vista (`'Sí, cerrar caja'`) y se
  lee como "no dijo nada". Filtrar por `title: 'Error'|'Éxito'|'Atención'`.
- **`group_concat` trunca en 1.024 bytes: una huella de tabla entera MIENTE.** Para 112k filas,
  `bit_xor(crc32(concat(Id,':',Campo)))` — independiente del orden y sensible a una sola fila.
- **Toda afirmacion de idempotencia necesita el control de que la PRIMERA pasada hizo algo.** Mi
  primer 6a dio "idempotente: True" con los dos aplicar rechazados por un nombre de clave JSON
  equivocado (`generadoEn`, no `previewGeneradoEn`): la linea "los precios cambiaron respecto del
  estado inicial: False" fue lo unico que lo delato.

**Copiar un arbol con cambios SIN COMMITEAR:** `git archive HEAD` no sirve (se pierde el fix) y
`tar` del arbol completo se trae 17 GB de una carpeta ignorada. `tar -cf - --exclude=.git
--exclude=./Migracion --exclude=./publish --exclude=bin --exclude=obj --exclude=keys . | tar -xf -
-C /c/qaXX` deja 21 MB en 0,7 s, y la fidelidad se prueba con `md5sum` de los archivos del diff.

Relacionado: [[herramientas-de-la-corrida]], [[metodo-qa-datos-reales]], [[lotes-en-paralelo]].
