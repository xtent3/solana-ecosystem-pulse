# 🎬 GUIÓN DETALLADO — VIDEO ZEROCLAW (5 MINUTOS)

## 📋 Información del video

| Campo | Valor |
|---|---|
| **Duración objetivo** | 4:30 - 5:00 minutos |
| **Formato** | 1080p o 4K |
| **Plataforma** | YouTube (no listado) + link en submission |
| **Idioma** | Inglés (Zeroclaw es bounty internacional) |
| **Tono** | Técnico pero accesible, no acelerado |

---

## 🎬 ESCENA POR ESCENA

### **ESCENA 1: INTRO (0:00 - 0:30)**

**Visual:**
- Pantalla negra con logo Solana Pulse apareciendo fade-in
- Texto overlay: "Solana Ecosystem Pulse — Built for Zeroclaw Bounty"

**Audio/Voz:**
> "This is Solana Ecosystem Pulse — a dependency-free, auditable network monitor built for the Zeroclaw bounty. One command, real network data, zero secrets."

**Notas técnicas:**
- Usar el favicon SVG o logo del proyecto
- Música de fondo suave (opcional, volumen bajo)

---

### **ESCENA 2: EL PROBLEMA (0:30 - 1:00)**

**Visual:**
- Split screen: 
  - Izquierda: Otros dashboards de Solana (con advertencia "Requires API key")
  - Derecha: Tu terminal con `python -m solpulse` ejecutándose limpio

**Audio/Voz:**
> "Most Solana dashboards require API keys, sign transactions, or depend on heavy frameworks. This one doesn't. It's 100% read-only, zero dependencies, and works with just Python's standard library."

**Notas técnicas:**
- Capturar pantalla de solana.com o explorer.solana.com con disclaimers
- Mostrar tu terminal con el comando ejecutándose
- Highlight el texto "no API keys" en pantalla

---

### **ESCENA 3: DEMO EN VIVO (1:00 - 2:30)**

**Visual:**
- Pantalla completa del navegador mostrando `https://xtent3.github.io/solana-ecosystem-pulse`
- Navegar por el dashboard:
  - Hover en cards
  - Click en toggle theme (dark/light)
  - Zoom en gráficos SVG
  - Mostrar source health

**Audio/Voz:**
> "Here's the live dashboard. Real TPS from mainnet, validator health, DeFi TVL from DeFiLlama, DEX volume. Everything is timestamped and auditable. The theme toggle persists your preference. And it prints clean PDF reports for record-keeping."

**Notas técnicas:**
- Grabar en screen recording (OBS, Windows Xbox Game Bar, o ShareX)
- Mostrar:
  - TPS actual (ej: 4,090)
  - Validators: 692 activos
  - DeFi TVL: $4.75B
  - Click en theme toggle
  - Press Ctrl+P para mostrar print preview limpio

---

### **ESCENA 4: CÓDIGO AUDITABLE (2:30 - 3:30)**

**Visual:**
- VS Code (o tu editor) mostrando:
  - `solpulse/cli.py` (corto, limpio)
  - `solpulse/_premium.py` (líneas clave)
  - `tests/test_cli.py`
  - Terminal con `python -m pytest tests/ -v` (todos pasando)

**Audio/Voz:**
> "Every line is auditable. Pure Python, no external packages. The collector fetches from public RPC and CoinGecko, the renderer generates four formats from one snapshot, and 18 tests cover error handling, HTML escaping, and cross-format consistency."

**Notas técnicas:**
- Mostrar que `requirements.txt` no existe o está vacío
- Highlight: `zero dependencies`
- Mostrar suite de tests corriendo (18 passed)
- Mostrar `SECURITY-AUDIT.md` brevemente

---

### **ESCENA 5: REPRODUCIBILIDAD (3:30 - 4:15)**

**Visual:**
- Terminal mostrando:
```bash
git clone https://github.com/xtent3/solana-ecosystem-pulse.git
cd solana-ecosystem-pulse
python -m solpulse --output output
ls output/
```
- Mostrar que se generan los 4 archivos idénticos

**Audio/Voz:**
> "Anyone can verify this. Clone, run, get the same four artifacts. The GitHub Actions workflow refreshes the demo every six hours automatically. No setup, no config, no secrets."

**Notas técnicas:**
- Ejecutar en limpio (usa VM o nueva terminal)
- Mostrar `snapshot.json` con esquema real
- Highlight: `atomically replaced` en el código

---

### **ESCENA 6: CONCLUSIÓN + CTA (4:15 - 5:00)**

**Visual:**
- Volver al dashboard en pantalla completa
- Texto overlay grande:
  - "No API keys"
  - "18/18 tests"
  - "Zero dependencies"
  - "Fully auditable"
- Final con link al repo

**Audio/Voz:**
> "Solana Ecosystem Pulse. No API keys, no signatures, no bloat. Just real network data, rendered beautifully, and fully auditable. Check the repo — the code speaks for itself. Built for the Zeroclaw bounty."

**Notas técnicas:**
- Terminación limpia (logo + repo URL)
- Mostrar QR code al repo (opcional)
- Texto: "Link in description"

---

## 🎬 CHECKLIST DE GRABACIÓN

### Software necesario
- [ ] OBS Studio (gratis) o ShareX
- [ ] Audacity (para grabar voz aparte si es necesario)
- [ ] Editor de video: DaVinci Resolve, CapCut, o Shotcut (todos gratis)

### Setup técnico
- [ ] Resolución: 1920x1080 mínimo
- [ ] Frame rate: 30fps (60 si tu PC lo aguanta)
- [ ] Audio: micrófono limpio (usa micrófono del celular si es necesario)
- [ ] Pantalla limpia (sin notificaciones, sin otros apps abriendo)

### Pasos de grabación
1. [ ] Grabar cada escena por separado (más fácil editar)
2. [ ] Grabar voz por escena (no necesitas hacer todo en una toma)
3. [ ] Screenshot de cada escena clave para thumbnail
4. [ ] Montar en editor de video
5. [ ] Agregar texto overlay (subtítulos opcionales pero recomendados)
6. [ ] Música de fondo suave (opcional, volumen -20dB)
7. [ ] Exportar como MP4 (H.264, 1080p)

### Thumbnail para YouTube
- [ ] 1280x720 píxeles
- [ ] Logo Solana Pulse grande
- [ ] Texto: "ZERO API KEYS | 18/18 TESTS | ZERO DEPENDENCIES"
- [ ] Fondo oscuro con acento verde (#14F195)

---

## 📝 NOTAS FINALES

- **Si te tiembla la voz**: usa ElevenLabs (gratis hasta 10K caracteres) para generar voz, luego sincroniza
- **Si no tienes experiencia editando**: usa CapCut con templates pre-hechos
- **Si te tardas más de 5 minutos**: mejor corta el código — enfócate en el demo en vivo que es lo más impresionante

---

**Ready?** Cuando lo tengas grabado, súbelo a YouTube (no listado), copia el link, y pégalo en el submission de Zeroclaw.

**Zeroclaw submission link:** Revisar en `ZEROCRAWL-SUBMISSION-GUIDE.md`
