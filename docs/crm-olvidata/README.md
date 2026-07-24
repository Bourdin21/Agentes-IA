# Plantilla de proyecto

Copiar esta carpeta como /docs/<nombre-proyecto>/ para inicializar la memoria de un proyecto nuevo.

Pasos:
1. Copiar la carpeta completa como /docs/<nombre-proyecto>/.
2. Completar metadata.md con datos del proyecto.
3. Completar presupuesto-cliente.md cuando el proyecto llegue a etapa de presupuesto.
4. Registrar el proyecto en /docs/indice.md.
5. Cada agente lee y actualiza su archivo en definiciones/ al inicio y cierre de cada etapa.
6. Copiar `copilot-instructions.md` de esta plantilla al repositorio del sistema como `.github/copilot-instructions.md` y personalizar:
   - Reemplazar `<NombreProyecto>` y `<Proyecto>` por el nombre real.
   - Ajustar las secciones marcadas como `[Personalizar]` (stack, paleta, comandos) si el proyecto difiere del baseline BlankProject.
   - Mantener ese archivo sincronizado con las definiciones de los agentes `3-arquitecto-mvc` y `5-implementador`.
