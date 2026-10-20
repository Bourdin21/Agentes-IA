# Pipeline
> **Archivo generado — no editarlo a mano.** Lo regenera `python scripts/olvidata_datos.py pipeline` leyendo el CRM productivo.
> Snapshot del 2026-10-20. Lo que el CRM no sabe se edita en `datos-manuales.yml`.

## El embudo, por etapa

| Etapa | Contactos | Cotizado USD |
|---|---:|---:|
| Pendiente | 3657 | — |
| Mensaje enviado | 799 | — |
| Follow-up enviado | 32 | — |
| Respondio | 305 | — |
| Presupuesto enviado | 16 | — |
| Cerrado | 16 | — |
| Frio | 4516 | — |
| Descartado | 892 | — |
| Derivado manual | 7 | — |
| **Total** | **10.240** | |

## Conversión del embudo

| Paso | Cantidad | Tasa |
|---|---:|---:|
| Contactados (mensaje o más) | 5.691 | — |
| Respondieron | 344 | 6.0% |
| Con presupuesto enviado | 32 | 9.3% de los que respondieron |
| Cerrados | 16 | 50.0% de los presupuestados |

> La tasa demo → cierre no sale de acá: el CRM registra el presupuesto enviado, no la demo. Hasta que exista ese dato, se anota a mano en `metricas.md`.

## Leads abiertos

Entran los que tuvieron actividad en los últimos 30 días, más todos los que tienen presupuesto enviado o están derivados a mano (esos van sin importar la fecha).

| Negocio | Contacto | Rubro | Zona | Canal | Frente (por gancho) | Etapa | Cotizado USD | Última actividad |
|---|---|---|---|---|---|---|---:|---|
| El Showroom de la Cris | Equipo | Indumentaria o calzado | La Plata | Outbound frio | Landing | Respondio | — | 2026-10-20 |
| — | — | — | — | Ads pagos | — *sin gancho* | Respondio | — | 2026-10-20 |
| — | Esteban | Comercio o alquiler de maquinaria | — | Ads pagos | — *sin gancho* | Derivado manual | — | 2026-10-20 |
| Importadora jorge | Equipo | Comercios de venta por peso o unidad | CABA | Outbound frio | Build | Derivado manual | — | 2026-10-20 |
| — | Arreglotodo | Servicios urbanos o técnicos | — | Ads pagos | — *sin gancho* | Derivado manual | — | 2026-10-17 |
| — | ɴᴜʟʟ | — | — | Instagram organico | — *sin gancho* | Respondio | — | 2026-10-17 |
| — | Andrea Puglisi | — | — | Instagram organico | — *sin gancho* | Respondio | — | 2026-10-16 |
| Departamento Southern Living | Equipo | Inmuebles / Real estate | Bariloche | Outbound frio | — *sin gancho* | Presupuesto enviado | — | 2026-10-16 |
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

**Dormidos:** otros 288 leads siguen en etapa abierta pero sin actividad en más de 30 días (288 en Respondio; el más reciente movió el 2026-09-18). No se listan uno por uno a propósito — son decisión de reactivar o marcar fríos, no seguimiento. Para verlos: el CRM.
