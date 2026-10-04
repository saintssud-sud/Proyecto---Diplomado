# Espera a que aparezca el puerto de la placa y despues escucha el monitor serie.
#
# Por que existe: la placa no siempre esta conectada cuando se quiere registrar un
# ciclo. Sin esto hay que estar probando a mano hasta que aparece el puerto, y el
# ciclo de servicio dura 300 segundos, asi que cada intento fallido cuesta tiempo.
#
# Uso:
#   pwsh -File esperar_y_escuchar.ps1 -Puerto COM6 -EsperaMaxima 300 -Segundos 300

param(
    [string]$Puerto = "COM6",
    [int]$EsperaMaxima = 300,
    [int]$Segundos = 300
)

$ErrorActionPreference = 'Continue'
$espera = 0
while ($espera -lt $EsperaMaxima) {
    if ([System.IO.Ports.SerialPort]::GetPortNames() -contains $Puerto) { break }
    Start-Sleep -Seconds 5
    $espera += 5
}

if ($espera -ge $EsperaMaxima) {
    Write-Host ("No aparecio {0} en {1} segundos. Revisa el cable USB: tiene que ser un cable de datos, no uno de solo carga." -f $Puerto, $EsperaMaxima)
    exit 3
}

Write-Host ("Puerto {0} disponible despues de {1} segundos. Empieza la escucha." -f $Puerto, $espera)
& (Join-Path $PSScriptRoot "leer_serial.ps1") -Puerto $Puerto -Segundos $Segundos
