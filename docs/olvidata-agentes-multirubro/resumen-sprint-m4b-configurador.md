# Olvidata**Soft**

---

**Olvidata Agentes Multi-rubro — Configurar reglas conversando**

**OlvidataSoft · Septiembre 2026**

## Sobre el proyecto

En esta entrega el Director puede configurar las reglas de su empresa contándole a un agente cómo trabajan, sin llenar formularios ni conocer los detalles de cada regla. Nada se aplica sin su confirmación.

- El Director abre "Configurar conversando" en Reglas y cuenta cómo trabaja la empresa.
- El configurador revisa las reglas actuales y propone reglas nuevas, cambios o desactivaciones.
- Cada propuesta aparece como una tarjeta clara: dónde aplica, cuándo, el texto y por qué.
- El Director aplica, corrige o descarta cada una con un botón.

## Cambios entregados

- **Conversación de configuración** con ejemplos para arrancar ("Cómo hablamos con los clientes", "Cosas que nunca hacemos", "Revisá mis reglas actuales").
- **Tarjetas de propuesta** con "Aplicar", "Editar y aplicar", "Descartar" y "Aplicar todas", con resumen de lo que se aplicó y lo que no.
- **Aviso cuando una regla cambió** desde que se hizo la propuesta, para revisar antes de aplicar.
- **Nada se aplica escribiendo**: solo con los botones.
- **Lista de conversaciones compartida** entre Directores, con propuestas pendientes y aplicadas.
- **Origen visible**: cada regla muestra si nació de una propuesta del configurador.
- **Costo a la vista** en el listado de Tareas.
- **Protección**: el configurador solo lee lo que el Director puede ver, nunca preferencias personales de otras personas ni datos de otras empresas.

## Beneficio

- Configurar la empresa pasa a ser una conversación: el Director no necesita aprender cómo funcionan las reglas por dentro.
- El control queda siempre del lado de la persona: el agente propone, el Director decide.
- Lo probé en un navegador real con todos los casos (propuestas que fallan por límite, reglas que cambiaron, dos Directores a la vez, permisos), sin errores funcionales.

## Pendientes o fuera de alcance

- **El prompt del configurador está en borrador**: hay que revisarlo y publicarlo para habilitar la función.
- Falta una prueba con el modelo real para medir la calidad de las propuestas y el costo (requiere tu OK).
- Los empleados todavía no tienen un configurador para sus preferencias.
- Hay colores de botones de todo el portal con poco contraste para revisar en conjunto.

## Próximo paso sugerido

Publicar el prompt del configurador después de revisarlo y hacer la primera corrida real, antes de seguir con **M5 — Espacio de trabajo por cliente**.

**Olvidata Soft — olvidatasoft@gmail.com — https://olvidata.com.ar/**
