# ============================================================================
#  SI.G.VA.C.H. — Proyecto ESP-IDF del módulo de adquisición
#
#  Activa el entorno de ESP-IDF en la sesión actual de PowerShell.
#
#  USO (el punto del principio es obligatorio: ejecuta el script EN esta sesión,
#  porque si no, las variables se pierden al terminar):
#
#      . .\entorno_idf.ps1
#
#  Después ya se puede usar idf.py normalmente:
#
#      idf.py set-target esp32
#      idf.py build
#      idf.py -p COM3 flash monitor
# ============================================================================

$ErrorActionPreference = 'Stop'

$idfTools  = 'C:\esp-idf-v5.5.3\Espressif'
$idfScript = Join-Path $idfTools 'frameworks\esp-idf-v5.5.3\export.ps1'

if (-not (Test-Path $idfScript)) {
    Write-Host "ERROR: no se encontro el entorno de ESP-IDF en:" -ForegroundColor Red
    Write-Host "  $idfScript" -ForegroundColor Red
    Write-Host "Revise la ruta o reinstale ESP-IDF." -ForegroundColor Red
    return
}

# el script de Espressif espera esta variable
$env:IDF_TOOLS_PATH = $idfTools

Write-Host "Activando ESP-IDF v5.5.3..." -ForegroundColor Cyan
& $idfScript | Out-Null

if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
    Write-Host "ERROR: fallo la activacion del entorno." -ForegroundColor Red
    return
}

Write-Host "Entorno listo. idf.py apunta a:" -ForegroundColor Green
idf.py --version
