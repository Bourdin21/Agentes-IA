---
name: verificador-de-perimetro-y-su-calibracion
description: Cuando se escribe una verificacion ejecutable que enumera un perimetro (los sitios que escriben plata, los que tocan stock), hay que calibrarla exigiendo que encuentre PRIMERO los sitios que ya sabemos que faltan; si no los ve, no sirve para los que no sabemos.
metadata:
  type: feedback
---

Cuando una decision pide reemplazar una lista mantenida a mano por **una verificacion ejecutable que
enumera un perimetro** (los POST que escriben plata, los Services que tocan stock, los que postean en
caja), la verificacion no esta lista cuando corre: esta lista cuando **encuentra los sitios que ya
sabiamos que faltaban**. Ese es el unico calibre disponible, y hay que usarlo antes de creerle
cualquier numero.

**Why:** en la-platense, el verificador de cobertura del token de submit dio en su primera corrida un
perimetro de **10 POST** y se veia razonable. Faltaban dos sitios que ya tenian parte de defecto
(`Devoluciones/Registrar` y `NotasCredito/Emitir`), por dos causas distintas y las dos invisibles
leyendo el codigo del verificador:

1. **Analisis de un solo nivel.** El Controller llamaba a un Service que **delegaba** la escritura en
   otro Service. Arreglo: cierre transitivo sobre el grafo de llamadas entre Services (campos
   `private readonly IXxx _x;` → clase `Xxx`).
2. **Escaneo de metodos publicos solamente.** El Service estaba partido en cascara y nucleo, y el
   `new ComprobanteAfip` vivia en el **nucleo privado**. Arreglo: escanear todos los metodos y agregar
   las aristas intra-clase.

Con las dos correcciones el perimetro paso de 10 a **23 POST** — y el numero real era casi el doble de
los 13 sitios que tres rondas de QA habian medido a mano. El falso negativo es el unico error que una
verificacion asi no puede permitirse, porque es exactamente la forma de falla de la lista a mano que
viene a reemplazar.

**Y el error mas caro de todos, que es el que repiti: NO PONER UNA LISTA A MANO DENTRO DEL
INSTRUMENTO QUE PROTEGE CONTRA LAS LISTAS A MANO.** Mi detector enumeraba 7 nombres de entidad y una
sola forma de escritura, asi que una entidad no listada (`new CierreCajaDiario`) y una escritura por
SQL crudo salian **exit 0**. Es la forma exacta del defecto que el programa existia para prevenir, y
la peor version, porque sale en verde. El arreglo no es agregar los nombres que faltan: es **derivar
el criterio del dato** — en este caso, "una entidad es de dinero si declara una propiedad `decimal`",
leido del proyecto Domain en cada corrida. Si hay una forma de escritura que el detector **no puede**
clasificar (SQL crudo, reflexion), que entre al perimetro por las dudas y **se declare ruidosa**; lo
que no puede pasar es que salga 0.

**How to apply:**

- Antes de reportar un perimetro, pasarle la lista de sitios ya conocidos y exigir que aparezcan
  todos. Si falta uno, el verificador esta roto, no el repo.
- Imprimir el **conteo** de lo enumerado como parte del resultado: si el numero baja de golpe en una
  corrida futura, el patron dejo de matchear. Y abortar con error si el conteo da cero — "cero
  escritores de plata" es un fallo del verificador, no un repo limpio.
- Detectar la escritura por `new Entidad` y no por `.Add(...)`: el `new` es donde la fila se
  construye y no se puede escribir de otra forma.
- Las excepciones declaradas llevan **motivo + id de defecto**, y hay que denunciar tambien las
  **excepciones muertas** (las que ya no corresponden a ningun sitio): una lista de permitidos que
  acumula entradas viejas vuelve a ser el comentario que nadie ejecuta.
- Separar las excepciones en grupos por lo que se sabe de cada una, y para las que nadie evaluo
  escribir **"SIN EVALUAR"** y no "esta bien": ni roto ni bien es la unica afirmacion sostenible, y es
  informacion que el que sigue necesita.
- Probar que la verificacion **falla**: quitarle la cobertura a un sitio cubierto y confirmar exit 1.
  Una verificacion que nunca se vio en rojo no es una mitigacion.
- **Un chequeo que puede quedar inerte no debe imprimir su afirmacion.** El mio buscaba un artefacto
  (el Razor compilado) que solo existe tras un build especial: en un build normal no medía nada y el
  programa igual imprimia "el cableado esta bien" — un verde falso en el unico chequeo del modo de
  falla total. O el chequeo **se produce su propia evidencia** (lanzar el build desde el verificador,
  a un directorio temporal), o no imprime nada y la corrida sale con un exit distinto. Las dos son
  honestas; la combinacion no.
- Imprimir en la ultima linea qué significa el verde y qué no. Un verde con 1 cubierto y 22 declarados
  se lee como "esto esta resuelto" si no lo dice.
