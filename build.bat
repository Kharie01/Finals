@echo off
pyinstaller --clean --noconsole --onefile --add-data "assets;assets" --distpath "." --name "Fortress Frontline" main.py
echo Build Complete!
pause
