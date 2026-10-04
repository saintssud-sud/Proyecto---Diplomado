# Muestra en vivo las lecturas de los sensores del modulo, en esta PC.
#
# Es el hermano comodo de `leer_serial.ps1`: aquel vuelca todo lo que sale por el
# puerto —incluido el ruido del controlador de WiFi y el arranque del chip— porque
# su trabajo es dejar un registro de evidencia. Este, en cambio, esta pensado para
# mirar: descarta lo que no son lecturas y muestra con la hora local solo lo que
# informa el firmware.
#
# Uso:
#   pwsh -File ver_lecturas.ps1
#   pwsh -File ver_lecturas.ps1 -Puerto COM7
#   pwsh -File ver_lecturas.ps1 -Segundos 120     # se detiene solo (para pruebas)
#
# Como el modulo mide cada cinco minutos, lo mas comodo es apretar RESET en la
# placa: a los pocos segundos del arranque hace el primer ciclo y aparecen las
# lecturas. Si no, hay que esperar al ciclo siguiente.
#
# No se tocan DTR ni RTS: en las placas ESP32 esas lineas estan conectadas al
# circuito de reinicio y activarlas reinicia el chip o lo deja en modo grabacion.
#
# Si el puerto devuelve el mismo contenido del buffer a un ritmo imposible —algo
# que pasa cuando el controlador queda trabado—, se cierra y se reabre solo, como
# si se desenchufara y volviera a enchufar el cable.

param(
    [string]$Puerto = "COM6",
    [int]$Velocidad = 115200,
    [int]$Recuperaciones = 3,
    [int]$Segundos = 0,
    [switch]$Crudo
)

$ErrorActionPreference = 'Continue'

