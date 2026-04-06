using System.Globalization;

namespace BlankProject.Web.Helpers;

/// <summary>
/// Helper centralizado para formateo de importes monetarios.
/// Formato argentino: $ 1.234.567,89 / U$D 1.234.567,89
/// </summary>
public static class FormatoMoneda
{
    private static readonly CultureInfo CulturaAR = new("es-AR");

    /// <summary>
    /// Formatea un importe con separador de miles (.) y decimal (,).
    /// Ejemplo: FormatMonto(1234567.89m) → "1.234.567,89"
    /// </summary>
    public static string FormatMonto(decimal valor)
    {
        return valor.ToString("N2", CulturaAR);
    }

    /// <summary>
    /// Formatea un importe con símbolo de moneda.
    /// Ejemplo: FormatMoneda(1234567.89m, "$") → "$ 1.234.567,89"
    /// </summary>
    public static string FormatMoneda(decimal valor, string simbolo)
    {
        return $"{simbolo} {FormatMonto(valor)}";
    }

    /// <summary>
    /// Formatea un porcentaje con 1 decimal.
    /// Ejemplo: FormatPorcentaje(32.15m) → "32,1%"
    /// </summary>
    public static string FormatPorcentaje(decimal valor)
    {
        return valor.ToString("N1", CulturaAR) + "%";
    }
}
