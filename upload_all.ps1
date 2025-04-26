Write-Host "=== SUBIENDO PROYECTO COMPLETO A GITHUB ===" -ForegroundColor Green
Write-Host "Limpiando estado del repositorio..." -ForegroundColor Yellow
git reset

# Modificar el .gitignore para incluir todo temporalmente
Write-Host "Guardando .gitignore original..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Copy-Item ".gitignore" ".gitignore.bak" -Force
    # Crear un .gitignore vacío para incluir todos los archivos
    Set-Content ".gitignore" ""
}

# Agregar todos los archivos
Write-Host "Agregando TODOS los archivos al repositorio (incluso los ignorados normalmente)..." -ForegroundColor Yellow
git add --all

# Commit con mensaje descriptivo
Write-Host "Realizando commit con todos los archivos..." -ForegroundColor Yellow
git commit -m "Subida completa del proyecto con TODOS los archivos"

# Push forzado al repositorio
Write-Host "Enviando a GitHub (push forzado)..." -ForegroundColor Yellow
git push -f origin main

# Restaurar el .gitignore original
Write-Host "Restaurando .gitignore original..." -ForegroundColor Yellow
if (Test-Path ".gitignore.bak") {
    Copy-Item ".gitignore.bak" ".gitignore" -Force
    Remove-Item ".gitignore.bak" -Force
}

Write-Host "=== PROCESO COMPLETADO ===" -ForegroundColor Green
Write-Host "Todos los archivos han sido subidos a: https://github.com/aop68/PROYECTO_FINAL_ITLA_GRUPO3.git" -ForegroundColor Cyan
pause 