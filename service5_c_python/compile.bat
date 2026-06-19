@echo off
REM compile.bat - Compile src\stats.c en bibliotheque partagee lib\stats.dll (Windows)
REM Prerequis : gcc (MinGW-w64 ou MSYS2) dans le PATH.
REM Usage (CMD ou PowerShell, depuis le dossier service5_c_python) :
REM    compile.bat

setlocal

where gcc >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] gcc introuvable dans le PATH.
    echo          Installez MinGW-w64 ^(https://www.mingw-w64.org^) ou MSYS2,
    echo          puis ajoutez le dossier bin\ contenant gcc.exe au PATH.
    exit /b 1
)

if not exist lib mkdir lib

echo [1/2] Compilation de src\stats.c -^> lib\stats.dll...
REM Sous MinGW : pas de -fPIC (ignore), mais -lm requis pour sqrt() (link de math.h)
gcc -shared -O2 -Wall -o lib\stats.dll src\stats.c -lm
if errorlevel 1 (
    echo [ERREUR] La compilation a echoue.
    exit /b 1
)

echo [2/2] Bibliotheque creee : lib\stats.dll
echo Compilation reussie !
endlocal
