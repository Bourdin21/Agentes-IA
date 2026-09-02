---
name: project-botpublicitario
description: "WhatsApp outbound bot for Olvidata Soft — current status, IDs, pending manual steps"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3852cee1-ac66-4cd4-bebe-7d515e611a03
---

## Goal
Outbound WhatsApp marketing campaigns targeting accounting firms (estudios contables) in La Plata, Argentina.

## GitLab Remote
`git@gitlab.com-bot:olvidata/bot-publicitario.git` (via SSH alias `gitlab.com-bot`, key `id_ed25519_olvidata_gitlab`)

## Meta API IDs (all verified correct)
- Business Manager ID: `618534606686923`
- WABA ID: `829193586771866`
- Phone Number ID: `1117253834810607`
- WhatsApp number: `542214402340` (54 + area + local, WITHOUT the 9 for API)
- Ad Account: `act_818765367582069`
- Page ID: `488639934340412`
- Instagram Account: `17841456625525075`
- Catalog ID: `1418913103373508`

## Key Known Facts
- Phone number format for Meta API: `542214402340` NOT `5492214402340` (drop the 9)
- Platform type: CLOUD_API (not ON_PREMISE). Phone Number ID `1117253834810607` is VERIFIED.
- Two WABAs exist: `1185003232489003` (old, on-premise, ignore) and `829193586771866` (correct, active)
- `UpdateCommerceSettingsAsync` via Cloud API returns 400 — cart must be disabled manually in WhatsApp Manager

## Pending Manual Steps (as of 2026-05-22)
1. WhatsApp Manager → number 1117253834810607 → Catalog → link catalog `1418913103373508`
2. WhatsApp Manager → disable cart toggle (so CTA = "Enviar mensaje")
3. Upload product images to `olvidata.com.ar/img/`: `build.jpg`, `landing.jpg`, `merge.jpg`, `mantenimiento.jpg`
4. Wait for Meta to approve 3 templates: `contacto_frio_olvidata`, `contacto_referido_olvidata`, `seguimiento_olvidata`

## When Templates Are Approved
Run: `dotnet run -- check-templates` then `dotnet run -- run`

## State
10 prospects loaded in `WhatsApp/outbound_state.json`, all status=0 (Pending), all La Plata accounting firms.
