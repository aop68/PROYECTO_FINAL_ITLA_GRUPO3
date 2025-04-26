Write-Host "Limpiando estado del git..." -ForegroundColor Green
git reset | Out-File -FilePath "git_output.log" -Append
Write-Host "Añadiendo todos los archivos..." -ForegroundColor Green
git add . | Out-File -FilePath "git_output.log" -Append
Write-Host "Realizando commit..." -ForegroundColor Green
git commit -m "Carga completa del proyecto FINAL ITLA GRUPO3" | Out-File -FilePath "git_output.log" -Append
Write-Host "Enviando a GitHub..." -ForegroundColor Green
git push -f origin main | Out-File -FilePath "git_output.log" -Append
Write-Host "Proceso completado." -ForegroundColor Green
Write-Host "Consulta git_output.log para ver los detalles" -ForegroundColor Yellow
pause 