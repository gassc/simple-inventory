@ECHO OFF
CALL ENV\Scripts\activate
start python run.py && start /B /WAIT "" http://flynn-chiropractic:8700/admin