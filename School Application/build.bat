@echo off
echo Building School Application...

REM Clean up previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Create the executable
pyinstaller ^
    --name="SchoolApp" ^
    --windowed ^
    --icon=icon.ico ^
    --clean ^
    --add-data "utils.py;." ^
    --add-data "timer_module.py;." ^
    --add-data "name_picker_module.py;." ^
    --add-data "tournament_module.py;." ^
    --add-data "tournament_display.py;." ^
    --add-data "timer_tick.wav;." ^
    --add-data "timer_end.wav;." ^
    --hidden-import pandas ^
    --hidden-import pygame ^
    main.py

echo.
echo Build completed! The executable can be found in the 'dist' folder.
pause 