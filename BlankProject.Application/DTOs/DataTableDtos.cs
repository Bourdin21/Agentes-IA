namespace BlankProject.Application.DTOs;

/// <summary>
/// Request generico para DataTables server-side (jQuery DataTables).
/// </summary>
public class DataTableRequest
{
    public int Draw { get; set; }
    public int Start { get; set; }
    public int Length { get; set; } = 15;
    public string? SearchValue { get; set; }
    public string? SortColumn { get; set; }
    public string? SortDirection { get; set; } = "asc";
}

/// <summary>
/// Response generico para DataTables server-side.
/// </summary>
public class DataTableResponse<T>
{
    public int Draw { get; set; }
    public int RecordsTotal { get; set; }
    public int RecordsFiltered { get; set; }
    public List<T> Data { get; set; } = new();
}
