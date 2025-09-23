@echo off
echo Starting Robot Bridge Server (Python 2)...
echo.
echo Make sure you have Python 2 installed and libpyauboi5 available
echo.
echo Robot IP: 192.168.23.129 (change this in robot_bridge_server.py if needed)
echo Bridge Port: 5000
echo.
echo Press Ctrl+C to stop the server
echo.

python2 robot_bridge_server.py

pause
