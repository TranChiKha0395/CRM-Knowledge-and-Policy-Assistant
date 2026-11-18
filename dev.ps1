# dev.ps1 — Thay thế Makefile trên Windows
# Dùng: .\dev.ps1 <target>
param([string]$Target = "help")

$Root = $PSScriptRoot

function Invoke-DevDB {
    Write-Host "Starting dev databases (PostgreSQL+pgvector, Redis)..." -ForegroundColor Cyan
    docker compose up -d db redis
}

function Invoke-Up {
    Write-Host "Starting all services (--profile app)..." -ForegroundColor Cyan
    docker compose --profile app up -d
}

function Invoke-Down {
    Write-Host "Stopping all services..." -ForegroundColor Cyan
    docker compose --profile app down
}

function Invoke-Logs {
    docker compose logs -f
}

function Invoke-Lint {
    Write-Host "Running backend & worker lint..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    try {
        python -m ruff check .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        python -m mypy src
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        python -m compileall -q ../worker/src
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Set-Location $Root
    }
}

function Invoke-CheckCsv {
    Write-Host "Validating template CSV contracts..." -ForegroundColor Cyan
    Set-Location $Root
    @'
import csv
import pathlib
import sys

checks = [
    ("data/templates/passages_template.csv", 21),
    ("data/templates/critical_fields_template.csv", 23),
]
errors = []
for path_str, expected_cols in checks:
    rows = list(csv.reader(pathlib.Path(path_str).read_text(encoding="utf-8-sig").splitlines()))
    cols = rows[0] if rows else []
    if len(cols) != expected_cols:
        errors.append(f"{path_str}: expected {expected_cols} cols, got {len(cols)}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("Template CSV contracts valid")
'@ | python -
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Invoke-Test {
    Write-Host "Running backend tests..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    try {
        python -m pytest -q
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Set-Location $Root
    }
}

function Invoke-Migrate {
    Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    try {
        python -m alembic upgrade head
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Set-Location $Root
    }
}

function Invoke-Dev {
    Write-Host "Starting FastAPI dev server on http://localhost:8000..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    Set-Location $Root
}

function Invoke-Help {
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 <target>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Targets:"
    Write-Host "  dev-db      Start PostgreSQL+pgvector, Redis"
    Write-Host "  dev         Start FastAPI backend dev server (uvicorn --reload)"
    Write-Host "  up          Start all containerized services (--profile app)"
    Write-Host "  down        Stop all services"
    Write-Host "  logs        Tail logs"
    Write-Host "  lint        Run ruff, mypy, and worker compileall"
    Write-Host "  check-csv   Validate UTF-8 CSV template headers"
    Write-Host "  test        Run pytest"
    Write-Host "  migrate     Run alembic upgrade head"
    Write-Host ""
}

switch ($Target) {
    "dev-db"      { Invoke-DevDB }
    "dev"         { Invoke-Dev }
    "start"       { Invoke-Dev }
    "up"          { Invoke-Up }
    "down"        { Invoke-Down }
    "logs"        { Invoke-Logs }
    "lint"        { Invoke-Lint }
    "check-csv"   { Invoke-CheckCsv }
    "test"        { Invoke-Test }
    "migrate"     { Invoke-Migrate }
    default       { Invoke-Help }
}

