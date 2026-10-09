@echo off
setlocal
if "%~1"=="" (
  echo Drag the clean unheadered "Final Fantasy III (USA) (Rev 1).sfc" onto this BAT.
  pause
  exit /b 1
)
python "%~dp0build.py" "%~1" --out "%~dp0out"
if errorlevel 1 (
  echo BUILD FAILED
  pause
  exit /b 1
)
python "%~dp0tools\selftest.py" "%~1"
pause
