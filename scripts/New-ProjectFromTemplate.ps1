#!/usr/bin/env pwsh
# ============================================================
# New-ProjectFromTemplate.ps1
# Crea un nuevo proyecto a partir de la plantilla BlankProject.
#
# USO:
#   .\scripts\New-ProjectFromTemplate.ps1 -NewName "MiProyecto" -OutputDir "C:\Sistemas"
#
# RESULTADO:
#   C:\Sistemas\MiProyecto\  (listo para abrir en Visual Studio)
# ============================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$NewName,

    [Parameter(Mandatory = $false)]
    [string]$OutputDir = "..",

    [Parameter(Mandatory = $false)]
    [string]$TemplateDir = ""
)

# Resolver TemplateDir: si viene vacio, usar la ubicacion del script
if ([string]::IsNullOrWhiteSpace($TemplateDir)) {
    $TemplateDir = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($TemplateDir)) {
        $TemplateDir = (Get-Location).Path
    }
}

# Si se ejecuta desde /scripts, subir un nivel para encontrar la raiz
if ($TemplateDir -match '[/\\]scripts[/\\]?$') {
    $TemplateDir = Split-Path $TemplateDir -Parent
}

$OldName = "BlankProject"
$DestDir = Join-Path $OutputDir $NewName

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Olvidata Soft - Generador de Proyecto" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Template:  $TemplateDir" -ForegroundColor Gray
Write-Host "  Nuevo:     $DestDir" -ForegroundColor Green
Write-Host "  Renombrar: $OldName -> $NewName" -ForegroundColor Yellow
Write-Host ""

# --- Validaciones ---
if (Test-Path $DestDir) {
    Write-Host "ERROR: El directorio destino ya existe: $DestDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $TemplateDir "$OldName.slnx"))) {
    Write-Host "ERROR: No se encontro $OldName.slnx en $TemplateDir" -ForegroundColor Red
    exit 1
}

# --- 1. Copiar plantilla ---
Write-Host "[1/5] Copiando plantilla..." -ForegroundColor Cyan
$excludeDirs = @('.git', '.vs', 'bin', 'obj', 'node_modules', 'Logs')

function Copy-FilteredTree {
    param($Source, $Dest)
    Get-ChildItem -Path $Source -Force | ForEach-Object {
        if ($_.PSIsContainer) {
            if ($excludeDirs -notcontains $_.Name) {
                $newDest = Join-Path $Dest $_.Name
                New-Item -ItemType Directory -Path $newDest -Force | Out-Null
                Copy-FilteredTree -Source $_.FullName -Dest $newDest
            }
        } else {
            Copy-Item $_.FullName -Destination $Dest -Force
        }
    }
}

New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
Copy-FilteredTree -Source $TemplateDir -Dest $DestDir

# --- 2. Renombrar carpetas ---
Write-Host "[2/5] Renombrando carpetas..." -ForegroundColor Cyan
Get-ChildItem -Path $DestDir -Directory -Recurse |
    Where-Object { $_.Name -match $OldName } |
    Sort-Object { $_.FullName.Length } -Descending |
    ForEach-Object {
        $newPath = Join-Path $_.Parent.FullName ($_.Name -replace [regex]::Escape($OldName), $NewName)
        Rename-Item $_.FullName $newPath
        Write-Host "  DIR  $($_.Name) → $(Split-Path $newPath -Leaf)" -ForegroundColor DarkGray
    }

# --- 3. Renombrar archivos ---
Write-Host "[3/5] Renombrando archivos..." -ForegroundColor Cyan
Get-ChildItem -Path $DestDir -File -Recurse |
    Where-Object { $_.Name -match $OldName } |
    ForEach-Object {
        $newFileName = $_.Name -replace [regex]::Escape($OldName), $NewName
        $newPath = Join-Path $_.DirectoryName $newFileName
        Rename-Item $_.FullName $newPath
        Write-Host "  FILE $($_.Name) → $newFileName" -ForegroundColor DarkGray
    }

# --- 4. Reemplazar contenido ---
Write-Host "[4/5] Reemplazando contenido en archivos..." -ForegroundColor Cyan
$extensions = @('*.cs', '*.csproj', '*.slnx', '*.json', '*.cshtml', '*.css', '*.js',
                '*.webmanifest', '*.md', '*.example', '*.html')
$count = 0

foreach ($ext in $extensions) {
    Get-ChildItem -Path $DestDir -Recurse -Filter $ext -File | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldName) {
            $newContent = $content -replace [regex]::Escape($OldName), $NewName
            Set-Content $_.FullName $newContent -NoNewline
            $count++
        }
    }
}
Write-Host "  $count archivos actualizados." -ForegroundColor DarkGray

# --- 5. Limpiar migraciones (proyecto nuevo = DB nueva) ---
Write-Host "[5/5] Limpiando migraciones antiguas..." -ForegroundColor Cyan
$migrationsDir = Join-Path (Join-Path (Join-Path $DestDir "$NewName.Infrastructure") "Data") "Migrations"
if (Test-Path $migrationsDir) {
    Remove-Item $migrationsDir -Recurse -Force
    Write-Host "  Carpeta Migrations eliminada. Crear nueva con:" -ForegroundColor DarkGray
    Write-Host "    dotnet ef migrations add InitialCreate -p $NewName.Infrastructure -s $NewName.Web -o Data/Migrations" -ForegroundColor Yellow
}

# --- Resumen ---
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  OK - Proyecto '$NewName' creado exitosamente!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Proximos pasos:" -ForegroundColor White
Write-Host "  1. Abrir $DestDir\$NewName.slnx en Visual Studio" -ForegroundColor Gray
Write-Host "  2. Editar appsettings.Development.json (connection string)" -ForegroundColor Gray
Write-Host "  3. Crear migracion inicial:" -ForegroundColor Gray
Write-Host "     dotnet ef migrations add InitialCreate -p $NewName.Infrastructure -s $NewName.Web -o Data/Migrations" -ForegroundColor Yellow
Write-Host "  4. Aplicar migracion:" -ForegroundColor Gray
Write-Host "     dotnet ef database update -p $NewName.Infrastructure -s $NewName.Web" -ForegroundColor Yellow
Write-Host "  5. Ejecutar: dotnet run --project $NewName.Web" -ForegroundColor Gray
Write-Host ""
Write-Host "  Opcional:" -ForegroundColor White
Write-Host "  - git init && git remote add origin <tu-repo>" -ForegroundColor Gray
Write-Host "  - Editar appsettings.Production.json con credenciales reales" -ForegroundColor Gray
Write-Host "  - Reemplazar wwwroot/icons/icon-192.png con el logo del nuevo proyecto" -ForegroundColor Gray
Write-Host ""
