
@setlocal
@set PYTHON_BASE=%~d0\local\Python37
@set PATH=%PYTHON_BASE%;%PYTHON_BASE%\Scripts;%PYTHON_BASE%\Lib;%PYTHON_BASE%\Lib\site-packages\pywin32_system32;%PATH%
@set PYTHONPATH=%PYTHON_BASE%\Lib\site-packages;%PYTHON_BASE%\Lib\site-packages\rtctree\rtmidl\;%~dp0..


@set MODULE=%1 
%PYTHON_BASE%\python -m zipapp %MODULE% -m "%MODULE: =%:main"

@set EXEC_FILE=%MODULE: =%.exe

@if not exist %EXEC_FILE% @(
    copy cli64.exe  %EXEC_FILE%
)

@endlocal
