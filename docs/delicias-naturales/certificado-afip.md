# Certificado Digital AFIP - Delicias Naturales

## Datos del certificado

| Campo | Valor |
|---|---|
| CUIT | `20119511519` |
| Alias | `DELICIASNAT` |
| DN | `SERIALNUMBER=CUIT 20119511519, CN=deliciasnat` |
| Password p12 | `olvidata123` |
| Ruta HML | `C:\Sistemas\delicias-naturales\Certificados\aliashml.p12` |
| Ruta PROD | `C:\Sistemas\delicias-naturales\Certificados\aliasprod.p12` |
| Ruta PROD servidor | `h:\root\home\olvidatasoft-002\www\deliciasnaturales\Certificados\aliasprod.p12` |

## Historial de renovaciones

| Fecha | Vencimiento | Nro Serie AFIP | Renovado por |
|---|---|---|---|
| 26/06/2026 | 25/06/2028 | (ver portal AFIP) | Claude Code |

## Configuración en Web.config

```xml
<add key="cuitCertificado" value="20119511519" />
<add key="rutaCertificado" value="C:\Sistemas\delicias-naturales\Certificados\aliashml.p12" />
<add key="passwordCertificado" value="olvidata123" />
```

## Servicios AFIP asignados al certificado

- `wsfe` - Facturación electrónica (WSFEv1)
- `wsmtxca` - Facturación con detalle (WSMTXCA)
- `ws_sr_padron_a5` - Constancia de inscripción
- `wsrgiva` - Percepción IVA

## Notas

- El proyecto tiene dos ambientes: HML (homologación) y PROD. El mismo par de archivos privada.key + certificado.crt genera ambos .p12.
- Al renovar, subir `aliasprod.p12` manualmente al servidor de hosting.
- Ver template genérico en `/docs/templates/afip-certificado-digital.md`.
