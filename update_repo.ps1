Write-Host "Copiando archivos importantes de env al directorio principal..." -ForegroundColor Green

# Crear directorios si no existen
New-Item -ItemType Directory -Force -Path "./templates" | Out-Null
New-Item -ItemType Directory -Force -Path "./static" | Out-Null
New-Item -ItemType Directory -Force -Path "./utils" | Out-Null
New-Item -ItemType Directory -Force -Path "./models" | Out-Null

# Copiar archivos principales
Copy-Item -Path "./env/app.py" -Destination "./" -Force
Copy-Item -Path "./env/dash_app.py" -Destination "./" -Force
Copy-Item -Path "./env/wsgi.py" -Destination "./" -Force
Copy-Item -Path "./env/init_dashboard_db.py" -Destination "./" -Force
Copy-Item -Path "./env/cargar_datos_simple.py" -Destination "./" -Force
Copy-Item -Path "./env/importar_datos_csv.py" -Destination "./" -Force
Copy-Item -Path "./env/generate_qr.py" -Destination "./" -Force
Copy-Item -Path "./env/CONFIGURACION_LMSTUDIO.md" -Destination "./" -Force
Copy-Item -Path "./env/requirements.txt" -Destination "./" -Force

# Copiar directorios
Copy-Item -Path "./env/templates/*" -Destination "./templates/" -Recurse -Force
Copy-Item -Path "./env/static/*" -Destination "./static/" -Recurse -Force
Copy-Item -Path "./env/utils/*" -Destination "./utils/" -Recurse -Force
Copy-Item -Path "./env/models/*" -Destination "./models/" -Recurse -Force

Write-Host "Añadiendo archivos al repositorio..." -ForegroundColor Green
git add .

Write-Host "Realizando commit..." -ForegroundColor Green
git commit -m "Subida completa del proyecto con todos los archivos importantes"

Write-Host "Enviando a GitHub..." -ForegroundColor Green
git push -f origin main

Write-Host "Proceso completado." -ForegroundColor Green
Write-Host "Revisa el repositorio en https://github.com/aop68/PROYECTO_FINAL_ITLA_GRUPO3.git" -ForegroundColor Yellow 