@echo off
echo Limpiando estado del git...
git reset
echo Añadiendo todos los archivos...
git add .
echo Realizando commit...
git commit -m "Carga completa del proyecto"
echo Enviando a GitHub...
git push -f origin main
echo Proceso completado.
pause 