function Abrir-Puerto {
    $p = New-Object System.IO.Ports.SerialPort($Puerto, $Velocidad, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
    $p.DtrEnable = $false
    $p.RtsEnable = $false
    $p.ReadTimeout = 1000
    $p.Open()
    return $p
}

# Lo que interesa lleva la etiqueta SIGVACH; tambien se muestran la deteccion de
# sensores, el estado de la cola y la conexion de red.
#
# El criterio es una LISTA DE LO PERMITIDO, no una lista de lo prohibido. La
# diferencia importa: cuando el controlador del puerto se traba, devuelve el mismo
# fragmento —«acenada», el final de «almacenada»— miles de veces por segundo, y un
# fragmento suelto no se parece a nada conocido, asi que cualquier lista de ruido
# lo deja pasar. Con lo permitido, en cambio, solo se ve lo que se reconoce.
$etiqueta = 'SIGVACH:\s*'
$permitidos = 'SIGVACH:|\(\d+\) (COLA|SENSORES):|wifi:connected with|wifi:state:|esp_netif_handlers: sta ip'

Write-Host ""
Write-Host ("  Lecturas de los sensores · puerto {0} · {1} baudios" -f $Puerto, $Velocidad) -ForegroundColor Green
Write-Host "  Sale con Ctrl + C. Si no aparece nada, apreta RESET en la placa." -ForegroundColor DarkGray
Write-Host ""

try {
    $serial = Abrir-Puerto
} catch {
    Write-Host ("  No se pudo abrir {0}: {1}" -f $Puerto, $_.Exception.Message) -ForegroundColor Red
    Write-Host "  Cerrá el programa que lo esté usando y volvé a intentar." -ForegroundColor DarkGray
    exit 1
}

$buffer = New-Object byte[] 4096
$pendiente = ""
$bytes = 0
$inicio = Get-Date
$techo = [math]::Round($Velocidad / 10 * 1.05)
$reintentos = 0
$fin = if ($Segundos -gt 0) { (Get-Date).AddSeconds($Segundos) } else { $null }

function Mostrar-Linea([string]$linea) {
    $hora = Get-Date -Format "HH:mm:ss"

    # Con -Crudo se muestra todo, tal como sale del puerto.
    if (-not $Crudo -and $linea -notmatch $permitidos) { return }

    $coincidencia = [regex]::Match($linea, $etiqueta + '(.*)$')
    if (-not $coincidencia.Success) {
        Write-Host ("  [{0}] {1}" -f $hora, $linea) -ForegroundColor DarkGray
        return
    }

    $mensaje = $coincidencia.Groups[1].Value.TrimEnd()
    if (-not $mensaje) { return }

    # Las lecturas se destacan; los avisos de red van en amarillo para no taparlas.
    if ($mensaje -match '^(Ambiente|Solucion|pH|TDS)\s*->|^\s*->') {
        Write-Host ("  [{0}] {1}" -f $hora, $mensaje) -ForegroundColor White
    }
    elseif ($mensaje -match 'Conectado|Conectando') {
        Write-Host ("  [{0}] {1}" -f $hora, $mensaje) -ForegroundColor Green
    }
    elseif ($mensaje -match 'caido|Sin red|cola|reintenta') {
        Write-Host ("  [{0}] {1}" -f $hora, $mensaje) -ForegroundColor Yellow
    }
    else {
        Write-Host ("  [{0}] {1}" -f $hora, $mensaje) -ForegroundColor DarkGray
    }
}

try {
    while ($true) {
        if ($fin -and (Get-Date) -ge $fin) {
            Write-Host ""
            Write-Host ("  Fin de los {0} segundos pedidos." -f $Segundos) -ForegroundColor DarkGray
            break
        }
        try {
            $leidos = $serial.Read($buffer, 0, $buffer.Length)
        } catch [System.TimeoutException] {
            continue
        } catch {
            Write-Host ("  Error de lectura: {0}" -f $_.Exception.Message) -ForegroundColor Red
            break
        }
        if ($leidos -le 0) { continue }

        $bytes += $leidos
        if ($bytes -gt 100000) {
            $transcurrido = ((Get-Date) - $inicio).TotalSeconds
            if ($transcurrido -gt 1) {
                $ritmo = [math]::Round($bytes / $transcurrido)
                if ($ritmo -gt $techo) {
                    $reintentos++
                    if ($reintentos -gt $Recuperaciones) {
                        Write-Host ""
                        Write-Host ("  El puerto sigue devolviendo datos imposibles ({0} caracteres por segundo)." -f $ritmo) -ForegroundColor Red
                        Write-Host "  Desenchufá el USB y volvé a enchufarlo." -ForegroundColor Red
                        break
                    }
                    Write-Host ""
                    Write-Host ("  El puerto se trabó; se reinicia la conexión ({0} de {1})." -f $reintentos, $Recuperaciones) -ForegroundColor Yellow
                    try { $serial.Close(); $serial.Dispose() } catch { }
                    Start-Sleep -Seconds 2
                    try { $serial = Abrir-Puerto } catch { Write-Host "  No se pudo reabrir el puerto." -ForegroundColor Red; break }
                    $pendiente = ""
                    $bytes = 0
                    $inicio = Get-Date
                    continue
                }
            }
        }

        # El firmware escribe en UTF-8: los grados de «°C» son dos bytes, y si se
        # decodifican como ASCII aparecen como «??C». Por eso se decodifica en UTF-8.
        $pendiente += [System.Text.Encoding]::UTF8.GetString($buffer, 0, $leidos)

        while ($true) {
            $corte = $pendiente.IndexOf("`n")
            if ($corte -lt 0) { break }
            $linea = $pendiente.Substring(0, $corte).TrimEnd("`r")
            $pendiente = $pendiente.Substring($corte + 1)
            if ($linea) { Mostrar-Linea $linea }
        }
    }
}
finally {
    try { $serial.Close(); $serial.Dispose() } catch { }
    Write-Host ""
    Write-Host "  Fin del visor." -ForegroundColor DarkGray
    Write-Host ""
}
