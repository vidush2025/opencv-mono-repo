@echo off
setlocal

cd /d "%~dp0\midi"

if not exist out mkdir out

dir /s /b src\*.java > sources.txt
javac -cp "lib\*" -d out @sources.txt
if errorlevel 1 (
  echo Java compile failed.
  del sources.txt >nul 2>nul
  exit /b 1
)
del sources.txt >nul 2>nul

echo Starting Java MIDI receiver...
java -cp "out;lib\*" main.Main %*

endlocal