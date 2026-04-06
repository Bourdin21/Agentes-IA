---
description: Reglas de Application (interfaces, DTOs, ServiceResult y contratos async).
applyTo: "**/Application/**/*.cs"
---

# Application
- Define interfaces y DTOs, nunca implementaciones.
- Todas las interfaces async con Task.

# Interfaces obligatorias
- IRepository<T> con constraint where T : SoftDestroyable.
- IEmailService.
- IErrorNotifier.
- INotificationService.
- IExportService.

# DTOs base
- ServiceResult y ServiceResult<T>.
- DataTableRequest y DataTableResponse<T>.
- NotificationDto.

# Patron ServiceResult
- Servicios que pueden fallar deben retornar ServiceResult o ServiceResult<T>.
