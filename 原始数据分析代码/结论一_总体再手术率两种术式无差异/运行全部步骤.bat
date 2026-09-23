@echo off
cd /d %~dp0
for %%s in (step1 step2 step3 step4) do (
    for %%f in (%%s*.py) do python "%%f"
    echo.
)
pause
