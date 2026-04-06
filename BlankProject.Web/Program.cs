using System.IO.Compression;
using System.Threading.RateLimiting;
using BlankProject.Domain.Entities;
using BlankProject.Infrastructure;
using BlankProject.Infrastructure.Data;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.AspNetCore.ResponseCompression;
using QuestPDF.Infrastructure;
using Serilog;
using BlankProject.Web.Middleware;

// QuestPDF Community License
QuestPDF.Settings.License = LicenseType.Community;

// Bootstrap logger (antes de que la app arranque)
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateBootstrapLogger();

try
{
    var builder = WebApplication.CreateBuilder(args);

    // Serilog: leer config desde appsettings.{Environment}.json
    builder.Host.UseSerilog((context, services, configuration) =>
        configuration.ReadFrom.Configuration(context.Configuration));

    // Infrastructure: EF Core + MySQL + Repositorios + Email
    builder.Services.AddInfrastructure(builder.Configuration);

    // Identity
    builder.Services.AddIdentity<ApplicationUser, IdentityRole>(options =>
    {
        options.Password.RequireDigit = true;
        options.Password.RequiredLength = 6;
        options.Password.RequireNonAlphanumeric = false;
        options.Password.RequireUppercase = true;
        options.Password.RequireLowercase = true;
        options.User.RequireUniqueEmail = true;
        options.SignIn.RequireConfirmedAccount = false;
    })
    .AddEntityFrameworkStores<AppDbContext>()
    .AddDefaultTokenProviders();

    // Cookie config
    builder.Services.ConfigureApplicationCookie(options =>
    {
        options.LoginPath = "/Account/Login";
        options.LogoutPath = "/Account/Logout";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromDays(90);
        options.SlidingExpiration = true;
    });

    // Authorization policies
    builder.Services.AddAuthorization(options =>
    {
        options.AddPolicy("RequireSuperUsuario",
            policy => policy.RequireRole(SeedData.RolSuperUsuario));

        options.AddPolicy("RequireAdministracion",
            policy => policy.RequireRole(SeedData.RolSuperUsuario, SeedData.RolAdministrador));
    });

    builder.Services.AddControllersWithViews();

    // Global Exception Handler
    builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
    builder.Services.AddProblemDetails();

    // Response Compression: Brotli + Gzip
    builder.Services.AddResponseCompression(options =>
    {
        options.EnableForHttps = true;
        options.Providers.Add<BrotliCompressionProvider>();
        options.Providers.Add<GzipCompressionProvider>();
        options.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
        [
            "application/json",
            "application/javascript",
            "text/css",
            "image/svg+xml"
        ]);
    });
    builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
        options.Level = CompressionLevel.Fastest);
    builder.Services.Configure<GzipCompressionProviderOptions>(options =>
        options.Level = CompressionLevel.SmallestSize);

    // Rate Limiting
    builder.Services.AddRateLimiter(options =>
    {
        options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

        // Política general: 100 requests por minuto por IP
        options.AddPolicy("general", context =>
            RateLimitPartition.GetFixedWindowLimiter(
                partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                factory: _ => new FixedWindowRateLimiterOptions
                {
                    PermitLimit = 100,
                    Window = TimeSpan.FromMinutes(1),
                    QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                    QueueLimit = 5
                }));

        // Política estricta para login: 10 intentos por minuto por IP
        options.AddPolicy("login", context =>
            RateLimitPartition.GetFixedWindowLimiter(
                partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                factory: _ => new FixedWindowRateLimiterOptions
                {
                    PermitLimit = 10,
                    Window = TimeSpan.FromMinutes(1),
                    QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                    QueueLimit = 0
                }));
    });

    // Session: persistir filtros de usuario entre navegaciones
    builder.Services.AddDistributedMemoryCache();
    builder.Services.AddSession(options =>
    {
        options.IdleTimeout = TimeSpan.FromMinutes(60);
        options.Cookie.HttpOnly = true;
        options.Cookie.IsEssential = true;
    });

    // Forzar HTTPS en todas las redirecciones
    builder.Services.AddHttpsRedirection(options =>
    {
        options.HttpsPort = 443;
    });

    builder.Services.AddHsts(options =>
    {
        options.MaxAge = TimeSpan.FromDays(365);
        options.IncludeSubDomains = true;
        options.Preload = true;
    });

    var app = builder.Build();

    // Cultura fija: es-AR para que serialización y model binding coincidan
    var cultureInfo = new System.Globalization.CultureInfo("es-AR");
    app.UseRequestLocalization(new RequestLocalizationOptions
    {
        DefaultRequestCulture = new Microsoft.AspNetCore.Localization.RequestCulture(cultureInfo),
        SupportedCultures = [cultureInfo],
        SupportedUICultures = [cultureInfo]
    });

    if (app.Environment.IsDevelopment())
    {
        // Developer Exception Page: muestra stack trace, query, cookies, headers.
        // Equivalente al Application_Error de Global.asax para debugging.
        app.UseDeveloperExceptionPage();
    }
    else
    {
        // GlobalExceptionHandler procesa la excepción (log + JSON para AJAX),
        // luego UseExceptionHandler redirige a /Home/Error para requests MVC.
        app.UseExceptionHandler("/Home/Error");
        app.UseHsts();
    }

    app.UseHttpsRedirection();

    // Response Compression (antes de static files para comprimir respuestas dinámicas)
    app.UseResponseCompression();

    app.UseStatusCodePagesWithReExecute("/Home/StatusCode", "?code={0}");

    // Serilog: log de requests HTTP
    app.UseSerilogRequestLogging(options =>
    {
        options.MessageTemplate = "{RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000}ms";
    });

    app.UseStaticFiles();

    app.UseRouting();

    app.UseAuthentication();
    app.UseAuthorization();
    app.UseRateLimiter();
    app.UseSession();

    app.MapControllerRoute(
        name: "default",
        pattern: "{controller=Home}/{action=Index}/{id?}")
        .RequireRateLimiting("general");

    app.MapHealthChecks("/health");

    // Seed: crear roles y SuperUsuario inicial
    using (var scope = app.Services.CreateScope())
    {
        await SeedData.InitializeAsync(scope.ServiceProvider);
    }

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "La aplicación falló al iniciar.");
}
finally
{
    Log.CloseAndFlush();
}
