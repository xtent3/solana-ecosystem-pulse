#!/usr/bin/env python
"""
Zeroclaw Demo Script
Ejecuta Solana Ecosystem Pulse y abre el dashboard automáticamente.
Para usar: python run_demo.py
"""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def main():
    # Configura rutas
    project_dir = Path.home() / "Proyectos" / "solana-ecosystem-pulse"
    output_dir = project_dir / "output"
    dashboard_html = output_dir / "dashboard.html"

    # Verifica que el proyecto existe
    if not project_dir.exists():
        print(f"❌ Error: No se encontró el proyecto en {project_dir}")
        sys.exit(1)

    # Cambia al directorio del proyecto
    os.chdir(project_dir)

    print("🚀 Generando reporte de Solana Ecosystem Pulse...")
    print("=" * 60)

    # Ejecuta el CLI
    result = subprocess.run(
        [sys.executable, "-m", "solpulse", "--output", "output", "--timeout", "45"],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"❌ Error al generar el reporte (exit code: {result.returncode})")
        sys.exit(1)

    print("=" * 60)
    print("📊 Abriendo dashboard en navegador...")

    # Abre el dashboard en el navegador predeterminado
    if dashboard_html.exists():
        webbrowser.open(f"file://{dashboard_html.resolve()}")
        print("✅ Listo. Dashboard abierto.")
        print()
        print("⏱️ Pasos para grabación (1 minuto total):")
        print("  1. Muestra terminal con output del CLI (5s)")
        print("  2. Muestra dashboard.html con métricas en vivo (30s)")
        print("  3. Explica: 'No API keys, no firmas, read-only monitor' (15s)")
        print()
        print("📺 Sube el video a YouTube/Vimeo y pega el enlace en el post de Discord.")
    else:
        print(f"❌ Error: No se encontró {dashboard_html}")


if __name__ == "__main__":
    main()
