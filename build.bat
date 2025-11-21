@echo off
echo Building BlackScreen.exe...
pyinstaller --noconfirm --onefile --windowed --icon "icon.ico" --add-data "icon.ico;." --name "BlackScreen" main.py
echo Build complete! Check the dist folder.
pause
