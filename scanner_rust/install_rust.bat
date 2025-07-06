@echo off
echo Installing Rust for CFAB Browser Rust Scanner...
echo.

:: Check if Rust is already installed
where rustc >nul 2>nul
if %errorlevel% equ 0 (
    echo Rust is already installed!
    rustc --version
    echo.
    goto :check_maturin
)

:: Download and install Rust
echo Downloading Rust installer...
curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs -o rustup-init.exe
if %errorlevel% neq 0 (
    echo ERROR: Failed to download Rust installer
    echo Please check your internet connection
    pause
    exit /b 1
)

echo Installing Rust...
rustup-init.exe -y --default-toolchain stable
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Rust
    pause
    exit /b 1
)

:: Add Rust to PATH for current session
set PATH=%USERPROFILE%\.cargo\bin;%PATH%

:: Clean up installer
del rustup-init.exe

echo.
echo Rust installed successfully!
rustc --version
echo.

:check_maturin
:: Check if maturin is installed
where maturin >nul 2>nul
if %errorlevel% equ 0 (
    echo maturin is already installed!
    maturin --version
    echo.
    goto :build_scanner
)

:: Install maturin
echo Installing maturin...
pip install maturin
if %errorlevel% neq 0 (
    echo ERROR: Failed to install maturin
    echo Please make sure Python and pip are installed
    pause
    exit /b 1
)

echo.
echo maturin installed successfully!
maturin --version
echo.

:build_scanner
echo All dependencies installed!
echo.
echo You can now build the scanner with:
echo   build.bat
echo.
echo Or run the benchmark with:
echo   python benchmark.py
echo.
pause 