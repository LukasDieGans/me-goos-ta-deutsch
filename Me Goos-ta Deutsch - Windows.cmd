@echo off
rem ===========================================================================
rem  Me Goos-ta Deutsch - start for Windows                        Version 2.2
rem
rem  Just double-click. The first start sets everything up: a Python of its
rem  own in your user folder (no administrator rights needed) and the packages
rem  (tools only on request). Then the interface opens in the browser, and the
rem  icon "Me Goos-ta Deutsch" sits on the desktop. Honk if you like it!
rem
rem  Python comes as the official, signed "embeddable" package from python.org;
rem  its SHA-256 checksum is verified. Location:
rem    %LOCALAPPDATA%\Me-Goos-ta-Deutsch\python
rem  Everything else is done by Programm\starter.py (with a log in that folder).
rem
rem  Messages are in English; once a language is chosen in the program, they
rem  follow that choice (German / English / Spanish).
rem
rem  Deliberately ASCII only, Windows line endings and no bracket blocks with
rem  paths: so the file also works in folders with spaces, brackets, "&" or
rem  umlauts in the name.
rem ===========================================================================
setlocal EnableExtensions DisableDelayedExpansion
title Me Goos-ta Deutsch
set "PY_VER=3.13.16"
set "PY_SHA=97dae5274cc54867065e8d5a3226e48c35017ed332a0fdb0e27d5b5821961297"
set "PY_URL=https://www.python.org/ftp/python/3.13.16/python-3.13.16-embed-amd64.zip"
set "SYS32=%SystemRoot%\System32"
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONSTARTUP="

rem --- Sprache der Meldungen: Englisch, nach der ersten Wahl die im Programm gewaehlte (de / en / es) ---
set "SPR=en"
"%SYS32%\findstr.exe" /l /c:"\"sprache\": \"de\"" "%~dp0Programm\ui_einstellungen.json" >nul 2>&1
if not errorlevel 1 set "SPR=de"
"%SYS32%\findstr.exe" /l /c:"\"sprache\": \"es\"" "%~dp0Programm\ui_einstellungen.json" >nul 2>&1
if not errorlevel 1 set "SPR=es"
call :texte_%SPR%

rem --- Wurde die ZIP-Datei entpackt? (Doppelklick in der ZIP startet nur diese eine Datei) ---
cd /d "%~dp0"
if not exist "%~dp0Programm\starter.py" goto :nicht_entpackt
set "MGD_PROGRAMM=%~dp0Programm"

rem --- 64-Bit-Windows? (ARM-Rechner nutzen die x64-Fassung ueber die eingebaute Emulation) ---
set "ARCH=%PROCESSOR_ARCHITECTURE%"
if defined PROCESSOR_ARCHITEW6432 set "ARCH=%PROCESSOR_ARCHITEW6432%"
if /i "%ARCH%"=="x86" goto :x86

rem --- Eigenes Python vorhanden und funktionsfaehig? Dann direkt starten. ---
set "BASIS=%LOCALAPPDATA%"
if not defined BASIS set "BASIS=%USERPROFILE%\AppData\Local"
set "MGD_DATEN=%BASIS%\Me-Goos-ta-Deutsch"
set "PYDIR=%BASIS%\Me-Goos-ta-Deutsch\python"
set "PY=%BASIS%\Me-Goos-ta-Deutsch\python\python.exe"
if not exist "%PY%" goto :python_einrichten
"%PY%" -c "import sys, ssl, ctypes" >nul 2>&1
if errorlevel 1 goto :python_einrichten
goto :starten

rem ===========================================================================
rem  Erster Start: Python laden, pruefen, entpacken
rem ===========================================================================
:python_einrichten
echo.
echo   %T_KOPF%
echo   %T_PY%
echo.
if not exist "%MGD_DATEN%\" mkdir "%MGD_DATEN%" >nul 2>&1
if not exist "%MGD_DATEN%\" goto :fehler_ordner
set "MGD_ZIP=%MGD_DATEN%\python-%PY_VER%-embed-amd64.zip"
set "MGD_TEIL=%MGD_DATEN%\python-%PY_VER%-embed-amd64.zip.part"
set "MGD_NEU=%MGD_DATEN%\python-neu"
if exist "%MGD_ZIP%" goto :pruefen

:laden
echo   %T_LADE%
if exist "%MGD_TEIL%" del /f /q "%MGD_TEIL%" >nul 2>&1
if not exist "%SYS32%\curl.exe" goto :laden_ps
"%SYS32%\curl.exe" -fL --retry 3 --retry-delay 3 --connect-timeout 30 --progress-bar -o "%MGD_TEIL%" "%PY_URL%"
if not errorlevel 1 goto :geladen
:laden_ps
rem Rueckfall: PowerShell nutzt auch die Proxy-Einstellungen von Windows
"%PS%" -NoProfile -NonInteractive -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -UseBasicParsing -Uri $env:PY_URL -OutFile $env:MGD_TEIL; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 goto :fehler_netz
:geladen
if not exist "%MGD_TEIL%" goto :fehler_netz
move /y "%MGD_TEIL%" "%MGD_ZIP%" >nul
if not exist "%MGD_ZIP%" goto :fehler_ordner

