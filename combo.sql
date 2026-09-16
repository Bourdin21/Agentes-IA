SET NAMES utf8mb4;
INSERT INTO templateswhatsapp (Nombre, Texto, Rubro, Pais, EstadoAprobacionMeta, Activo, CreatedAt) SELECT 'olv_frio_combo_web_v1', 'Hola! Vi tu negocio y pensé: {{2}}.

Soy Joaquín, de Olvidata Soft. Ayudamos a {{1}} como el tuyo armando su página web propia para ordenar {{3}} de una vez por todas.

Básicamente, {{4}}.

Y de paso te muestro el resto del combo: agentes de IA para lo administrativo y un asistente que responde solo las consultas por WhatsApp.

Te sirve?

Un saludo,

Joaquín
Olvidata Soft', NULL, NULL, 3, 1, UTC_TIMESTAMP(6) FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM templateswhatsapp WHERE Nombre='olv_frio_combo_web_v1');
INSERT INTO templateswhatsapp (Nombre, Texto, Rubro, Pais, EstadoAprobacionMeta, Activo, CreatedAt) SELECT 'olv_frio_combo_consultas_v1', 'Hola! Vi tu negocio y pensé: {{2}}.

Soy Joaquín, de Olvidata Soft. Ayudamos a {{1}} como el tuyo con un asistente que se encarga de {{3}} de una vez por todas.

Básicamente, {{4}}.

Y de paso te muestro el resto del combo: tu propia página web y agentes de IA para lo administrativo.

Te sirve?

Un saludo,

Joaquín
Olvidata Soft', NULL, NULL, 3, 1, UTC_TIMESTAMP(6) FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM templateswhatsapp WHERE Nombre='olv_frio_combo_consultas_v1');
INSERT INTO templateswhatsapp (Nombre, Texto, Rubro, Pais, EstadoAprobacionMeta, Activo, CreatedAt) SELECT 'olv_frio_combo_gestion_v1', 'Hola! Vi tu negocio y pensé: {{2}}.

Soy Joaquín, de Olvidata Soft. Ayudamos a {{1}} como el tuyo armando sistemas a medida para ordenar {{3}} de una vez por todas.

Básicamente, {{4}}.

Y de paso te muestro el resto del combo: tu propia página web, agentes de IA para lo administrativo y un asistente que responde solo por WhatsApp.

Te sirve?

Un saludo,

Joaquín
Olvidata Soft', NULL, NULL, 3, 1, UTC_TIMESTAMP(6) FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM templateswhatsapp WHERE Nombre='olv_frio_combo_gestion_v1');
INSERT INTO templateswhatsapp (Nombre, Texto, Rubro, Pais, EstadoAprobacionMeta, Activo, CreatedAt) SELECT 'olv_frio_combo_admin_v1', 'Hola! Vi tu negocio y pensé: {{2}}.

Soy Joaquín, de Olvidata Soft. Ayudamos a {{1}} como el tuyo con agentes de IA que se encargan de {{3}} de una vez por todas.

Básicamente, {{4}}.

Y de paso te muestro el resto del combo: tu propia página web y un asistente que responde solo las consultas por WhatsApp.

Te sirve?

Un saludo,

Joaquín
Olvidata Soft', NULL, NULL, 3, 1, UTC_TIMESTAMP(6) FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM templateswhatsapp WHERE Nombre='olv_frio_combo_admin_v1');
UPDATE configuracionesoutbound SET
  PlantillaGanchoPresenciaWeb   = 'olv_frio_combo_web_v1',
  PlantillaGanchoAdministracion = 'olv_frio_combo_admin_v1',
  PlantillaGanchoConsultas      = 'olv_frio_combo_consultas_v1',
  PlantillaGanchoGestion        = 'olv_frio_combo_gestion_v1';
SELECT Nombre, EstadoAprobacionMeta, Activo, CHAR_LENGTH(Texto) AS Largo FROM templateswhatsapp WHERE Nombre LIKE 'olv_frio_combo%';