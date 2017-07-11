@ECHO OFF
CALL ENV\Scripts\activate
START /B "" python run.py && START /WAIT "" http://localhost:8700/admin