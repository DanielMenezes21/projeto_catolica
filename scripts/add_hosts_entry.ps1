Param(
  [string]$Hostname = "myapp.local",
  [string]$IP
)

# Verifica se está sendo executado como Administrador
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
  Write-Warning "Este script precisa ser executado como Administrador. Reinicie o PowerShell como Administrador e execute novamente."
  exit 1
}

# Se o IP não foi passado, tenta descobrir um IP IPv4 local
if (-not $IP) {
  try {
    $IP = (Get-NetIPAddress -AddressFamily IPv4 |
           Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.IPAddress -notlike '169.*' -and $_.PrefixOrigin -ne 'WellKnown' } |
           Select-Object -First 1 -ExpandProperty IPAddress)
  } catch {
    $IP = $null
  }

  if (-not $IP) {
    # fallback para ipconfig parsing
    $ipLine = (ipconfig | Select-String -Pattern 'IPv4.*?:\s*([0-9\.]+)') | Select-Object -First 1
    if ($ipLine) {
      $m = [regex]::Match($ipLine.ToString(), '([0-9]{1,3}\.){3}[0-9]{1,3}')
      if ($m.Success) { $IP = $m.Value }
    }
  }

  if (-not $IP) {
    Write-Error "Não foi possível determinar o IP local automaticamente. Passe o parâmetro -IP. Ex: -IP 192.168.1.10"
    exit 1
  }
}

$hostsPath = "${env:SystemRoot}\System32\drivers\etc\hosts"
$entry = "$IP`t$Hostname"

# Verifica se já existe uma entrada exatamente igual
$exactPattern = "^\s*{0}\s+{1}\s*$" -f [regex]::Escape($IP), [regex]::Escape($Hostname)
if (Select-String -Path $hostsPath -Pattern $exactPattern -Quiet) {
  Write-Host "Entrada já existe no arquivo hosts: $entry"
  exit 0
}

# Se existir alguma entrada com o hostname, avisa e mostra o trecho para revisão
if (Select-String -Path $hostsPath -Pattern ([regex]::Escape($Hostname)) -Quiet) {
  Write-Warning "Já existe uma entrada para '$Hostname' no arquivo hosts (possivelmente com IP diferente). Verifique manualmente: $hostsPath"
  Select-String -Path $hostsPath -Pattern ([regex]::Escape($Hostname)) | ForEach-Object { Write-Host $_.Line }
  exit 0
}

# Adiciona a entrada
try {
  Add-Content -Path $hostsPath -Value "`n# Added by projeto_catolica script`n$entry"
  Write-Host "Entrada adicionada com sucesso: $entry"
  Write-Host "(Execute 'ipconfig /flushdns' se precisar limpar cache DNS no cliente.)"
} catch {
  Write-Error "Falha ao escrever em $hostsPath $_"
  exit 1
}