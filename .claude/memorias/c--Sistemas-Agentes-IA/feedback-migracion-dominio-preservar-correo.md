---
name: feedback-migracion-dominio-preservar-correo
description: "En migraciones de dominio/DNS/hosting de un cliente con correo en Google Workspace (u otro proveedor externo), ofrecer explícitamente un backup extra (Google Takeout) aunque técnicamente el DNS no toque el almacenamiento del correo"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 311be6a4-e5ba-46ff-845b-c40275e187be
  modified: 2026-09-02T03:16:18.507Z
---

Cuando se migra el DNS/hosting de un dominio de cliente que tiene correo en Google Workspace (o cualquier proveedor de mail externo al hosting), Joaquín insiste explícitamente en que no se pierda "ningún correo enviado ni recibido" — incluso después de haber confirmado dos veces que técnicamente el MX/DNS no toca el almacenamiento del correo (el mail vive en el proveedor externo, no en el hosting que se está migrando).

**Why:** Aunque el riesgo real es solo de un bache de entrega (nunca pérdida de histórico) si el MX no se recrea a tiempo en el nuevo DNS, la insistencia repetida indica que para el cliente/Joaquín la garantía verbal de "no se toca nada" no es suficiente tranquilidad — quieren un respaldo tangible antes de tocar cualquier DNS.

**How to apply:** En cualquier plan de migración de dominio (ver caso belclau.com.ar → Hostinger, [[infraestructura-completa-olvidata]]) que involucre un dominio con correo externo (Google Workspace, M365, etc.), incluir como paso explícito del runbook —no solo como explicación— un backup previo (Google Takeout / export a `.mbox`, o Vault si aplica) antes de tocar nameservers, y mencionarlo proactivamente sin esperar a que lo pidan una tercera vez.
