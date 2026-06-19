<#
.SYNOPSIS
    Cree et configure le serveur MySQL local du projet (version Windows / PowerShell).

.DESCRIPTION
    Equivalent de scripts/setup_mysql.sh pour Windows. Idempotent :
      1. cree la base flask_stats + la table donnees (via sql/init_db.sql)
      2. cree l'utilisateur applicatif et lui donne les droits
      3. genere les fichiers .env des services 3 et 4 (fins de ligne LF)

    Prerequis : un serveur MySQL demarre, et le client mysql.exe dans le PATH.
    Si mysql.exe n'est pas trouve, le script indique comment l'ajouter au PATH.

.EXAMPLE
    .\scripts\setup_mysql.ps1

.EXAMPLE
    # Si le compte root a un mot de passe :
    .\scripts\setup_mysql.ps1 -MysqlAdminPassword 'monmdp'

.NOTES
    Si l'execution de scripts est bloquee :
      powershell -ExecutionPolicy Bypass -File .\scripts\setup_mysql.ps1
#>
param(
    [string]$DbName             = $(if ($env:DB_NAME)  { $env:DB_NAME }  else { 'flask_stats' }),
    [string]$DbUser             = $(if ($env:DB_USER)  { $env:DB_USER }  else { 'flask_user' }),
    [string]$DbPassword         = $(if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { 'flask_pwd' }),
    [string]$DbHost             = $(if ($env:DB_HOST)  { $env:DB_HOST }  else { 'localhost' }),
    [string]$DbPort             = $(if ($env:DB_PORT)  { $env:DB_PORT }  else { '3306' }),
    [string]$MysqlAdmin         = $(if ($env:MYSQL_ADMIN) { $env:MYSQL_ADMIN } else { 'root' }),
    [string]$MysqlAdminPassword = $(if ($env:MYSQL_ADMIN_PASSWORD) { $env:MYSQL_ADMIN_PASSWORD } else { '' })
)

$ErrorActionPreference = 'Stop'

# Force l'encodage UTF-8 (sans BOM) quand PowerShell envoie du texte a mysql.exe.
# Sans ca, Windows PowerShell 5.1 pipe en ASCII/CP1252 et corromprait tout
# caractere accentue passe a MySQL.
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)

# --- Repertoires ---------------------------------------------------------
$RootDir = Resolve-Path (Join-Path $PSScriptRoot '..')
$SqlFile = Join-Path $RootDir 'sql/init_db.sql'

# --- Arguments de connexion admin ----------------------------------------
# --default-character-set=utf8mb4 : mysql interprete l'entree comme de l'UTF-8.
$AdminArgs = @('-u', $MysqlAdmin, '-h', $DbHost, '-P', $DbPort, '--default-character-set=utf8mb4')
if ($MysqlAdminPassword -ne '') {
    $AdminArgs += "-p$MysqlAdminPassword"
}

function Invoke-MySql {
    param([string]$Sql)
    $Sql | & mysql @AdminArgs
    if ($LASTEXITCODE -ne 0) { throw "La commande mysql a echoue (code $LASTEXITCODE)." }
}

Write-Host '==> Verification du client mysql...'
if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR : 'mysql' est introuvable dans le PATH." -ForegroundColor Red
    Write-Host "         L'installateur MySQL n'ajoute pas toujours le client au PATH."
    Write-Host "         Ajoutez le dossier bin de MySQL, par exemple :"
    Write-Host '           setx PATH "%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin"'
    Write-Host '         puis rouvrez le terminal.'
    exit 1
}

Write-Host "==> Test de connexion au serveur MySQL ($MysqlAdmin@${DbHost}:$DbPort)..."
try {
    Invoke-MySql 'SELECT 1;' | Out-Null
} catch {
    Write-Host 'ERREUR : connexion impossible.' -ForegroundColor Red
    Write-Host '         - le serveur MySQL est-il demarre ? (Services Windows -> MySQL)'
    Write-Host "         - si root a un mot de passe : .\scripts\setup_mysql.ps1 -MysqlAdminPassword '...'"
    exit 1
}

if (-not (Test-Path $SqlFile)) {
    Write-Host "ERREUR : $SqlFile introuvable." -ForegroundColor Red
    exit 1
}

Write-Host '==> [1/3] Creation de la base et de la table (sql/init_db.sql)...'
Get-Content -Raw $SqlFile | & mysql @AdminArgs
if ($LASTEXITCODE -ne 0) { throw 'Echec de l execution de init_db.sql.' }

Write-Host "==> [2/3] Creation de l'utilisateur applicatif '$DbUser' et attribution des droits..."
$UserSql = @"
CREATE USER IF NOT EXISTS '$DbUser'@'localhost' IDENTIFIED BY '$DbPassword';
ALTER USER '$DbUser'@'localhost' IDENTIFIED BY '$DbPassword';
GRANT ALL PRIVILEGES ON ``$DbName``.* TO '$DbUser'@'localhost';
FLUSH PRIVILEGES;
"@
Invoke-MySql $UserSql

Write-Host '==> [3/3] Generation des fichiers .env (services 3 et 4)...'
$EnvLines = @(
    "DB_HOST=$DbHost",
    "DB_PORT=$DbPort",
    "DB_USER=$DbUser",
    "DB_PASSWORD=$DbPassword",
    "DB_NAME=$DbName"
)
# Fins de ligne LF + UTF-8 sans BOM (compatibles python-dotenv et cross-platform)
$EnvContent = ($EnvLines -join "`n") + "`n"
foreach ($svc in @('service3_stats_mysql', 'service4_csv_mysql')) {
    $EnvPath = Join-Path $RootDir (Join-Path $svc '.env')
    [System.IO.File]::WriteAllText($EnvPath, $EnvContent, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "    ecrit : $svc/.env"
}

Write-Host ''
Write-Host "==> Verification finale : contenu de la table '$DbName.donnees'"
Invoke-MySql "USE $DbName; SELECT nom_serie, COUNT(*) AS n_points FROM donnees GROUP BY nom_serie;"

Write-Host ''
Write-Host "Termine. La base '$DbName' est prete." -ForegroundColor Green
Write-Host 'Lance les services 3 et 4 :'
Write-Host '    cd service3_stats_mysql ; python app.py   # port 5003'
Write-Host '    cd service4_csv_mysql  ; python app.py    # port 5004'