:pruefen
echo   %T_PRUEFE%
set "HASH="
for /f "skip=1 delims=" %%h in ('%SYS32%\certutil.exe -hashfile "%MGD_ZIP%" SHA256 2^>nul') do if not defined HASH set "HASH=%%h"
if defined HASH set "HASH=%HASH: =%"
if /i "%HASH%"=="%PY_SHA%" goto :pruefsumme_ok
set "HASH="
for /f "delims=" %%h in ('%PS% -NoProfile -NonInteractive -Command "$h = Get-FileHash -Algorithm SHA256 -LiteralPath $env:MGD_ZIP; $h.Hash"') do set "HASH=%%h"
if /i "%HASH%"=="%PY_SHA%" goto :pruefsumme_ok
del /f /q "%MGD_ZIP%" >nul 2>&1
goto :fehler_pruefsumme

:pruefsumme_ok
echo   %T_ENTPACKE%
if exist "%MGD_NEU%\" rd /s /q "%MGD_NEU%" >nul 2>&1
mkdir "%MGD_NEU%" >nul 2>&1
"%SYS32%\tar.exe" -xf "%MGD_ZIP%" -C "%MGD_NEU%" >nul 2>&1
if exist "%MGD_NEU%\python.exe" goto :entpackt
"%PS%" -NoProfile -NonInteractive -Command "Expand-Archive -LiteralPath $env:MGD_ZIP -DestinationPath $env:MGD_NEU -Force"
if not exist "%MGD_NEU%\python.exe" goto :fehler_entpacken

:entpackt
rem python313._pth: Pakete aus Lib\site-packages erlauben (sonst ignoriert das embeddable Python sie)
(
echo python313.zip
echo .
echo Lib\site-packages
echo import site
) > "%MGD_NEU%\python313._pth"
mkdir "%MGD_NEU%\Lib\site-packages" >nul 2>&1
"%MGD_NEU%\python.exe" -c "import sys, ssl, ctypes" >nul 2>&1
if errorlevel 1 goto :fehler_python
> "%MGD_NEU%\mgd-version.txt" echo %PY_VER%
if exist "%PYDIR%\" rd /s /q "%PYDIR%" >nul 2>&1
if exist "%PYDIR%\" goto :fehler_besetzt
rem Verschieben kann kurz scheitern ("Zugriff verweigert"), solange der Virenscanner das frische Python noch
rem prueft - vor allem auf ARM-Rechnern. Dann bis zu 15-mal nach 2 Sekunden neu versuchen.
set "VERSUCH=0"
:verschieben
move "%MGD_NEU%" "%PYDIR%" >nul 2>&1
if exist "%PY%" goto :verschoben
set /a VERSUCH+=1
if %VERSUCH% GEQ 15 goto :fehler_entpacken
"%SYS32%\ping.exe" -n 3 127.0.0.1 >nul
goto :verschieben
:verschoben
del /f /q "%MGD_ZIP%" >nul 2>&1
echo   %T_OK%

rem ===========================================================================
rem  Start: starter.py erkennt den ersten Start und richtet den Rest ein
rem ===========================================================================
:starten
"%PY%" "%MGD_PROGRAMM%\starter.py" --konsole %*
if errorlevel 1 goto :ende_fehler
exit /b 0

:ende_fehler
echo.
pause
exit /b 1

rem ===========================================================================
rem  Probleme
rem ===========================================================================
:nicht_entpackt
echo.
echo   %T_ZIP1%
echo   %T_ZIP2%
echo   %T_ZIP3%
goto :ende_fehler

:x86
echo.
echo   %T_X86%
goto :ende_fehler

:fehler_ordner
echo.
echo   %T_ORDNER%
echo   %MGD_DATEN%
goto :ende_fehler

:fehler_netz
if exist "%MGD_TEIL%" del /f /q "%MGD_TEIL%" >nul 2>&1
echo.
echo   %T_NETZ1%
echo   %T_NETZ2%
goto :ende_fehler

:fehler_pruefsumme
echo.
echo   %T_SUMME%
goto :ende_fehler

:fehler_entpacken
echo.
echo   %T_ENTPACKEN%
goto :ende_fehler

:fehler_python
echo.
echo   %T_PYTHON%
goto :ende_fehler

:fehler_besetzt
echo.
echo   %T_BESETZT%
goto :ende_fehler

