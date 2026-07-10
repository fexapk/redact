# Run Redact from a local virtual environment.

$ErrorActionPreference = "Stop"

$projectDir = $PSScriptRoot
$venvDir = Join-Path $projectDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $pythonCommand) {
    $pythonExecutable = $pythonCommand.Source
    $pythonArguments = @("-3")
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommand) {
        Write-Error "Python 3.11 or newer is required. Install Python, then run this script again."
        exit 1
    }

    $pythonExecutable = $pythonCommand.Source
    $pythonArguments = @()
}

& $pythonExecutable @pythonArguments -c "import sys; sys.exit(sys.version_info < (3, 11))"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 3.11 or newer is required. Install a supported Python version, then run this script again."
    exit 1
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating local virtual environment..."
    & $pythonExecutable @pythonArguments -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not create a virtual environment. Install your Python distribution's venv support, then run this script again."
        exit $LASTEXITCODE
    }
}

& $venvPython -c "import redact_app" *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Redact dependencies..."
    & $venvPython -m pip install --disable-pip-version-check --editable $projectDir
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

& $venvPython -m redact_app
exit $LASTEXITCODE
