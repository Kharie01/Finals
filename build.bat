@echo off
pyinstaller --clean --noconsole --onefile --add-data "assets;assets" --distpath "." --icon "assets/images/icon/gameicon.ico" --name "Fortress Frontline" main.py
echo Build Complete!
pause
