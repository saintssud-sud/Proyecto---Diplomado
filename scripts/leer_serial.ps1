# Lee el Monitor Serie del ESP32 desde este equipo, sin abrir el entorno de ESP-IDF.
#
# Dos precauciones aprendidas a golpes:
#
#  1. NO se tocan DTR ni RTS. En las placas ESP32 esas lineas estan conectadas al
#     circuito de reinicio (EN y BOOT): activarlas reinicia la placa o la deja en
#     modo de grabacion.
#  2. Se leen BYTES y se arman las lineas a mano, en vez de usar ReadLine. Con
#     ReadLine aparecieron miles de lineas repetidas y cortadas ("acenada"), que
#     no eran lo que el modulo estaba informando.
#
# Uso:
#   pwsh -File leer_serial.ps1 -Puerto COM6 -Segundos 180
#
# La placa imprime una linea de depuracion del WiFi ("ssn:5, winSize:64") miles de
# veces por segundo, y tapa las lineas utiles. Con -Ocultar se descartan esas lineas
# y al final se informa cuantas se descartaron, para no perder la cuenta.
#
# Ademas, cuando el modulo se reinicia a medias, el buffer entrega el mismo fragmento
# repetido ("cenada", el final de "almacenada"). Las lineas identicas y consecutivas
# se cuentan y se informan una sola vez al final del bloque.
#
# Y hay un tercer caso: el puerto puede quedar atascado y devolver el MISMO contenido
# del buffer a toda velocidad. A 115200 baudios no pueden pasar mas de unos 11500
# caracteres por segundo, asi que si el ritmo medido supera ese techo, el dato no
# viene del cable: es el controlador que devuelve una y otra vez lo ultimo que tenia
# guardado.
#
# Antes, al detectar eso el escucha se detenia y el registro quedaba marcado como
# invalido: era lo correcto para no dar por bueno un registro falso, pero obligaba a
# desenchufar el USB cada vez. Ahora, antes de rendirse, CIERRA Y REABRE EL PUERTO,
# que es lo que hace el desenchufe, descarta el contenido trabado y sigue escuchando.
# Si tras -Recuperaciones intentos el puerto sigue devolviendo basura, entonces si se
# detiene y lo declara: un registro con artefactos no sirve como evidencia.

param(
    [string]$Puerto = "COM6",
    [int]$Segundos = 180,
    [int]$Velocidad = 115200,
    [string]$Ocultar = "^(ssn:)",
    [int]$Recuperaciones = 3
)

$ErrorActionPreference = 'Continue'

function Abrir-Puerto {
    $p = New-Object System.IO.Ports.SerialPort($Puerto, $Velocidad, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
    # Sin tocar las lineas de reinicio.
    $p.DtrEnable = $false
    $p.RtsEnable = $false
    $p.ReadTimeout = 1000
    $p.Open()
    return $p
}

try {
    $serial = Abrir-Puerto
} catch {
    Write-Host ("No se pudo preparar el puerto {0}: {1}" -f $Puerto, $_.Exception.Message)
    exit 1
}

Write-Host ("Escuchando {0} a {1} baudios durante {2} segundos. Pulsa RESET en la placa." -f $Puerto, $Velocidad, $Segundos)

$fin = (Get-Date).AddSeconds($Segundos)
$buffer = New-Object byte[] 4096
$pendiente = ""
$lineas = 0
$ocultas = 0
$repetidas = 0
$anterior = $null
$veces = 0
$bytes = 0
$inicio = Get-Date
$techo = [math]::Round($Velocidad / 10 * 1.05)
$artefacto = $false
$reintentos = 0

function Cerrar-Bloque {
    if ($script:veces -gt 1) {
        Write-Host ("        ... la linea anterior se repitio {0} veces" -f $script:veces)
        $script:repetidas += ($script:veces - 1)
    }
    $script:veces = 0
}

while ((Get-Date) -lt $fin) {
    try {
        $leidos = $serial.Read($buffer, 0, $buffer.Length)
    } catch [System.TimeoutException] {
        continue
    } catch {
        Write-Host ("Error de lectura: " + $_.Exception.Message)
        break
    }
    if ($leidos -le 0) { continue }

    $bytes += $leidos
    if ($bytes -gt 100000) {
        $transcurrido = ((Get-Date) - $inicio).TotalSeconds
        if ($transcurrido -gt 1) {
            $ritmo = [math]::Round($bytes / $transcurrido)
            if ($ritmo -gt $techo) {
                if ($reintentos -ge $Recuperaciones) {
                    Write-Host ("ALTO: el puerto entrego {0} caracteres por segundo y el techo del cable a {1} baudios es {2}, tras {3} intentos de recuperarlo." -f $ritmo, $Velocidad, $techo, $reintentos)
                    $artefacto = $true
                    break
                }

                $reintentos++
                Write-Host ("")
                Write-Host ("Nota: el puerto entrego {0} caracteres por segundo y el techo del cable es {1}. Es el bufer del controlador trabado, no el modulo: se cierra y se reabre el puerto para destrabarlo ({2} de {3})." -f $ritmo, $techo, $reintentos, $Recuperaciones)

                try { $serial.Close(); $serial.Dispose() } catch { }
                Start-Sleep -Seconds 2
                try {
                    $serial = Abrir-Puerto
                } catch {
                    Write-Host ("No se pudo reabrir el puerto: " + $_.Exception.Message)
                    $artefacto = $true
                    break
                }

                # El contenido trabado se descarta y se vuelve a medir el ritmo.
                $pendiente = ""
                $anterior = $null
                $veces = 0
                $bytes = 0
                $inicio = Get-Date
                Write-Host "Puerto reabierto; se sigue escuchando."
                Write-Host ""
                continue
            }
        }
    }

    # El firmware escribe en UTF-8: los grados de «°C» son dos bytes, y si se
    # decodifican como ASCII quedan como «??C» en el registro de evidencia.
    $pendiente += [System.Text.Encoding]::UTF8.GetString($buffer, 0, $leidos)

    while ($true) {
        $corte = $pendiente.IndexOf("`n")
        if ($corte -lt 0) { break }
        $linea = $pendiente.Substring(0, $corte).TrimEnd("`r")
        $pendiente = $pendiente.Substring($corte + 1)
        if ($linea) {
            if ($Ocultar -and $linea -match $Ocultar) {
                $ocultas++
                continue
            }
            if ($linea -eq $anterior) {
                $veces++
                continue
            }
            Cerrar-Bloque
            Write-Host $linea
            $anterior = $linea
            $veces = 1
            $lineas++
        }
    }
}

Cerrar-Bloque
try { $serial.Close(); $serial.Dispose() } catch { }
Write-Host ("--- fin del escucha: {0} linea(s) util(es) distinta(s), {1} repetida(s) y {2} descartada(s) por el filtro ---" -f $lineas, $repetidas, $ocultas)
if ($reintentos -gt 0) {
    Write-Host ("--- el puerto se destrabo {0} vez/veces durante el escucha; el contenido descartado no se cuenta ---" -f $reintentos)
}
if ($artefacto) {
    Write-Host "--- el registro NO es valido: el puerto siguio devolviendo mas datos de los que el cable puede llevar ---"
    exit 2
}
