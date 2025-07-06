@echo off
echo Building Rust Scanner for CFAB Browser...
echo.

:: Check if Rust is installed
where rustc >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Rust is not installed or not in PATH
    echo Please install Rust from https://rustup.rs/
    pause
    exit /b 1
)

:: Check if maturin is installed
where maturin >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing maturin...
    pip install maturin
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install maturin
        pause
        exit /b 1
    )
)

:: Build development version
echo Building development version...
maturin develop --release
if %errorlevel% neq 0 (
    echo ERROR: Failed to build development version
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo You can now import scanner_rust in Python
echo.
pause 