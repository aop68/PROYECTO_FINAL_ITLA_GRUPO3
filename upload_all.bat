@echo off
echo === SUBIENDO PROYECTO COMPLETO A GITHUB ===
echo Limpiando estado del repositorio...
git reset

echo Guardando .gitignore original...
if exist .gitignore (
    copy .gitignore .gitignore.bak /Y
    echo. > .gitignore
)

echo Agregando TODOS los archivos al repositorio...
git add --all

echo Realizando commit con todos los archivos...
git commit -m "Subida completa del proyecto con TODOS los archivos"

echo Enviando a GitHub (push forzado)...
git push -f origin main

echo Restaurando .gitignore original...
if exist .gitignore.bak (
    copy .gitignore.bak .gitignore /Y
    del .gitignore.bak
)

echo === PROCESO COMPLETADO ===
echo Todos los archivos han sido subidos a: https://github.com/aop68/PROYECTO_FINAL_ITLA_GRUPO3.git
pause 