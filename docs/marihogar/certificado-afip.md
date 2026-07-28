# Certificado Digital AFIP/ARCA — MariHogar

Guía paso a paso para tramitar el certificado `.p12` necesario para el módulo de Facturación
electrónica (M7, `AfipService.cs`). Mismo procedimiento ya usado en `delicias-naturales`
(ver `../delicias-naturales/certificado-afip.md` y el template genérico en
`../templates/afip-certificado-digital.md`), adaptado a MariHogar.

**Estado: Certificado de PRODUCCIÓN completo, conectado a `appsettings.Production.json` y
VERIFICADO con un login real contra el WSAA de AFIP (2026-07-28) — AFIP devolvió token/sign
válidos, confirmando que el certificado y la relación de servicio WSFE funcionan de punta a
punta. Falta únicamente: subir `marihogarprod.p12` al servidor real (paso manual, se hace en la
próxima ventana de deploy) y, opcionalmente, repetir el trámite en el portal de Homologación si
se quiere probar sin facturar en real.**

---

## Datos completados

| Campo | Valor |
|---|---|
| CUIT del negocio | `20331136132` (20-33113613-2) — confirmado por el cliente 2026-07-28 |
| Alias del certificado | `marihogar` |
| DN del certificado emitido | `CN=marihogar, serialNumber=CUIT 20331136132` (emisor: AFIP, `Not Before: 28/07/2026`, `Not After: 27/07/2028`) |
| Password del .p12 | `Olvidata2026!` (elegida por el cliente 2026-07-28 — también está en `appsettings.Production.json`, gitignored) |
| Ambiente | **Producción** (el trámite se hizo en el portal de Producción de AFIP, no en Homologación — este certificado NO sirve para probar contra el ambiente de homologación) |
| Punto de Venta configurado | `1` (valor por defecto ya cargado — **no confirmado explícitamente con el cliente**, verificar antes de emitir el primer comprobante real) |
| Ruta local | `C:\Sistemas\marihogar\Certificados\marihogarprod.p12` |
| Ruta configurada en `appsettings.Production.json` | `Certificados/marihogarprod.p12` (relativa a la raíz del sitio en el servidor — **falta subir el archivo ahí manualmente, ver Paso 5**) |

