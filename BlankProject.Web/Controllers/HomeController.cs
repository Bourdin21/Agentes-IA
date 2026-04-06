using System.Diagnostics;
using BlankProject.Web.Models;
using Microsoft.AspNetCore.Mvc;

namespace BlankProject.Web.Controllers;

public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    public IActionResult Index()
    {
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel
        {
            RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier,
            StatusCode = 500,
            Titulo = "Error interno",
            Mensaje = "Ocurrió un error inesperado al procesar su solicitud."
        });
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult StatusCode(int code)
    {
        if (code < 400 || code > 599)
            code = 500;

        var vm = code switch
        {
            404 => new ErrorViewModel
            {
                StatusCode = 404,
                Titulo = "Página no encontrada",
                Mensaje = "La página que buscás no existe o fue movida."
            },
            403 => new ErrorViewModel
            {
                StatusCode = 403,
                Titulo = "Acceso denegado",
                Mensaje = "No tenés permisos para acceder a esta sección."
            },
            429 => new ErrorViewModel
            {
                StatusCode = 429,
                Titulo = "Demasiadas solicitudes",
                Mensaje = "Realizaste demasiadas solicitudes en poco tiempo. Esperá un momento e intentá de nuevo."
            },
            500 => new ErrorViewModel
            {
                StatusCode = 500,
                Titulo = "Error interno",
                Mensaje = "Ocurrió un error inesperado al procesar su solicitud."
            },
            _ => new ErrorViewModel
            {
                StatusCode = code,
                Titulo = $"Error {code}",
                Mensaje = "Ocurrió un error al procesar su solicitud."
            }
        };

        vm.RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier;
        return View("Error", vm);
    }
}
