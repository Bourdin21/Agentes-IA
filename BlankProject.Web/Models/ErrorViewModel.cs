namespace BlankProject.Web.Models;

public class ErrorViewModel
{
    public string? RequestId { get; set; }
    public int StatusCode { get; set; }
    public string Titulo { get; set; } = "Error";
    public string Mensaje { get; set; } = "Ocurrió un error inesperado.";

    public bool ShowRequestId => !string.IsNullOrEmpty(RequestId);
}
