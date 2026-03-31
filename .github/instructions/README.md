# Instrucciones Modulares BlankProject

Esta carpeta divide las reglas en modulos reutilizables por etapa y por capa.

## Orden sugerido de lectura
1. 00-operativa-global.instructions.md
2. 01-fronteras-por-capa.instructions.md
3. 10-blankproject-base.instructions.md
4. 20-domain.instructions.md
5. 21-application.instructions.md
6. 22-infrastructure.instructions.md
7. 23-web.instructions.md
8. 24-config-paquetes.instructions.md
9. 25-frontend-design-system.instructions.md
10. 26-checklists.instructions.md

## Como usar
- Las reglas globales definen marco comun de trabajo y formato de salida.
- Las reglas de capa definen limites tecnicos y responsabilidades.
- Los agentes y prompts deben referenciar explicitamente los modulos que priorizan.

## Nota
Evitar reglas globales con applyTo demasiado amplio salvo que sea estrictamente necesario.
