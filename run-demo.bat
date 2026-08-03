@echo off
rem Zeroclaw Demo Script (Windows batch)
rem Ejecuta Solana Ecosystem Pulse y abre el dashboard automáticamente

cd /d "%USERPROFILE%\Proyectos\solana-ecosystem-pulse"

echo 🚀 Generando reporte de Solana Ecosystem Pulse...
python -m solpulse --output output --timeout 45

echo 📊 Abriendo dashboard en navegador...
start "" "%USERPROFILE%\Proyectos\solana-ecosystem-pulse\output\dashboard.html"

echo ✅ Listo. Dashboard abierto. Grabación sugerida: 1 minuto
echo.
echo ⏱️ Pasos para grabación:
echo 1. Muestra terminal con output del CLI (5s)
echo 2. Muestra dashboard.html con métricas en vivo (30s)
echo 3. Explica: 'No API keys, no firmas, read-only monitor' (15s)
