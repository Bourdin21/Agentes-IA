---
name: clon-de-prod-y-el-token-que-viaja-en-user-secrets
description: Cuando los criterios de aceptacion son conteos de produccion, la unica base de Development util es un clon de prod — y levantar la app sobre ese clon arma la trampa de que user-secrets trae el token real del canal de envio
metadata:
  type: project
---

Cuando los criterios a verificar son **numeros de produccion** ("la cola da 270, 50 excluidos"), una base de
desarrollo con datos de juguete no sirve de oraculo y correr contra produccion no esta autorizado. El unico
camino que cierra: **clonar prod a una base local** (solo `SHOW CREATE TABLE` + `SELECT` del lado de prod, con
`rollback()`), levantar la app en `Development` con `ConnectionStrings__DefaultConnection` pisado por variable
de entorno, y dejar el repo intacto. En crm-olvidata son 33 tablas / ~25k filas / ~13 MB: menos de un minuto.

Dos detalles que lo rompen la primera vez:

- **Columnas generadas.** `INSERT ... VALUES` con todas las columnas falla con error 3105. Hay que armar la
  lista de columnas desde `information_schema.columns` descartando las que tienen `GENERATED` en `extra`.
- **Los usuarios no se copian.** Omitir las filas de `AspNetUsers`/`AspNetUserRoles` y dejar que el seeder de
  la app cree el SuperUsuario con la password de `appsettings`. Para probar autorizacion por rol, insertar un
  segundo usuario en el clon copiando la fila del seeder y cambiandole `Id`/`Email`/`SecurityStamp`: el hash de
  password se reusa, asi que entra con la misma clave.

**LA TRAMPA, y es de las caras:** `dotnet user-secrets` del proyecto Web tiene el **AccessToken real de
WhatsApp** (y la API key de Maps), y `dotnet run` en Development lo carga. Si la app arranca sobre el clon de
prod con ese token vivo, los hosted services de envio corren contra contactos reales. Antes de levantar, en
este orden:

1. `Olvidata_WhatsApp__AccessToken=QA_TOKEN_INVALIDO_NO_ENVIAR` por variable de entorno (gana sobre
   user-secrets; `appsettings.Secrets.json` se carga **despues** de las env vars, asi que verificar que no
   tenga la clave que estas pisando — hoy solo tiene `Anthropic:ApiKey`).
2. En el clon: `OutboundPausado=1`, `AvisoRenovacionHabilitado=0`, `BusquedaMapsPausada=1`,
   `ConversacionIaPausada=1`. Los schedulers quedan inertes sin tocar una linea de codigo.
3. Oraculo de "cero envios": contar `ContactoRespuestas` antes y despues de cada POST. Si no se movio, no
   salio nada.

**El tope de gasto es el mejor arnes para probar el camino pagado sin pagar.** Poner
`PresupuestoMensualArs=0.01` en el clon y recien entonces mandar el POST con la plantilla **permitida**: el
chequeo de tope corta antes de la red, asi que se observa el camino feliz completo hasta el borde del envio y
el conteo de respuestas no se mueve. Es la unica forma de darle PASS a "el tope se consulta por este camino"
con evidencia de comportamiento en vez de lectura de codigo.

**Para probar una rama que los datos reales no tienen** (ej. "0 contactos con la ventana de 24 h abierta"):
insertar en el clon la fila minima que la abre —un entrante sintetico con fecha reciente—, verificar que el
servidor cambia de rama, y borrarla. Marcar la fila con un texto reconocible (`ARNES QA - ...`) para poder
borrarla por `WHERE` y para que el conteo final lo demuestre.

Ver tambien [[project_metodo_qa_datos_reales]], [[entorno-sin-navegador]] y
[[feedback-arnes-miente-primero]] — el filtro que parecia no persistir en Session resulto estar restaurado
por JS y no por el atributo `selected` del HTML: el arnes miraba el oraculo equivocado.