rem ===========================================================================
rem  Texte (nur ASCII - Umlaute waeren je nach Codepage unleserlich)
rem ===========================================================================
:texte_de
set "T_KOPF=Me Goos-ta Deutsch - Lernkarten zum Ausdrucken"
set "T_PY=Erster Start: Python wird eingerichtet - 11 MB von python.org, ohne Administratorrechte."
set "T_LADE=Lade Python ..."
set "T_PRUEFE=Kontrolliere die Datei ..."
set "T_ENTPACKE=Entpacke Python ..."
set "T_OK=Python ist bereit."
set "T_ZIP1=Bitte zuerst die ZIP-Datei entpacken:"
set "T_ZIP2=Rechtsklick auf die ZIP-Datei - 'Alle extrahieren...' - 'Extrahieren'."
set "T_ZIP3=Dann im neuen Ordner 'Me Goos-ta Deutsch - Windows' doppelklicken."
set "T_X86=Dieses Windows ist ein 32-Bit-System. Me Goos-ta Deutsch braucht Windows 10 oder 11 mit 64 Bit."
set "T_ORDNER=Dieser Ordner kann nicht angelegt oder beschrieben werden:"
set "T_NETZ1=Python konnte nicht geladen werden - keine Internetverbindung?"
set "T_NETZ2=Nur beim ersten Start wird Internet gebraucht, danach geht alles auch ohne. Bitte Verbindung pruefen und noch einmal starten."
set "T_SUMME=Die geladene Datei ist fehlerhaft - falsche Kontrollsumme. Bitte noch einmal starten."
set "T_ENTPACKEN=Python konnte nicht entpackt werden. Bitte noch einmal starten."
set "T_PYTHON=Python startet nicht. Vielleicht blockiert ein Virenschutz das Programm - siehe 'LIES MICH ZUERST'."
set "T_BESETZT=Das alte Python wird noch benutzt. Bitte alle Fenster von Me Goos-ta Deutsch schliessen und noch einmal starten."
exit /b 0

:texte_en
set "T_KOPF=Me Goos-ta Deutsch - printable flashcards"
set "T_PY=First start: setting up Python - 11 MB from python.org, no administrator rights needed."
set "T_LADE=Downloading Python ..."
set "T_PRUEFE=Checking the file ..."
set "T_ENTPACKE=Unpacking Python ..."
set "T_OK=Python is ready."
set "T_ZIP1=Please extract the ZIP file first:"
set "T_ZIP2=Right-click the ZIP file - 'Extract All...' - 'Extract'."
set "T_ZIP3=Then double-click 'Me Goos-ta Deutsch - Windows' in the new folder."
set "T_X86=This is a 32-bit Windows. Me Goos-ta Deutsch needs 64-bit Windows 10 or 11."
set "T_ORDNER=This folder cannot be created or written:"
set "T_NETZ1=Python could not be downloaded - no internet connection?"
set "T_NETZ2=Internet is only needed on the first start, afterwards everything works offline. Please check the connection and start again."
set "T_SUMME=The downloaded file is damaged - wrong checksum. Please start again."
set "T_ENTPACKEN=Python could not be unpacked. Please start again."
set "T_PYTHON=Python does not start. Maybe an antivirus blocks it - see 'LIES MICH ZUERST'."
set "T_BESETZT=The old Python is still in use. Please close all Me Goos-ta Deutsch windows and start again."
exit /b 0

:texte_es
set "T_KOPF=Me Goos-ta Deutsch - tarjetas para imprimir"
set "T_PY=Primer inicio: se instala Python - 11 MB de python.org, sin permisos de administrador."
set "T_LADE=Descargando Python ..."
set "T_PRUEFE=Revisando el archivo ..."
set "T_ENTPACKE=Descomprimiendo Python ..."
set "T_OK=Python listo."
set "T_ZIP1=Primero descomprime el archivo ZIP:"
set "T_ZIP2=Clic derecho en el ZIP - 'Extraer todo...' - 'Extraer'."
set "T_ZIP3=Luego haz doble clic en 'Me Goos-ta Deutsch - Windows' en la carpeta nueva."
set "T_X86=Este Windows es de 32 bits. Me Goos-ta Deutsch necesita Windows 10 u 11 de 64 bits."
set "T_ORDNER=No se puede crear o escribir esta carpeta:"
set "T_NETZ1=No se pudo descargar Python. Revisa que haya internet."
set "T_NETZ2=Solo el primer inicio necesita internet, luego todo funciona sin internet. Revisa la conexion e inicia otra vez."
set "T_SUMME=El archivo descargado tiene errores. Inicia otra vez."
set "T_ENTPACKEN=No se pudo descomprimir Python. Inicia otra vez."
set "T_PYTHON=Python no arranca. Tal vez un antivirus lo bloquea - mira 'LIES MICH ZUERST'."
set "T_BESETZT=El Python anterior sigue en uso. Cierra todas las ventanas de Me Goos-ta Deutsch e inicia otra vez."
exit /b 0
