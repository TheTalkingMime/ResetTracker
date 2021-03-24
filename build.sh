rm -r dist
mkdir dist
sudo chown 1000 dist

sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows "pyinstaller --onefile src/main.py"
sudo chown 1000 dist/main.exe

pyinstaller --onefile src/main.py