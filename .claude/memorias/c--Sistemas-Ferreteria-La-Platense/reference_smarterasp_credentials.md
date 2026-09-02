---
name: reference-smarterasp-credentials
description: Dónde está guardada la password de la cuenta reseller de SmarterASP para Web Deploy/FTP de todos los clientes de Olvidata Soft
metadata: 
  node_type: memory
  type: reference
  originSessionId: bc755a3e-0b32-4b42-9695-956808c26af7
  modified: 2026-08-17T23:54:28.826Z
---

Las credenciales de Web Deploy/FTP de SmarterASP (site4now.net) — usuario `olvidatasoft-002`,
compartido por todos los sitios de clientes de Olvidata Soft — están en
`C:\Sistemas\Agentes-IA\docs\credenciales.local.md`.

Ese archivo está en `.gitignore` a propósito: el repo de Agentes-IA tiene remoto en GitHub
(`Bourdin21/Agentes-IA`), así que nunca se debe poner la password en un archivo tracked
(`.PublishSettings` de cada proyecto, `metadata.md`, etc.) — solo completarla ahí temporalmente
al momento del deploy y borrarla después.

Ver también [[project_la_platense_status]] para el contexto del deploy donde se confirmó esta password.
