"""
Patch generate.py: Archiv-Feature hinzufügen
(Status-Filter-Leiste + Action-Buttons in Kacheln + localStorage-Persistenz)
"""
import re

PATH = r"C:\Users\joerg\job-briefing-public\generate.py"

with open(PATH, encoding="utf-8") as f:
    src = f.read()

# ─── 1. Grid-Div: Status-Filter-Bar davor einfügen ───────────────────────────
OLD_GRID = '<div class=\\"grid\\" id=\\"grid\\"></div>'
NEW_GRID = (
    '<div class=\\"status-filter\\">\n'
    '  <button class=\\"sf-btn active\\" data-sf=\\"active\\"   onclick=\\"setStatusFilter(\'active\')\\">&#128269; Aktiv <span class=\\"sf-cnt\\" id=\\"cnt-active\\">0</span></button>\n'
    '  <button class=\\"sf-btn\\" data-sf=\\"starred\\"         onclick=\\"setStatusFilter(\'starred\')\\">&#11088; Gemerkt <span class=\\"sf-cnt\\" id=\\"cnt-starred\\">0</span></button>\n'
    '  <button class=\\"sf-btn\\" data-sf=\\"applied\\"         onclick=\\"setStatusFilter(\'applied\')\\">&#10003; Beworben <span class=\\"sf-cnt\\" id=\\"cnt-applied\\">0</span></button>\n'
    '  <button class=\\"sf-btn\\" data-sf=\\"archived\\"        onclick=\\"setStatusFilter(\'archived\')\\">&#128230; Archiv <span class=\\"sf-cnt\\" id=\\"cnt-archived\\">0</span></button>\n'
    '  <button class=\\"sf-btn\\" data-sf=\\"all\\"             onclick=\\"setStatusFilter(\'all\')\\">&#128203; Alle <span class=\\"sf-cnt\\" id=\\"cnt-all\\">0</span></button>\n'
    '</div>\n'
    '<div class=\\"grid\\" id=\\"grid\\"></div>'
)
