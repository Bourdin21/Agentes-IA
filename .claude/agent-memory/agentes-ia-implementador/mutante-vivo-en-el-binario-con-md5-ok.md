---
name: mutante-vivo-en-el-binario-con-md5-ok
description: Restaurar un mutante desde el backup con shutil.copy2 preserva el mtime, MSBuild no recompila y el mutante sigue vivo en la DLL mientras el control de md5 contra el backup PASA; mas las otras dos formas de medir el binario equivocado.
metadata:
  type: feedback
---

Al medir por mutacion, el control de integridad que el proyecto pide —`md5` del fuente contra el
backup despues de restaurar— **puede pasar con el mutante todavia vivo en el binario**. Es la unica
trampa de esta familia que la verificacion recomendada no atrapa, porque el md5 es correcto: lo que
esta mal no es el fuente, es la DLL.

**Why:** `shutil.copy2` (y `cp -p`) **preserva el mtime del backup**, asi que el archivo restaurado
queda *mas viejo* que la DLL compilada con la mutacion. MSBuild compara timestamps, lo ve "al dia" y
**no recompila**. En la-platense (fase 1 del token de submit) eso contamino una corrida de 10
mutantes: `M10` quedo vivo tres corridas despues de "restaurado", y se destapo solo porque el control
negativo empezo a fallar en verde-limpio con el mensaje `"MUTANTE: clave natural de vuelta"` impreso
por el propio mutante. Peor: contamina **en una sola direccion** y eso lo hace parecer intermitente —
si el mutante siguiente toca Infrastructure, Web se recompila sola (la referencia de proyecto fuerza
su rebuild) y el mutante de Web "se cura"; al reves no pasa. El sintoma es un mutante que tumba
afirmaciones que no deberia tocar, en familias que no tienen nada que ver.

**How to apply:** en el script de mutacion, `os.utime(archivo, None)` despues de copiar el backup, y
correr todos los builds de la corrida con `--no-incremental`. El `md5` se sigue haciendo, pero ya no
alcanza como prueba: la prueba es que la corrida limpia reproduzca su linea base EXACTA despues de la
restauracion. Si un mutante tumba algo de otra familia, sospechar contaminacion antes que un
descubrimiento.

**Las otras dos formas de medir el binario equivocado, que mordieron en la misma ronda:**

1. **El arnes que no compila y corre el EXE anterior.** `tools/` no esta en la solucion, asi que
   `dotnet build` de la solucion no lo toca. Al borrar una constante que el arnes referenciaba, su
   build fallo y `dotnet run --no-build` corrio el binario viejo: la corrida salio **111/0 sobre el
   codigo viejo**, con los mensajes de la guarda ya borrada en el log como unica pista. **Hay que
   mirar el RESULTADO del build (contar `: error `), no su "Tiempo transcurrido".** Ver tambien
   [[arnes-que-muere-en-vez-de-medir]].
2. **Un mutante que no mata nada puede haber corrido contra el instrumento equivocado.** `M15` (quitar
   el lock de `PAT-059`) dio "0 falladas" y parecia probar que la afirmacion era vacia. No lo era: el
   script lo habia corrido contra el otro arnes —donde ese mutante efectivamente no cambia nada—
   porque un `&&` corto-circuitado dejo sin aplicar el parche que agregaba la rama. Contra el arnes
   correcto tumba la afirmacion con el numero exacto del defecto original. **A un mutante que no mata
   nada hay que creerle solo despues de verificar contra que instrumento corrio.**
