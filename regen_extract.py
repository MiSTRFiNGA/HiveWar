"""Re-extract the inline game script from index.html for headless testing."""
import re
html = open('index.html', encoding='utf-8').read()
scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
open('_game_extract.js', 'w', encoding='utf-8').write(max(scripts, key=len))
print("extracted", len(max(scripts, key=len)), "chars -> _game_extract.js")
