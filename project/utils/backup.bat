REM @ECHO OFF
REM runs geostore_backup.py
CALL "C:\simple-inventory\ENV\Scripts\activate.bat"
python backup.py "C:\simple-inventory\project\inventory_0.1.0.sqlite" "C:\simple-inventory\backup"