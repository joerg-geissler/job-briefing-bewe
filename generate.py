"""
Job Briefing BEWE - Static HTML Generator
Liest jobs_dashboard.json und erzeugt eine selbststaendige index.html fuer GitHub Pages.
Taeglich vom Scheduled Task aufgerufen.
"""
import json, os, sys
from datetime import date

DB_PATH  = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
OUT_PATH = r"C:\Users\joerg\job-briefing-public\index.html"
TODAY    = date.today().isoformat()

# Jobs laden
with open(DB_PATH, encoding="utf-8-sig") as f:
    jobs = json.load(f)

jobs_json = json.dumps(jobs, ensure_ascii=False, separators=(",", ":"))
total     = len(jobs)
sources   = len(set(j.get("source","") for j in jobs if j.get("source")))
new_today = sum(1 for j in jobs if j.get("date_added") == TODAY)

# HTML Template
html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Briefing BEWE</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333}}
.header{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);color:white;padding:18px 24px 14px}}
.header h1{{font-size:22px;font-weight:700}}
.header .sub{{font-size:13px;color:#aab;margin-top:4px}}
.controls{{background:white;padding:14px 24px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #e0e4e8;box-shadow:0 2px 4px rgba(0,0,0,.05)}}
.controls label{{font-size:13px;color:#666}}
.controls select{{border:1px solid #ddd;border-radius:6px;padding:6px 10px;font-size:13px;background:#fafafa}}
.controls input[type=range]{{width:120px}}
#scoreVal{{font-weight:700;color:#e63946;min-width:28px}}
.stats{{display:flex;gap:8px;margin-left:auto;align-items:center}}
#dataInfo{{background:#e8f5e9;color:#2e7d32;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600}}
.grid{{padding:16px 24px;display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:14px}}
.card{{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.06);border-left:4px solid #ccc;transition:transform .15s,box-shadow .15s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.12)}}
.card.s95{{border-left-color:#e63946}}.card.s90{{border-left-color:#f4a261}}
.card.s80{{border-left-color:#2a9d8f}}.card.s70{{border-left-color:#4a6cf7}}
.card.s60{{border-left-color:#95a5a6}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}}
.score-badge{{min-width:44px;height:44px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;flex-shrink:0}}
.score-badge.s95{{background:#fde8ea;color:#e63946}}.score-badge.s90{{background:#fef3e8;color:#f4a261}}
.score-badge.s80{{background:#e8f5f3;color:#2a9d8f}}.score-badge.s70{{background:#eef1ff;color:#4a6cf7}}
.score-badge.s60{{background:#f5f6f7;color:#95a5a6}}
.card-title{{font-size:14px;font-weight:700;color:#1a1a2e;line-height:1.4}}
.card-company{{font-size:13px;color:#555;margin-top:3px}}
.card-meta{{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}}
.tag{{font-size:11px;padding:3px 8px;border-radius:20px;font-weight:600}}
.tag-loc{{background:#eef1ff;color:#4a6cf7}}.tag-sal{{background:#e8f5f3;color:#2a9d8f}}
.tag-src{{background:#f5f0ff;color:#7b2d8b}}.tag-new{{background:#fff3cd;color:#a0660a}}
.card-link{{display:inline-block;margin-top:10px;font-size:12px;color:#4a6cf7;text-decoration:none}}
.card-link:hover{{text-decoration:underline}}
#noResults{{text-align:center;padding:60px;color:#999;font-size:15px;grid-column:1/-1}}
.footer{{text-align:center;padding:16px;font-size:11px;color:#bbb;border-top:1px solid #e8e8e8;margin-top:8px}}
</style>
</head>
<body>
<div class="header">
  <h1>Job Briefing BEWE</h1>
  <div class="sub">Taeglich aktualisiert &middot; Zuletzt: {TODAY} &middot; {new_today} neue Stellen heute</div>
</div>
<div class="controls">
  <label>Mindest-Score:</label>
  <input type="range" id="scoreFilter" min="50" max="110" value="60"
    oninput="document.getElementById('scoreVal').textContent=this.value; render()">
  <span id="scoreVal">60</span>
  <label>Quelle:</label>
  <select id="sourceFilter" onchange="render()"><option value="">Alle</option></select>
  <label>Sortierung:</label>
  <select id="sortBy" onchange="render()">
    <option value="score">Score hoch-tief</option>
    <option value="date">Datum neu-alt</option>
    <option value="title">Titel A-Z</option>
  </select>
  <div class="stats"><span id="dataInfo">-</span></div>
</div>
<div class="grid" id="grid"></div>
<div class="footer">Stand {TODAY} &middot; {total} Stellen &middot; {sources} Quellen &middot; automatisch generiert</div>
<script>
const TODAY = '{TODAY}';
const ALL_JOBS = {jobs_json};

function scoreClass(s){{
  if(s>=95)return 's95'; if(s>=90)return 's90';
  if(s>=80)return 's80'; if(s>=70)return 's70'; return 's60';
}}
function esc(s){{
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
function buildSourceFilter(){{
  const sel=document.getElementById('sourceFilter');
  [...new Set(ALL_JOBS.map(j=>j.source).filter(Boolean))].sort().forEach(s=>{{
    const o=document.createElement('option');o.value=s;o.textContent=s;sel.appendChild(o);
  }});
}}
function render(){{
  const min=parseInt(document.getElementById('scoreFilter').value||'60');
  const src=document.getElementById('sourceFilter').value;
  const sort=document.getElementById('sortBy').value;
  let jobs=ALL_JOBS.filter(j=>j.score>=min);
  if(src) jobs=jobs.filter(j=>j.source===src);
  if(sort==='score') jobs.sort((a,b)=>b.score-a.score);
  else if(sort==='date') jobs.sort((a,b)=>(b.date_added||'').localeCompare(a.date_added||''));
  else jobs.sort((a,b)=>(a.title||'').localeCompare(b.title||''));
  document.getElementById('dataInfo').textContent=jobs.length+' Stellen · '+new Set(jobs.map(j=>j.source)).size+' Quellen';
  const grid=document.getElementById('grid');
  if(!jobs.length){{grid.innerHTML='<div id="noResults">Keine Stellen gefunden.</div>';return;}}
  grid.innerHTML=jobs.map(j=>{{
    const sc=scoreClass(j.score);
    const salTag=j.salary_text?'<span class="tag tag-sal">&#128182; '+esc(j.salary_text.replace('pro Jahr','p.a.').replace('pro Monat','p.M.'))+'</span>':'';
    const newTag=j.date_added===TODAY?'<span class="tag tag-new">&#127381; Heute</span>':'';
    const url=j.url||'https://www.google.com/search?q='+encodeURIComponent((j.title||'')+' '+(j.company||''));
    return '<div class="card '+sc+'"><div class="card-top"><div style="flex:1"><div class="card-title">'+esc(j.title||'Unbekannte Stelle')+'</div><div class="card-company">'+esc(j.company||'')+'</div></div><div class="score-badge '+sc+'">'+j.score+'</div></div><div class="card-meta"><span class="tag tag-loc">📍 '+esc(j.location||'-')+'</span>'+salTag+'<span class="tag tag-src">'+esc(j.source||'')+'</span>'+newTag+'</div><a class="card-link" href="'+esc(url)+'" target="_blank">'+(j.url?'Zum Angebot':'Google-Suche')+'</a></div>';
  }}).join('');
}}
buildSourceFilter();
render();
</script>
</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"OK: index.html generiert - {total} Jobs, {new_today} neu heute, Stand {TODAY}")
