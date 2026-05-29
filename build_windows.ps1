param(
    [string]$AppName = "AuroraLiteBrowser",
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$DistDir = Join-Path $ProjectRoot "dist"
$BuildRoot = Join-Path $ProjectRoot "build"
$PyInstallerDist = Join-Path $BuildRoot "pyinstaller-dist"
$PyInstallerWork = Join-Path $BuildRoot "pyinstaller-work"
$SpecDir = Join-Path $BuildRoot "spec"

function Assert-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    if (-not $pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside the project root: $pathFull"
    }
}

function Copy-IfExists {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
}

foreach ($path in @($DistDir, $BuildRoot)) {
    Assert-PathUnderRoot -Path $path -Root $ProjectRoot
}

if (-not $NoClean) {
    foreach ($path in @($DistDir, $PyInstallerDist, $PyInstallerWork, $SpecDir)) {
        Assert-PathUnderRoot -Path $path -Root $ProjectRoot
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Recurse -Force
        }
    }
}

New-Item -ItemType Directory -Path $DistDir, $PyInstallerDist, $PyInstallerWork, $SpecDir -Force | Out-Null

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", $AppName,
    "--distpath", $PyInstallerDist,
    "--workpath", $PyInstallerWork,
    "--specpath", $SpecDir,
    "--add-data", "$(Join-Path $ProjectRoot 'assets');assets",
    "--add-data", "$(Join-Path $ProjectRoot 'config');config",
    (Join-Path $ProjectRoot "main.py")
)

Write-Host "Building $AppName with PyInstaller..."
python @pyInstallerArgs

$packagedAppDir = Join-Path $PyInstallerDist $AppName
if (-not (Test-Path -LiteralPath $packagedAppDir)) {
    throw "PyInstaller did not create the expected folder: $packagedAppDir"
}

Write-Host "Staging InstallForge release folder..."
Copy-Item -Path (Join-Path $packagedAppDir "*") -Destination $DistDir -Recurse -Force
Copy-IfExists -Source (Join-Path $ProjectRoot "assets") -Destination (Join-Path $DistDir "assets")
Copy-IfExists -Source (Join-Path $ProjectRoot "config") -Destination (Join-Path $DistDir "config")

$readme = @"
Aurora Lite Browser
===================

This folder is ready to import into InstallForge.

Main executable:
  $AppName.exe

Include these release-folder items:
  $AppName.exe
  _internal\
  assets\
  config\
  README.txt

Runtime data location:
  %APPDATA%\AuroraLiteBrowser

No post-install commands are required.
"@

Set-Content -LiteralPath (Join-Path $DistDir "README.txt") -Value $readme -Encoding UTF8

Write-Host ""
Write-Host "Done. InstallForge release folder:"
Write-Host "  $DistDir"
Write-Host ""
Write-Host "Select this executable as the main program:"
Write-Host "  $(Join-Path $DistDir ($AppName + '.exe'))"
