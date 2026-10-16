# Pipeline
> **Archivo generado — no editarlo a mano.** Lo regenera `python scripts/olvidata_datos.py pipeline` leyendo el CRM productivo.
> Snapshot del 2026-10-15. Lo que el CRM no sabe se edita en `datos-manuales.yml`.

## El embudo, por etapa

| Etapa | Contactos | Cotizado USD |
|---|---:|---:|
| Pendiente | 3716 | — |
| Mensaje enviado | 833 | — |
| Follow-up enviado | 22 | — |
| Respondio | 301 | — |
| Presupuesto enviado | 16 | — |
| Cerrado | 16 | — |
| Frio | 4442 | — |
| Descartado | 885 | — |
| Derivado manual | 4 | — |
| **Total** | **10.235** | |

## Conversión del embudo

| Paso | Cantidad | Tasa |
|---|---:|---:|
| Contactados (mensaje o más) | 5.634 | — |
| Respondieron | 337 | 6.0% |
| Con presupuesto enviado | 32 | 9.5% de los que respondieron |
| Cerrados | 16 | 50.0% de los presupuestados |

> La tasa demo → cierre no sale de acá: el CRM registra el presupuesto enviado, no la demo. Hasta que exista ese dato, se anota a mano en `metricas.md`.

## Leads abiertos

Entran los que tuvieron actividad en los últimos 30 días, más todos los que tienen presupuesto enviado o están derivados a mano (esos van sin importar la fecha).

| Negocio | Contacto | Rubro | Zona | Canal | Frente (por gancho) | Etapa | Cotizado USD | Última actividad |
|---|---|---|---|---|---|---|---:|---|
| Departamento Southern Living | Equipo | Inmuebles / Real estate | Bariloche | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-10-15 |
| Estudio Caride Sierra - Consultoría | Equipo | estudio-laplata | La Plata | Outbound frio | Build | Respondio | — | 2026-10-15 |
| Farina Balbi | Estudio Jurídico Penal | Equipo | estudio-laplata | La Plata | Outbound frio | Build | Respondio | — | 2026-10-08 |
| — | digiphoto | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-06 |
| — | Santi | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-06 |
| — | Bresso José Luis | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-05 |
| — | Pamplona City Bell | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-03 |
| — | — | — | — | Ads pagos | — *sin gancho* | Derivado manual | — | 2026-10-03 |
| Naturissima | Equipo | Dietéticas y venta de productos | Recoleta | Outbound frio | — *sin gancho* | Respondio | — | 2026-10-03 |
| MACERATA FIAMBRERIA | Equipo | Comercio o alquiler de maquinaria | La Plata | Outbound frio | Landing | Presupuesto enviado | — | 2026-10-02 |
| — | Eneas Lezcaco | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-01 |
| — | Daro | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-30 |
| — | Valentin | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-30 |
| — | stechinaolivio | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-30 |
| Rebolledo Inmobiliaria | Equipo | Inmuebles / Real estate | Neuquén | Outbound frio | Chatbots | Respondio | — | 2026-09-30 |
| — | Esther | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-30 |
| — | Viky | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-18 |
| — | MELLINACHO | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-18 |
| — | Evangelina Di Croce | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-09-17 |
| DEPARTAMENTO Céntrico GALERIAS PACIFICO | Aparts Buenos Aires | ganaderia | Gran La Plata | Outbound frio | — *sin gancho* | Respondio | — | 2026-09-17 |
| Amapola | Amapola | indumentaria | La Plata Calle 12 | Outbound frio | — *sin gancho* | Respondio | — | 2026-09-16 |
| Albert Sport Talles Especiales | Albert Sport | indumentaria | La Plata Calle 12 | Outbound frio | — *sin gancho* | Respondio | — | 2026-09-16 |
| Librería Horizonte | Equipo | Comercio o alquiler de maquinaria | Centro | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-09-15 |
| — | Matias | Servicios urbanos o técnicos | — | Ads pagos | — *sin gancho* | Derivado manual | — | 2026-09-01 |
| TODOLANDIA | Equipo | Comercio o alquiler de maquinaria | Ciudad Vieja | Outbound frio | — *sin gancho* | Derivado manual | — | 2026-08-31 |
| Peras del Olmo | Equipo | Indumentaria o calzado | La Plata | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-27 |
| FABINCO - Soluciones en vestimenta laboral | Equipo | Indumentaria o calzado | Balvanera | Outbound frio | — *sin gancho* | Derivado manual | — | 2026-08-26 |
| DIETETICA MITRE | Equipo | Dietéticas y venta de productos | Mendoza | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-26 |
| DesBorder sin Gluten | Equipo | Dietéticas y venta de productos | Bariloche | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-26 |
| Centro Medico CMA La Plata | Equipo | Salud / Medicina | La Plata | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-21 |
| Estudio Contable Maribel Garcia | Equipo | Contabilidad / Estudios contables | Bariloche | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-20 |
| Consultorios del Lago Bariloche | Equipo | Salud / Medicina | Bariloche | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-20 |
| Coquitos Dietética | Equipo | Dietéticas y venta de productos | Microcentro | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-04 |
| Guanacos Ski Rental | Equipo | Alquiler de equipos de esquí | Esquel | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-01 |
| Yaghan Rental | Equipo | Alquiler de equipos de esquí | Ushuaia | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-01 |
| Mambos Rental Ski & Snowboard | Equipo | Alquiler de equipos de esquí | San Martín de los Andes | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-08-01 |
| Blue Label's Sastrería & Etiqueta | Equipo | Otro rubro | Microcentro | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-07-26 |
| Ferretería La Nueva Tuerca | Equipo | Comercio o alquiler de maquinaria | Melchor Romero | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-07-25 |
| FM reparaciones | franco machuca | Otro rubro | Gran La Plata | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-07-17 |

**Dormidos:** otros 282 leads siguen en etapa abierta pero sin actividad en más de 30 días (282 en Respondio; el más reciente movió el 2026-09-14). No se listan uno por uno a propósito — son decisión de reactivar o marcar fríos, no seguimiento. Para verlos: el CRM.
