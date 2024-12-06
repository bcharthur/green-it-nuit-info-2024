# setup_and_run.ps1

# Vérifier si Chocolatey est installé
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey n'est pas installé. Installation en cours..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = `
        [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "Chocolatey est déjà installé."
}

# Installer Docker Desktop via Chocolatey
Write-Host "Installation de Docker Desktop..."
choco install docker-desktop -y

# Démarrer Docker Desktop
Write-Host "Démarrage de Docker Desktop..."
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Attendre que Docker soit prêt
Write-Host "Attente que Docker soit prêt..."
Start-Sleep -Seconds 30  # Ajustez le temps d'attente selon votre machine

# Vérifier si Docker est installé
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker n'a pas pu être installé. Veuillez vérifier les erreurs ci-dessus."
    exit 1
} else {
    Write-Host "Docker est installé et en cours d'exécution."
}

# Installer Docker Compose (si nécessaire)
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Installation de Docker Compose..."
    choco install docker-compose -y
} else {
    Write-Host "Docker Compose est déjà installé."
}

# Construire et démarrer les conteneurs avec Docker Compose
Write-Host "Construction et démarrage des conteneurs avec Docker Compose..."
docker-compose up --build -d

# Vérifier l'état des conteneurs
docker ps

Write-Host "Application Flask et SQL Server sont en cours d'exécution."
