namespace BlankProject.Application.Interfaces;

/// <summary>
/// Servicio de exportacion a Excel y PDF.
/// </summary>
public interface IExportService
{
    /// <summary>
    /// Exporta datos a Excel (.xlsx). Devuelve los bytes del archivo.
    /// </summary>
    byte[] ExportToExcel<T>(IEnumerable<T> data, string sheetName = "Datos");

    /// <summary>
    /// Exporta datos a PDF. Devuelve los bytes del archivo.
    /// </summary>
    byte[] ExportToPdf<T>(IEnumerable<T> data, string title, string? subtitle = null);
}
