
#!/usr/bin/env python
"""Premium dashboard assets - embedded SVG logos (no external dependencies)."""

SOLANA_LOGO = """<svg viewBox="0 0 397 319" xmlns="http://www.w3.org/2000/svg">
  <g fill="none" fill-rule="evenodd">
    <path fill="#14F195" d="M198.5 319c0-3.7-3-6.7-6.7-6.7h-25.3c-3.7 0-6.7 3-6.7 6.7v26.7c0 3.7 3 6.7 6.7 6.7h25.3c3.7 0 6.7-3 6.7-6.7v-26.7z"/>
    <path fill="#14F195" d="M132.8 253.3c-3.7 0-6.7-3-6.7-6.7V166c0-3.7 3-6.7 6.7-6.7h123.3c3.7 0 6.7 3 6.7 6.7v86.6c0 3.7-3 6.7-6.7 6.7h-123.3z"/>
    <path fill="#14F195" d="M66.2 199.3c-3.7 0-6.7-3-6.7-6.7V72.7c0-3.7 3-6.7 6.7-6.7h259.3c3.7 0 6.7 3 6.7 6.7v119.9c0 3.7-3 6.7-6.7 6.7H66.2z"/>
    <path fill="#9945FF" d="M198.5 206c-3.7 0-6.7-3-6.7-6.7V72.7c0-3.7 3-6.7 6.7-6.7h123.3c3.7 0 6.7 3 6.7 6.7v126.6c0 3.7-3 6.7-6.7 6.7H198.5z"/>
    <path fill="#9945FF" d="M198.5 139.3c-3.7 0-6.7-3-6.7-6.7V16.7c0-3.7 3-6.7 6.7-6.7h123.3c3.7 0 6.7 3 6.7 6.7v119.9c0 3.7-3 6.7-6.7 6.7H198.5z"/>
    <path fill="#9945FF" d="M198.5 72.7c-3.7 0-6.7-3-6.7-6.7V0c0-3.7 3-6.7 6.7-6.7h123.3c3.7 0 6.7 3 6.7 6.7v66c0 3.7-3 6.7-6.7 6.7H198.5z"/>
  </g>
</svg>"""
SOLANA_LOGO_ALT = """<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="solanaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#14F195;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#9945FF;stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="90" fill="url(#solanaGradient)"/>
  <text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" fill="white" font-family="Arial" font-size="140" font-weight="bold" style="paint-order: stroke; stroke: white; stroke-width: 8;">S</text>
</svg>"""
SOLANA_TEXT_LOGO = """<svg viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg">
  <text x="0" y="60" font-family="Inter, -apple-system, BlinkMacSystemFont, sans-serif" font-size="48" font-weight="700" fill="#14F195">Solana</text>
  <text x="140" y="60" font-family="Inter, -apple-system, BlinkMacSystemFont, sans-serif" font-size="48" font-weight="300" fill="#9945FF">Ecosystem</text>
  <text x="0" y="85" font-family="Inter, -apple-system, BlinkMacSystemFont, sans-serif" font-size="14" fill="#9aa6c1" letter-spacing="2">PULSE</text>
</svg>"""

DATA_LOGOS = {
    "coingecko": """<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
      <text x="0" y="40" font-family="Inter" font-size="32" font-weight="600" fill="#F7931A">CoinGecko</text>
    </svg>""",
    "defillama": """<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
      <text x="0" y="40" font-family="Inter" font-size="32" font-weight="600" fill="#00A8FF">DeFiLlama</text>
    </svg>""",
    "rpc": """<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
      <text x="0" y="40" font-family="Inter" font-size="32" font-weight="600" fill="#14F195">Solana RPC</text>
    </svg>""",
}

# Color palette
COLORS = {
    "primary": "#14F195",   # Solana Green
    "secondary": "#9945FF", # Solana Violet
    "accent": "#F4F4F4",    # Solana White
    "dark_bg": "#0A0A0A",
    "card_bg": "#141414",
    "panel_bg": "#0B1220",
    "text_primary": "#eef2ff",
    "text_secondary": "#9aa6c1",
    "cyan": "#48d9d0",
    "violet": "#8b7cff",
    "warn": "#ffbd69",
    "critical": "#ff6685",
    "line": "#26324b",
}
