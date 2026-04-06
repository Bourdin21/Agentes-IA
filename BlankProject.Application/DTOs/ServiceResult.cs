namespace BlankProject.Application.DTOs;

/// <summary>
/// DTO base para respuestas de servicio.
/// </summary>
public class ServiceResult<T>
{
    public bool Success { get; set; } = true;
    public T? Data { get; set; }
    public string? Message { get; set; }
    public List<string> Errors { get; set; } = new();

    public static ServiceResult<T> CreateSuccess(T data, string? message = null) =>
        new() { Success = true, Data = data, Message = message };

    public static ServiceResult<T> CreateError(string message, List<string>? errors = null) =>
        new() { Success = false, Message = message, Errors = errors ?? new() };

    public static ServiceResult<T> CreateError(List<string> errors) =>
        new() { Success = false, Errors = errors };
}

/// <summary>
/// DTO base sin dato (para operaciones que no retornan data).
/// </summary>
public class ServiceResult
{
    public bool Success { get; set; } = true;
    public string? Message { get; set; }
    public List<string> Errors { get; set; } = new();

    public static ServiceResult CreateSuccess(string? message = null) =>
        new() { Success = true, Message = message };

    public static ServiceResult CreateError(string message, List<string>? errors = null) =>
        new() { Success = false, Message = message, Errors = errors ?? new() };

    public static ServiceResult CreateError(List<string> errors) =>
        new() { Success = false, Errors = errors };
}
