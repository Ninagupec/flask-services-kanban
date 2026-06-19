@echo off
REM setup_mysql.bat - Lance setup_mysql.ps1 (Windows) sans souci de policy PowerShell.
REM Usage : double-clic, ou bien depuis CMD : scripts\setup_mysql.bat
REM Pour un root avec mot de passe :
REM   powershell -ExecutionPolicy Bypass -File "%~dp0setup_mysql.ps1" -MysqlAdminPassword monmdp

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_mysql.ps1" %*
pause
