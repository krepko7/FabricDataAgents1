[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Server,
    [Parameter(Mandatory)][string]$Database
)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Get-Command sqlcmd -ErrorAction Stop | Out-Null

# Microsoft Entra authentication; no passwords or tokens are written to disk.
foreach ($file in @('01_schema.sql', '02_seed.sql', '03_validate.sql')) {
    Write-Host "Running $file against $Server / $Database"
    & sqlcmd -S $Server -d $Database -G -N -b -r 1 -i (Join-Path $root "sql\$file")
    if ($LASTEXITCODE -ne 0) {
        throw "sqlcmd failed in $file (exit $LASTEXITCODE). Loading stopped."
    }
}
