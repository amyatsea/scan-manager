set PYTHON_ROOT="d:\python27"
cd resources
%PYTHON_ROOT%\lib\site-packages\PySide\pyside-rcc.exe -o ..\resources.py scanmanager.qrc
pause
cd ..
%PYTHON_ROOT%\python setup.py py2exe
pause
cd dist
"D:\Program Files (x86)\NSIS\makensis.exe" /NOCD ..\scanmanager.nsi
cd ..
pause