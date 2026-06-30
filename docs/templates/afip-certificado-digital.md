# Template: Certificado Digital AFIP (WebServices)

Guía reutilizable para generar y renovar certificados AFIP en proyectos .NET.

---

## Datos a relevar del cliente

Antes de empezar, obtener del portal AFIP (Administración de Certificados Digitales) o del Web.config del proyecto:

| Campo | Dónde encontrarlo |
|---|---|
| CUIT | Portal AFIP / Web.config (`cuitCertificado`) |
| Alias | Portal AFIP / nombre del certificado existente |
| DN completo | Portal AFIP → detalle del certificado → campo DN |
| Password p12 | Web.config (`passwordCertificado`) |
| Ruta certificado | Web.config (`rutaCertificado`) |

---

## Prerrequisitos

OpenSSL disponible en `C:\Program Files\Git\usr\bin\openssl.exe` (viene con Git for Windows).
No es necesario instalar nada adicional.

---

## Paso 1 — Generar clave privada y CSR (automatizable)

```bash
OPENSSL="/c/Program Files/Git/usr/bin/openssl.exe"

# Generar clave privada
"$OPENSSL" genrsa -out /c/openssl/privada.key 2048

# Generar CSR — reemplazar los valores del DN con los del cliente
"$OPENSSL" req -new -key /c/openssl/privada.key \
  -subj "/serialNumber=CUIT {CUIT}/CN={alias_en_minusculas}" \
  -out /c/openssl/pedido.csr

# Verificar que el Subject sea correcto
"$OPENSSL" req -text -noout -in /c/openssl/pedido.csr | grep "Subject:"
```

El DN en el `-subj` debe coincidir exactamente con lo que muestra AFIP en el campo DN del certificado anterior.

---

## Paso 2 — Subir CSR a AFIP (manual)

1. Ingresar al portal AFIP con el CUIT del cliente
2. Ir a **Administración de Certificados Digitales**
3. Si hay una persona autorizante distinta al titular, ir a los certificados de la **persona autorizante**
4. Crear nuevo certificado con el alias del cliente
5. Pegar el contenido completo de `pedido.csr` (incluyendo `-----BEGIN...` y `-----END...`)
6. Asignar los servicios necesarios al nuevo certificado
7. Descargar el `.crt` generado por AFIP y guardarlo como `C:\openssl\certificado.crt`

---

## Paso 3 — Generar archivos .p12 (automatizable)

```bash
OPENSSL="/c/Program Files/Git/usr/bin/openssl.exe"
PASSWORD="{password_del_proyecto}"

# Verificar el CRT descargado
"$OPENSSL" x509 -text -noout -in /c/openssl/certificado.crt | grep -E "Subject:|Not Before|Not After"

# Generar p12 para homologación
"$OPENSSL" pkcs12 -export \
  -inkey /c/openssl/privada.key \
  -in /c/openssl/certificado.crt \
  -out /c/openssl/aliashml.p12 \
  -passout pass:$PASSWORD

# Generar p12 para producción
"$OPENSSL" pkcs12 -export \
  -inkey /c/openssl/privada.key \
  -in /c/openssl/certificado.crt \
  -out /c/openssl/aliasprod.p12 \
  -passout pass:$PASSWORD

# Verificar que los p12 son válidos
"$OPENSSL" pkcs12 -in /c/openssl/aliashml.p12 -passin pass:$PASSWORD -noout
"$OPENSSL" pkcs12 -in /c/openssl/aliasprod.p12 -passin pass:$PASSWORD -noout
```

---

## Paso 4 — Reemplazar en el proyecto (automatizable)

```bash
PROYECTO="/c/Sistemas/{nombre-proyecto}"

cp /c/openssl/aliashml.p12 "$PROYECTO/Certificados/aliashml.p12"
cp /c/openssl/aliasprod.p12 "$PROYECTO/Certificados/aliasprod.p12"
```

Si el proyecto tiene un solo ambiente, el nombre del archivo puede ser distinto (ej. `alias.p12`). Verificar en Web.config el valor de `rutaCertificado`.

---

## Paso 5 — Subir al servidor de producción (manual)

Copiar `aliasprod.p12` al servidor de hosting en la ruta configurada en Web.config de producción.

---

## Notas generales

- El mismo par `privada.key` + `certificado.crt` sirve para generar tanto el .p12 de HML como el de PROD.
- La password del `.p12` debe mantenerse igual a la que estaba en el proyecto, o actualizar todos los Web.config donde esté referenciada.
- Los certificados AFIP tienen vigencia de **2 años**.
- Guardar `privada.key` en lugar seguro — si se pierde hay que generar todo de nuevo.
- Los archivos intermedios (`privada.key`, `pedido.csr`, `certificado.crt`) quedan en `C:\openssl\` y pueden borrarse una vez que los `.p12` están en el proyecto y verificados.