**Archivos generados** (en `C:\Sistemas\marihogar\Certificados\`, excluidos de git):
- `privada.key` — clave privada, nunca se comparte.
- `pedido.csr` — el CSR ya subido a AFIP.
- `certificado.crt` — descargado desde el portal de AFIP el 2026-07-28.
- `marihogarprod.p12` — certificado final, listo para usar.

---

## Paso 0 — Qué necesitás tener antes de empezar

1. **Clave Fiscal del CUIT del negocio, con Nivel de Seguridad 3** (la 2 no alcanza para adherir servicios web). Si el cliente no la tiene, hay que generarla antes en cualquier oficina de AFIP con DNI, o vía la app "Mi AFIP" con reconocimiento facial.
2. Saber si quien va a hacer el trámite es el **titular del CUIT** o una **persona autorizada** (relación fiscal / apoderado) — cambia un paso en el Paso 2.
3. OpenSSL instalado. En esta máquina ya está disponible como parte de Git for Windows, en `C:\Program Files\Git\usr\bin\openssl.exe` — no hace falta instalar nada aparte (alternativa: bajarlo de https://slproweb.com/products/Win32OpenSSL.html a `C:\openssl\` si se prefiere una instalación standalone).

---

## Paso 1 — Generar la clave privada y el CSR (en esta máquina)

Abrir una terminal (PowerShell o Git Bash) y ejecutar, reemplazando `{CUIT_DEL_NEGOCIO}` por el CUIT real (sin guiones, 11 dígitos) y `{alias}` por el alias elegido en minúsculas (sin espacios, ej. `marihogar`):

```bash
mkdir -p /c/Sistemas/marihogar/Certificados
OPENSSL="/c/Program Files/Git/usr/bin/openssl.exe"

# 1. Clave privada — GUARDAR EN LUGAR SEGURO, si se pierde hay que rehacer todo el trámite
"$OPENSSL" genrsa -out /c/Sistemas/marihogar/Certificados/privada.key 2048

# 2. Pedido CSR — el -subj tiene que coincidir con lo que exige AFIP (ver Paso 2 para el
#    formato exacto una vez que estés parado en la pantalla de "Crear DN y certificado")
"$OPENSSL" req -new -key /c/Sistemas/marihogar/Certificados/privada.key \
  -subj "/C=AR/O={alias}/CN={alias}/serialNumber=CUIT {CUIT_DEL_NEGOCIO}" \
  -out /c/Sistemas/marihogar/Certificados/pedido.csr

# 3. Verificar que el Subject haya quedado como se espera
"$OPENSSL" req -text -noout -in /c/Sistemas/marihogar/Certificados/pedido.csr | grep "Subject:"
```

Esto genera 2 archivos en `C:\Sistemas\marihogar\Certificados\`: `privada.key` (nunca se sube a
ningún lado, ni a AFIP ni a git) y `pedido.csr` (este sí se sube a AFIP en el paso siguiente).

---

## Paso 2 — Trámite en el navegador, en el portal de AFIP (manual, con el cliente)

Necesitás la Clave Fiscal del CUIT del negocio (nivel de seguridad 3).

1. Entrar a **https://auth.afip.gob.ar/contribuyente_/login.xhtml** e iniciar sesión con CUIT + Clave Fiscal.
2. En el buscador de servicios ("Todos los trámites" o el buscador de arriba), escribir **"Administración de Certificados Digitales"** y entrar al servicio.
3. Si el que está haciendo el trámite es una **persona autorizada** (no el titular del CUIT), el sistema pregunta a nombre de quién ver los certificados — elegir la opción de la **persona autorizante** (el negocio/CUIT titular), no la del autorizado.
4. Dentro de "Administración de Certificados Digitales", buscar la opción **"Solicitar" / "Nuevo certificado" / "Crear DN y certificado"** (el nombre exacto varía un poco según la versión del portal, pero siempre está en esa pantalla principal de administración).
5. Va a pedir un **alias** para identificar el certificado — usar el alias elegido en el Paso 1 (ej. `marihogar`).
6. Va a pedir pegar el **CSR**. Abrir `pedido.csr` con el Bloc de notas (`notepad C:\Sistemas\marihogar\Certificados\pedido.csr`), copiar **todo el contenido incluyendo las líneas `-----BEGIN CERTIFICATE REQUEST-----` y `-----END CERTIFICATE REQUEST-----`**, y pegarlo en el campo correspondiente.
7. Confirmar. AFIP genera el certificado y lo deja disponible para descargar — descargarlo (queda como archivo `.crt` o `.pem`, puede tener un nombre genérico). Guardarlo como `C:\Sistemas\marihogar\Certificados\certificado.crt`.
8. Dentro del detalle de ese mismo certificado ya creado, hay una opción para **asignar servicios web (Web Services)** — ahí hay que sumar:
   - `wsfe` (Facturación electrónica — WSFEv1, el que usa este sistema)
   - Opcionalmente `ws_sr_padron_a5` (consulta de padrón/constancia de inscripción), si en algún momento se quiere validar CUIT de clientes automáticamente — no es requisito para emitir facturas.
9. **Importante — Homologación vs Producción son trámites separados**: todo lo anterior (pasos 1 a 8) corresponde al ambiente de **Producción** de AFIP. Para poder probar sin emitir comprobantes reales primero, hay que repetir el mismo trámite en el ambiente de **Homologación** de AFIP: **https://wsass-homo.afip.gob.ar/wsass/portal/login.xhtml** (credenciales de Clave Fiscal son las mismas). El certificado de Homologación es independiente del de Producción — se genera un CSR distinto (o se puede reusar la misma `privada.key`, ver nota abajo) y se sube ahí. `AfipSettings.Ambiente=Homologacion` en `appsettings.Development.json` es el que ya está configurado por defecto en este proyecto para probar sin arriesgar timbrado real.

---

## Paso 3 — Generar el archivo `.p12` (en esta máquina, después de tener el `.crt` de AFIP)

```bash
OPENSSL="/c/Program Files/Git/usr/bin/openssl.exe"

# Verificar que el .crt descargado es válido y corresponde al CUIT esperado
"$OPENSSL" x509 -text -noout -in /c/Sistemas/marihogar/Certificados/certificado.crt | grep -E "Subject:|Not Before|Not After"

# Generar el .p12 — va a pedir una password de exportación, elegirla ahora (no reutilizar
# la de otros proyectos del estudio) y anotarla en un lugar seguro (gestor de contraseñas)
"$OPENSSL" pkcs12 -export \
  -inkey /c/Sistemas/marihogar/Certificados/privada.key \
  -in /c/Sistemas/marihogar/Certificados/certificado.crt \
  -out /c/Sistemas/marihogar/Certificados/marihogar.p12

# Verificar que el .p12 quedó bien formado (pide la password recién elegida)
"$OPENSSL" pkcs12 -in /c/Sistemas/marihogar/Certificados/marihogar.p12 -noout
```

Si se hizo el trámite tanto en Homologación como en Producción (Paso 2, punto 9), repetir este
paso con el `.crt` de cada ambiente, generando `marihogarhml.p12` y `marihogarprod.p12` por
separado (mismo `privada.key` sirve para ambos si se usó la misma clave para los 2 CSR).

---

## Paso 4 — Conectarlo con la aplicación ✅ hecho (2026-07-28)

`MariHogar.Web/appsettings.Production.json` ya tiene la sección `Afip` cargada:

```json
"Afip": {
  "Ambiente": "Produccion",
  "CertificadoPath": "Certificados/marihogarprod.p12",
  "CertificadoPassword": "Olvidata2026!",
  "CUIT": "20331136132",
  "PuntoVenta": 1,
  "PorcentajeIva": 21
}
```

`CertificadoPath` es **relativo a la raíz del sitio** (`ContentRootPath`) — no una ruta
absoluta del servidor, para no depender de la estructura exacta de carpetas del hosting.

---

## Paso 5 — Subir el .p12 al servidor (manual, pendiente)

`appsettings.Production.json` ya apunta a `Certificados/marihogarprod.p12`, pero ese archivo
todavía no está en el servidor — falta:

1. Vía FTP/File Manager de SmarterASP (mismas credenciales del hosting ya usadas en
   `scripts/deploy-prod.ps1`), crear la carpeta `Certificados/` en la raíz del sitio
   `olvidatasoft-002-site16` (mismo nivel que `MariHogar.Web.dll`).
2. Subir `C:\Sistemas\marihogar\Certificados\marihogarprod.p12` ahí.
3. Confirmar que `appsettings.Production.json` (con la sección `Afip` ya cargada) esté
   incluido en el próximo deploy — es un archivo gitignored, así que no viaja con el `dotnet
   publish` normal del código: verificar que el paso de publish/deploy lo copie igual (mismo
   tratamiento que ya se le da a la connection string real de producción, que vive en el mismo
   archivo).

No hace falta un deploy de código para esto — es exclusivamente subir el archivo del
certificado y confirmar el `appsettings.Production.json` ya actualizado.

---

## Notas generales

- El par `privada.key` + `certificado.crt` de cada ambiente genera su `.p12` correspondiente — no mezclar el `.crt` de Homologación con el de Producción.
- Los certificados AFIP vencen a los **2 años** — anotar la fecha de vencimiento acá una vez emitido, para renovarlo a tiempo (mismo criterio que se lleva en `delicias-naturales/certificado-afip.md`).
- `privada.key` nunca se sube a AFIP ni se comparte — solo `pedido.csr` (que no es secreto) sale de esta máquina.
- Los archivos intermedios (`privada.key`, `pedido.csr`, `certificado.crt`) pueden quedar en `C:\Sistemas\marihogar\Certificados\` una vez que el `.p12` está generado y verificado — están excluidos de git.

## Historial de renovaciones

| Fecha | Ambiente | Vencimiento | Realizado por |
|---|---|---|---|
| 28/07/2026 | Producción | 27/07/2028 | Claude Code (orquestador, con el cliente completando el trámite manual en el portal de AFIP) |
