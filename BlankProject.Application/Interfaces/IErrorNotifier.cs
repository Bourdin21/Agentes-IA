namespace BlankProject.Application.Interfaces;

/// <summary>
/// Servicio para notificar errores por email a los administradores.
/// Puede usarse desde middleware (excepciones no manejadas) y controllers (excepciones capturadas).
/// </summary>
public interface IErrorNotifier
{
    /// <summary>
    /// Envía una notificación de error por email de forma fire-and-forget.
    /// No lanza excepciones si falla el envío.
    /// </summary>
    void NotifyError(Exception ex, string? usuario = null, string? requestInfo = null);
}
