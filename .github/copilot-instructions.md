# Stack oficial
- ASP.NET Core MVC (.NET 10)
- Entity Framework Core
- MySQL 8
- Arquitectura de tres capas: Presentacion, Negocio, Datos

# Secuencia operativa obligatoria
Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas -> Documentacion

# Fronteras por capa
- Presentacion: Controllers, Views, ViewModels, validaciones de pantalla.
- Negocio: Services, reglas de negocio, estados, permisos, procesos.
- Datos: DbContext, entidades, configuraciones EF, migraciones, acceso MySQL.

# Reglas obligatorias
- No colocar logica de negocio compleja en Controllers.
- Los Controllers solo coordinan request/response y delegan en Services.
- La logica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificacion debe indicar que capas afecta y por que.
- Si un cambio requiere migracion EF, debe indicarse explicitamente.
- Si un cambio afecta permisos, estados o validaciones, debe listarse.
- No hacer refactors cosmeticos salvo pedido expreso.
- Preservar comportamiento legacy salvo indicacion contraria.
- Siempre proponer pruebas minimas.

# Modo de trabajo recomendado
- Ask mode: Analisis, Diseno, Arquitectura, Presupuesto.
- Agent mode: Implementacion, pruebas tecnicas, correccion de build, generacion de tests, documentacion tecnica derivada de codigo.

# Formato minimo de respuestas tecnicas
- Alcance funcional resumido.
- Impacto tecnico por capa.
- Riesgos y supuestos.
- Pruebas minimas requeridas.
- Checklist de salida para merge.
