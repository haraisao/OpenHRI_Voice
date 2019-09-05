@setlocal
@set OpenHRI_ROOT=%~dp0\bin
@call %~d0\local\OpenRTM-aist\setup.bat
bin\%~n0.exe %*

@endlocal