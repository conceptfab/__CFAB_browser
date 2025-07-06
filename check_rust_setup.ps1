# PowerShell script do sprawdzania konfiguracji Rust + PyO3
# Sprawdzanie kompletności konfiguracji dla migracji Scanner → Rust

Write-Host "=============================================" -ForegroundColor Blue
Write-Host " CHECKER KONFIGURACJI RUST + PyO3" -ForegroundColor Blue
Write-Host " Sprawdzanie kompletności konfiguracji" -ForegroundColor Blue
Write-Host "=============================================" -ForegroundColor Blue
Write-Host ""

# Sprawdź czy Python jest dostępny
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python dostępny: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python nie jest zainstalowany lub nie jest w PATH" -ForegroundColor Red
        Write-Host "Zainstaluj Python z python.org" -ForegroundColor Yellow
        Read-Host "Naciśnij Enter aby kontynuować"
        exit 1
    }
} catch {
    Write-Host "✗ Błąd sprawdzania Python: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Naciśnij Enter aby kontynuować"
    exit 1
}

# Uruchom checker
Write-Host "Uruchamianie checker-a..." -ForegroundColor Cyan
Write-Host ""

try {
    python check_rust_setup.py
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "=============================================" -ForegroundColor Green
        Write-Host " SUKCES: Konfiguracja jest kompletna!" -ForegroundColor Green
        Write-Host "=============================================" -ForegroundColor Green
    } else {
        Write-Host "=============================================" -ForegroundColor Red
        Write-Host " BŁĄD: Konfiguracja wymaga poprawek" -ForegroundColor Red
        Write-Host "=============================================" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Błąd uruchamiania checker-a: $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Read-Host "Naciśnij Enter aby zakończyć"
exit $exitCode 