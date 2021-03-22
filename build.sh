rm -r dist
mkdir dist
sudo chown 1000 dist

sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows "pyinstaller --onefile ResetTracker/resetTracker.py"
sudo chown 1000 dist/resetTracker.exe

pyinstaller --onefile ResetTracker/resetTracker.py