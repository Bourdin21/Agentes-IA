using System.Reflection;
using ClosedXML.Excel;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
using BlankProject.Application.Interfaces;

namespace BlankProject.Infrastructure.Services;

public class ExportService : IExportService
{
    public byte[] ExportToExcel<T>(IEnumerable<T> data, string sheetName = "Datos")
    {
        using var workbook = new XLWorkbook();
        var worksheet = workbook.Worksheets.Add(sheetName);

        var properties = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance);

        // Headers
        for (var i = 0; i < properties.Length; i++)
        {
            var cell = worksheet.Cell(1, i + 1);
            cell.Value = GetDisplayName(properties[i]);
            cell.Style.Font.Bold = true;
            cell.Style.Fill.BackgroundColor = XLColor.FromHtml("#2b9de4");
            cell.Style.Font.FontColor = XLColor.White;
        }

        // Data
        var row = 2;
        foreach (var item in data)
        {
            for (var col = 0; col < properties.Length; col++)
            {
                var value = properties[col].GetValue(item);
                var cell = worksheet.Cell(row, col + 1);

                if (value is DateTime dt)
                    cell.Value = dt.ToString("dd/MM/yyyy HH:mm");
                else if (value is bool b)
                    cell.Value = b ? "Si" : "No";
                else
                    cell.Value = value?.ToString() ?? "";
            }
            row++;
        }

        worksheet.Columns().AdjustToContents();

        using var stream = new MemoryStream();
        workbook.SaveAs(stream);
        return stream.ToArray();
    }

    public byte[] ExportToPdf<T>(IEnumerable<T> data, string title, string? subtitle = null)
    {
        var properties = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance);
        var items = data.ToList();

        var document = Document.Create(container =>
        {
            container.Page(page =>
            {
                page.Size(PageSizes.A4.Landscape());
                page.Margin(30);
                page.DefaultTextStyle(x => x.FontSize(9));

                page.Header().Column(col =>
                {
                    col.Item().Text(title).FontSize(16).Bold().FontColor(Colors.Blue.Darken2);
                    if (!string.IsNullOrEmpty(subtitle))
                        col.Item().Text(subtitle).FontSize(10).FontColor(Colors.Grey.Darken1);
                    col.Item().Text($"Generado: {DateTime.Now:dd/MM/yyyy HH:mm}").FontSize(8).FontColor(Colors.Grey.Medium);
                    col.Item().PaddingBottom(10);
                });

                page.Content().Table(table =>
                {
                    table.ColumnsDefinition(columns =>
                    {
                        for (var i = 0; i < properties.Length; i++)
                            columns.RelativeColumn();
                    });

                    // Header
                    foreach (var prop in properties)
                    {
                        table.Cell().Background(Colors.Blue.Darken2).Padding(4)
                            .Text(GetDisplayName(prop)).FontColor(Colors.White).Bold().FontSize(8);
                    }

                    // Rows
                    var alternate = false;
                    foreach (var item in items)
                    {
                        var bg = alternate ? Colors.Grey.Lighten4 : Colors.White;
                        foreach (var prop in properties)
                        {
                            var value = prop.GetValue(item);
                            var text = value switch
                            {
                                DateTime dt => dt.ToString("dd/MM/yyyy HH:mm"),
                                bool b => b ? "Si" : "No",
                                _ => value?.ToString() ?? ""
                            };
                            table.Cell().Background(bg).Padding(4).Text(text).FontSize(8);
                        }
                        alternate = !alternate;
                    }
                });

                page.Footer().AlignCenter()
                    .Text(x => { x.Span("Pagina "); x.CurrentPageNumber(); x.Span(" de "); x.TotalPages(); });
            });
        });

        return document.GeneratePdf();
    }

    private static string GetDisplayName(PropertyInfo prop)
    {
        var attr = prop.GetCustomAttribute<System.ComponentModel.DataAnnotations.DisplayAttribute>();
        return attr?.Name ?? prop.Name;
    }
}
