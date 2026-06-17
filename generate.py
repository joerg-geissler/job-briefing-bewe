"""
Job Briefing BEWE - Static HTML Generator
Liest jobs_dashboard.json und erzeugt eine selbststaendige index.html fuer GitHub Pages.
Taeglich vom Scheduled Task aufgerufen.
"""
import json, os, re, sys
from datetime import datetime

_LOCAL_DB      = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\jobs_dashboard.json"
_LOCAL_STATUS  = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Artifacts\job-briefing-bewe\job_status.json"
_LOCAL_PROFILE = r"C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe\profile.json"
_LOCAL_OUT     = r"C:\Users\joerg\job-briefing-public\index.html"

DB_PATH      = os.environ.get("DB_PATH",      "jobs_dashboard.json" if os.path.exists("jobs_dashboard.json") else _LOCAL_DB)
STATUS_PATH  = os.environ.get("STATUS_PATH",  "job_status.json"     if os.path.exists("job_status.json")     else _LOCAL_STATUS)
PROFILE_PATH = os.environ.get("PROFILE_PATH", "profile.json"        if os.path.exists("profile.json")        else _LOCAL_PROFILE)
OUT_PATH     = os.environ.get("OUT_PATH",     "index.html")
TODAY        = datetime.now().strftime('%Y-%m-%d')
NOW          = datetime.now().strftime('%Y-%m-%d %H:%M')

# Jobs laden
with open(DB_PATH, encoding="utf-8-sig") as f:
    jobs = json.load(f)

# Status laden (aus job_status.json, falls vorhanden)
if os.path.exists(STATUS_PATH):
    with open(STATUS_PATH, encoding="utf-8") as f:
        job_status_data = json.load(f)
else:
    job_status_data = {}
status_json = json.dumps(job_status_data, ensure_ascii=False, separators=(",", ":"))

# Profil laden
if os.path.exists(PROFILE_PATH):
    with open(PROFILE_PATH, encoding="utf-8") as f:
        profile_data = json.load(f)
else:
    profile_data = {"base": 50, "hard_exclude": {"score": 5, "terms": []}, "tech_exclude": {"score": 10, "terms": []}, "criteria": []}
profile_json = json.dumps(profile_data, ensure_ascii=False, separators=(",", ":"))

jobs_json = json.dumps(jobs, ensure_ascii=False, separators=(",", ":"))
total     = len(jobs)
sources   = len(set(j.get("source","") for j in jobs if j.get("source")))
new_today = sum(1 for j in jobs if j.get("date_added") == TODAY)

# CSS (kein f-string noetig, keine Python-Variablen)
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333}
.header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);color:white;padding:18px 24px 0}
.header h1{font-size:22px;font-weight:700}
.header .sub{font-size:13px;color:#aab;margin-top:4px;padding-bottom:10px}
.tab-nav{display:flex;gap:2px;padding-top:4px}
.tab-btn{padding:10px 20px;font-size:13px;font-weight:600;border:none;border-radius:8px 8px 0 0;cursor:pointer;background:rgba(255,255,255,.1);color:rgba(255,255,255,.65);transition:background .15s,color .15s}
.tab-btn:hover{background:rgba(255,255,255,.2);color:white}
.tab-btn.active{background:#f0f2f5;color:#1a1a2e}
.page{display:none}.page.active{display:block}
.controls{background:white;padding:14px 24px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #e0e4e8;box-shadow:0 2px 4px rgba(0,0,0,.05)}
.controls label{font-size:13px;color:#666}
.controls select{border:1px solid #ddd;border-radius:6px;padding:6px 10px;font-size:13px;background:#fafafa}
.controls input[type=range]{width:120px}
#scoreVal{font-weight:700;color:#e63946;min-width:28px}
.stats{display:flex;gap:8px;margin-left:auto;align-items:center}
#dataInfo{background:#e8f5e9;color:#2e7d32;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600}
.grid{padding:16px 24px;display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:14px}
.card{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.06);border-left:4px solid #ccc;transition:transform .15s,box-shadow .15s}
.card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.12)}
.card.s95{border-left-color:#e63946}.card.s90{border-left-color:#f4a261}
.card.s80{border-left-color:#2a9d8f}.card.s70{border-left-color:#4a6cf7}
.card.s60{border-left-color:#95a5a6}
.card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.score-badge{min-width:44px;height:44px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;flex-shrink:0}
.score-badge.s95{background:#fde8ea;color:#e63946}.score-badge.s90{background:#fef3e8;color:#f4a261}
.score-badge.s80{background:#e8f5f3;color:#2a9d8f}.score-badge.s70{background:#eef1ff;color:#4a6cf7}
.score-badge.s60{background:#f5f6f7;color:#95a5a6}
.card-title{font-size:14px;font-weight:700;color:#1a1a2e;line-height:1.4}
.card-company{font-size:13px;color:#555;margin-top:3px}
.card-meta{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.tag{font-size:11px;padding:3px 8px;border-radius:20px;font-weight:600}
.tag-loc{background:#eef1ff;color:#4a6cf7}.tag-sal{background:#e8f5f3;color:#2a9d8f}
.tag-src{background:#f5f0ff;color:#7b2d8b}.tag-new{background:#fff3cd;color:#a0660a}.tag-pubdate{background:#fef3e2;color:#c25a00}.tag-maildate{background:#e8f0ff;color:#3b5bdb}
.card-link{display:inline-block;margin-top:10px;font-size:12px;color:#4a6cf7;text-decoration:none}
.card-link:hover{text-decoration:underline}
#noResults{text-align:center;padding:60px;color:#999;font-size:15px;grid-column:1/-1}
.footer{text-align:center;padding:16px;font-size:11px;color:#bbb;border-top:1px solid #e8e8e8;margin-top:8px}
.status-filter{display:flex;gap:6px;padding:10px 24px;background:white;border-bottom:1px solid #e8eaf0;flex-wrap:wrap}
.sf-btn{padding:6px 14px;font-size:12px;font-weight:600;border:1px solid #dde;border-radius:20px;cursor:pointer;background:white;color:#555;transition:all .15s}
.sf-btn:hover{background:#f0f2ff;border-color:#4a6cf7;color:#4a6cf7}
.sf-btn.active{background:#4a6cf7;color:white;border-color:#4a6cf7}
.sf-cnt{display:inline-block;margin-left:4px;border-radius:10px;padding:0 6px;font-size:11px;background:rgba(255,255,255,.3)}
.sf-btn:not(.active) .sf-cnt{background:#eef0f8;color:#666}
.card-actions{display:flex;gap:5px;margin-top:10px;padding-top:10px;border-top:1px solid #f0f0f0}
.act-btn{flex:1;padding:5px 4px;border:1px solid #e8e8e8;border-radius:7px;font-size:11px;font-weight:600;cursor:pointer;background:white;color:#666;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:3px}
.act-btn:hover{background:#f5f5ff;border-color:#c0c4ff}
.act-btn.st-starred{background:#fffbe6;border-color:#f5c518;color:#a0660a}
.act-btn.st-applied{background:#e8f5e9;border-color:#66bb6a;color:#2e7d32}
.act-btn.st-archived{background:#fce8e8;border-color:#ef9a9a;color:#c62828}
.card.job-starred{border-left-color:#f5c518!important}
.card.job-applied{border-left-color:#66bb6a!important}
.card.job-archived{opacity:.4}
.card.job-archived .card-title{text-decoration:line-through}
.neu-info{padding:14px 24px 4px;font-size:14px;font-weight:600;color:#1a1a2e}
.scores-page{padding:20px 24px;max-width:860px}
.crit-card{background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:14px;overflow:hidden}
.crit-card.exclude-card{border-left:4px solid #e63946}
.crit-header{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid #f0f0f0;flex-wrap:wrap}
.crit-name{flex:1;font-size:13px;font-weight:700;color:#1a1a2e}
.crit-name input{border:1px solid #e0e0e0;border-radius:6px;padding:4px 8px;font-size:13px;font-weight:700;width:140px}
.crit-pts{display:flex;align-items:center;gap:6px;font-size:12px;color:#666}
.crit-pts input{width:64px;border:1px solid #ddd;border-radius:6px;padding:4px 8px;font-size:13px;text-align:right}
.crit-del{border:none;background:none;cursor:pointer;color:#ccc;font-size:16px;padding:2px 6px;border-radius:5px}
.crit-del:hover{background:#fde8ea;color:#e63946}
.terms-area{display:flex;flex-wrap:wrap;gap:6px;padding:12px 16px;align-items:center}
.term-pill{display:inline-flex;align-items:center;gap:4px;background:#eef1ff;color:#4a6cf7;border-radius:20px;padding:3px 10px;font-size:12px;font-weight:600}
.term-pill.exclude-pill{background:#fde8ea;color:#e63946}
.term-pill button{border:none;background:none;cursor:pointer;color:inherit;font-size:13px;line-height:1;padding:0;opacity:.6}
.term-pill button:hover{opacity:1}
.term-add{display:flex;gap:5px;align-items:center}
.term-add input{border:1px solid #ddd;border-radius:20px;padding:3px 10px;font-size:12px;width:130px;outline:none}
.term-add input:focus{border-color:#4a6cf7}
.term-add button{border:1px solid #4a6cf7;background:#4a6cf7;color:white;border-radius:20px;padding:3px 10px;font-size:12px;cursor:pointer}
.scores-toolbar{display:flex;gap:10px;margin-top:6px;flex-wrap:wrap}
.btn-primary{background:#4a6cf7;color:white;border:none;border-radius:8px;padding:9px 18px;font-size:13px;font-weight:600;cursor:pointer}
.btn-primary:hover{background:#3a5ce7}
.btn-ghost{background:white;color:#555;border:1px solid #ddd;border-radius:8px;padding:9px 18px;font-size:13px;font-weight:600;cursor:pointer}
.btn-ghost:hover{background:#f5f5ff;border-color:#4a6cf7;color:#4a6cf7}
.scores-status{font-size:12px;color:#2e7d32;align-self:center}
.base-row{display:flex;align-items:center;gap:10px;padding:12px 16px}
.base-row label{font-size:13px;color:#555;flex:1}
"""

# JavaScript (kein f-string, nur jobs_json und TODAY werden spaeter eingefuegt)
JS = r"""
const STATUS_KEY = 'bewe_status_v1';
let jobStatus = {};
let activeStatusFilter = 'active';

function scoreClass(s){
  if(s>=95)return 's95'; if(s>=90)return 's90';
  if(s>=80)return 's80'; if(s>=70)return 's70'; return 's60';
}
function fmtDate(s){
  if(!s||s.length<10) return s||'';
  var p=s.split('-'); return p[2]+'.'+p[1]+'.'+p[0];
}
function esc(s){
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function getJobKey(j){ return ((j.title||'')+'|'+(j.company||'')).toLowerCase(); }
function loadStatus(){
  try{
    const ls=JSON.parse(localStorage.getItem(STATUS_KEY)||'{}');
    return Object.keys(ls).length ? ls : Object.assign({},INITIAL_STATUS);
  }
  catch(e){ return Object.assign({},INITIAL_STATUS); }
}
function saveStatus(){ localStorage.setItem(STATUS_KEY,JSON.stringify(jobStatus)); }

function showTab(name){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
  if(name==='neu')    renderNeu();
  if(name==='scores') renderScoresEditor();
}

function renderCard(j){
  const sc=scoreClass(j.score);
  const jk=getJobKey(j);
  const jst=jobStatus[jk]||'';
  const jkH=esc(jk);
  const salTag=j.salary_text?'<span class="tag tag-sal">&#128182; '+esc(j.salary_text.replace('pro Jahr','p.a.').replace('pro Monat','p.M.'))+'</span>':'';
  const newTag=j.date_added===TODAY?'<span class="tag tag-new">&#127381; Heute</span>':'';
  const applyDate=jst==='applied'&&jobStatus[jk+'_date']?'<span class="tag" style="background:#e8f5e9;color:#2e7d32">&#10003; '+jobStatus[jk+'_date']+'</span>':'';
  const pubDateTag=j.pub_date?'<span class="tag tag-pubdate" title="Veroeffentlichungsdatum">&#128197; '+fmtDate(j.pub_date)+'</span>':'';
  const mailDateTag=j.date_added?'<span class="tag tag-maildate" title="Systemerfassung">&#128269; '+fmtDate(j.date_added)+'</span>':'';
  const url=j.url||'https://www.google.com/search?q='+encodeURIComponent((j.title||'')+' '+(j.company||''));
  const xtra=jst==='archived'?' job-archived':jst==='starred'?' job-starred':jst==='applied'?' job-applied':'';
  return '<div class="card '+sc+xtra+'">'
    +'<div class="card-top"><div style="flex:1"><div class="card-title">'+esc(j.title||'Unbekannte Stelle')+'</div>'
    +'<div class="card-company">'+esc(j.company||'')+'</div></div>'
    +'<div class="score-badge '+sc+'">'+j.score+'</div></div>'
    +'<div class="card-meta"><span class="tag tag-loc">&#128205; '+esc(j.location||'-')+'</span>'
    +salTag+'<span class="tag tag-src">'+esc(j.source||'')+'</span>'+newTag+applyDate+'</div>'
    +'<div class="card-meta" style="margin-top:4px">'+pubDateTag+mailDateTag+'</div>'
    +'<a class="card-link" href="'+esc(url)+'" target="_blank">'+(j.url?'&#10132; Zum Angebot':'&#10132; Google-Suche')+'</a>'
    +'<div class="card-actions">'
    +'<button class="act-btn'+(jst==='starred'?' st-starred':'')+'" data-jk="'+jkH+'" data-st="starred"  onclick="toggleStatus(this.dataset.jk,this.dataset.st)">&#11088; Merken</button>'
    +'<button class="act-btn'+(jst==='applied'?' st-applied':'')+'" data-jk="'+jkH+'" data-st="applied"  onclick="toggleStatus(this.dataset.jk,this.dataset.st)">&#10003; Beworben</button>'
    +'<button class="act-btn'+(jst==='archived'?' st-archived':'')+'" data-jk="'+jkH+'" data-st="archived" onclick="toggleStatus(this.dataset.jk,this.dataset.st)">&#128230; Archiv</button>'
    +'</div></div>';
}

function renderNeu(){
  const maxDate=ALL_JOBS.reduce((m,j)=>j.date_added>m?j.date_added:m,'');
  const jobs=ALL_JOBS.filter(j=>j.date_added===maxDate).sort((a,b)=>b.score-a.score);
  document.getElementById('neu-info').textContent=jobs.length+' Stellen · letzte Abfrage: '+fmtDate(maxDate);
  const grid=document.getElementById('grid-neu');
  grid.innerHTML=jobs.length?jobs.map(j=>renderCard(j)).join(''):'<div style="padding:24px;color:#888">Keine Jobs.</div>';
}

function toggleStatus(jk,newSt){
  const cur=jobStatus[jk]||'';
  if(cur===newSt){ delete jobStatus[jk]; delete jobStatus[jk+'_date']; }
  else{ jobStatus[jk]=newSt; if(newSt==='applied') jobStatus[jk+'_date']=TODAY; else delete jobStatus[jk+'_date']; }
  saveStatus(); render();
  if(document.getElementById('page-neu').classList.contains('active')) renderNeu();
}
function setStatusFilter(sf){
  activeStatusFilter=sf;
  document.querySelectorAll('.sf-btn').forEach(b=>b.classList.toggle('active',b.dataset.sf===sf));
  render();
}
function updateStatusCounts(){
  const c={active:0,starred:0,applied:0,archived:0,all:0};
  ALL_JOBS.forEach(j=>{
    const st=jobStatus[getJobKey(j)]||'';
    c.all++;
    if(st==='starred'){c.starred++;c.active++;}
    else if(st==='applied') c.applied++;
    else if(st==='archived') c.archived++;
    else c.active++;
  });
  Object.entries(c).forEach(([k,v])=>{ const el=document.getElementById('cnt-'+k); if(el) el.textContent=v; });
}
function buildSourceFilter(){
  const sel=document.getElementById('sourceFilter');
  [...new Set(ALL_JOBS.map(j=>j.source).filter(Boolean))].sort().forEach(s=>{
    const o=document.createElement('option');o.value=s;o.textContent=s;sel.appendChild(o);
  });
}
function render(){
  updateStatusCounts();
  const min=parseInt(document.getElementById('scoreFilter').value||'60');
  const src=document.getElementById('sourceFilter').value;
  const sort=document.getElementById('sortBy').value;
  let jobs=ALL_JOBS.filter(j=>j.score>=min);
  if(src) jobs=jobs.filter(j=>j.source===src);
  if(activeStatusFilter==='active')    jobs=jobs.filter(j=>{ const s=jobStatus[getJobKey(j)]; return !s||s==='starred'; });
  else if(activeStatusFilter==='starred')  jobs=jobs.filter(j=>jobStatus[getJobKey(j)]==='starred');
  else if(activeStatusFilter==='applied')  jobs=jobs.filter(j=>jobStatus[getJobKey(j)]==='applied');
  else if(activeStatusFilter==='archived') jobs=jobs.filter(j=>jobStatus[getJobKey(j)]==='archived');
  if(sort==='score') jobs.sort((a,b)=>b.score-a.score);
  else if(sort==='date') jobs.sort((a,b)=>(b.date_added||'').localeCompare(a.date_added||''));
  else jobs.sort((a,b)=>(a.title||'').localeCompare(b.title||''));
  document.getElementById('dataInfo').textContent=jobs.length+' Stellen · '+new Set(jobs.map(j=>j.source)).size+' Quellen';
  const grid=document.getElementById('grid');
  if(!jobs.length){grid.innerHTML='<div id="noResults">Keine Stellen gefunden.</div>';return;}
  grid.innerHTML=jobs.map(j=>renderCard(j)).join('');
}
function updateNeuBadge(){
  const maxDate=ALL_JOBS.reduce((m,j)=>j.date_added>m?j.date_added:m,'');
  document.getElementById('neu-badge').textContent=ALL_JOBS.filter(j=>j.date_added===maxDate).length;
}
// ── Scoring-Editor ──
const PROFILE_KEY = 'bewe_profile_v1';
function loadProfile(){
  try{
    const s = localStorage.getItem(PROFILE_KEY);
    if(s) return JSON.parse(s);
  } catch(e){}
  return JSON.parse(JSON.stringify(PROFILE_SCORING));
}
function saveProfile(){
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profileData));
  const el = document.getElementById('scores-status');
  if(el){ el.textContent='&#10003; Gespeichert'; clearTimeout(el._t); el._t=setTimeout(()=>el.textContent='',2000); }
}
let profileData = loadProfile();

function esc2(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function renderScoresEditor(){
  const p = profileData;
  let html = '';

  // Basis-Score
  html += '<div class="crit-card"><div class="base-row">'
    + '<label>&#9889; Basis-Score (Ausgangswert jeder Stelle)</label>'
    + '<input type="number" id="pe-base" value="'+p.base+'" min="0" max="200" style="width:70px;border:1px solid #ddd;border-radius:6px;padding:5px 8px;font-size:14px;font-weight:700;text-align:right" onchange="profileData.base=parseInt(this.value)||0;saveProfile()">'
    + '<span style="font-size:12px;color:#888">Punkte</span>'
    + '</div></div>';

  // Exclude-Blöcke
  ['hard_exclude','tech_exclude'].forEach(key=>{
    const ex = p[key];
    const label = key==='hard_exclude' ? '&#128683; Hard-Exclude' : '&#9888; Tech-Exclude';
    html += '<div class="crit-card exclude-card">'
      + '<div class="crit-header">'
      + '<span class="crit-name">'+label+'</span>'
      + '<div class="crit-pts"><span>&#8594; Score:</span>'
      + '<input type="number" value="'+ex.score+'" min="0" max="50" onchange="profileData[\''+key+'\'].score=parseInt(this.value)||0;saveProfile()"></div>'
      + '</div>'
      + '<div class="terms-area" id="terms-'+key+'">'
      + ex.terms.map((t,i)=>'<span class="term-pill exclude-pill">'+esc2(t)
          +'<button onclick="removeTerm(\''+key+'\',null,'+i+')" title="Entfernen">&times;</button></span>').join('')
      + '<div class="term-add"><input type="text" id="ti-'+key+'" placeholder="Begriff..." onkeydown="if(event.key===\'Enter\')addTerm(\''+key+'\',null)">'
      + '<button onclick="addTerm(\''+key+'\',null)">&#65291;</button></div>'
      + '</div></div>';
  });

  // Dynamische Kriterien
  html += '<div id="crit-list">';
  p.criteria.forEach((c,i)=>{
    const hasSalary = 'salary_threshold' in c;
    html += '<div class="crit-card" id="crit-'+i+'">'
      + '<div class="crit-header">'
      + '<div class="crit-name"><input type="text" value="'+esc2(c.name)+'" placeholder="Name" onchange="profileData.criteria['+i+'].name=this.value;saveProfile()"></div>'
      + '<div class="crit-pts">';
    if(hasSalary){
      html += '<span>Gehalt &#8805;</span>'
        + '<input type="number" value="'+(c.salary_threshold||75000)+'" min="0" step="1000" onchange="profileData.criteria['+i+'].salary_threshold=parseInt(this.value)||0;saveProfile()">'
        + '<span>€ &rarr;</span>';
    }
    html += '<input type="number" value="'+c.points+'" min="0" max="200" onchange="profileData.criteria['+i+'].points=parseInt(this.value)||0;saveProfile()">'
      + '<span>Pkt</span></div>'
      + '<button class="crit-del" onclick="removeCriteria('+i+')" title="Kriterium l&ouml;schen">&#128465;</button>'
      + '</div>';
    if(!hasSalary){
      html += '<div class="terms-area" id="terms-crit-'+i+'">'
        + (c.terms||[]).map((t,ti)=>'<span class="term-pill">'+esc2(t)
            +'<button onclick="removeTerm(\'criteria\','+i+','+ti+')" title="Entfernen">&times;</button></span>').join('')
        + '<div class="term-add"><input type="text" id="ti-crit-'+i+'" placeholder="Begriff..." onkeydown="if(event.key===\'Enter\')addTerm(\'criteria\','+i+')">'
        + '<button onclick="addTerm(\'criteria\','+i+')">&#65291;</button></div>'
        + '</div>';
    }
    html += '</div>';
  });
  html += '</div>';

  // Neues Kriterium
  html += '<button class="btn-ghost" style="margin-bottom:16px" onclick="addCriteria()">&#65291; Neues Kriterium</button>';

  document.getElementById('scores-editor').innerHTML = html;
}

function addTerm(type, idx){
  const id = type==='criteria' ? 'ti-crit-'+idx : 'ti-'+type;
  const el = document.getElementById(id);
  const val = (el.value||'').trim();
  if(!val) return;
  if(type==='criteria') { profileData.criteria[idx].terms = profileData.criteria[idx].terms||[]; profileData.criteria[idx].terms.push(val); }
  else profileData[type].terms.push(val);
  el.value='';
  saveProfile(); renderScoresEditor();
}

function removeTerm(type, idx, ti){
  if(type==='criteria') profileData.criteria[idx].terms.splice(ti,1);
  else profileData[type].terms.splice(ti,1);
  saveProfile(); renderScoresEditor();
}

function addCriteria(){
  profileData.criteria.push({name:'neu',points:10,terms:[]});
  saveProfile(); renderScoresEditor();
}

function removeCriteria(i){
  profileData.criteria.splice(i,1);
  saveProfile(); renderScoresEditor();
}

function resetProfile(){
  localStorage.removeItem(PROFILE_KEY);
  profileData = JSON.parse(JSON.stringify(PROFILE_SCORING));
  renderScoresEditor();
  const el = document.getElementById('scores-status');
  el.textContent='Zur&uuml;ckgesetzt'; clearTimeout(el._t); el._t=setTimeout(()=>el.textContent='',2000);
}

function downloadProfile(){
  const blob = new Blob([JSON.stringify(profileData,null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'profile.json';
  a.click();
}

jobStatus=loadStatus();
buildSourceFilter();
render();
updateNeuBadge();
"""

# HTML zusammenbauen (nur die dynamischen Teile brauchen f-string)
HEADER = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Briefing BEWE</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>&#127919; Job Briefing BEWE</h1>
  <div class="sub">T&auml;glich aktualisiert &middot; Zuletzt: {NOW} &middot; {new_today} neue Stellen heute
    <button onclick="location.reload(true)" title="Seite neu laden" style="margin-left:10px;font-family:Roboto,Arial,sans-serif;font-size:12px;color:#5F6368;background:#F1F3F4;border:1px solid #DADCE0;border-radius:6px;padding:3px 10px;cursor:pointer;vertical-align:middle">&#128260; Aktualisieren</button>
  </div>
  <div class="tab-nav">
    <button class="tab-btn active" onclick="showTab('overview')" id="tab-overview">&#128203; &Uuml;bersicht</button>
    <button class="tab-btn" onclick="showTab('neu')" id="tab-neu">&#127381; NEU <span id="neu-badge" style="background:#e53935;color:white;border-radius:10px;padding:1px 7px;font-size:11px;margin-left:4px;vertical-align:middle">0</span></button>
    <button class="tab-btn" onclick="showTab('scores')" id="tab-scores">&#127919; Scoring</button>
  </div>
</div>

<div id="page-overview" class="page active">
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
<div class="status-filter">
  <button class="sf-btn active" data-sf="active"   onclick="setStatusFilter('active')">&#128269; Aktiv <span class="sf-cnt" id="cnt-active">0</span></button>
  <button class="sf-btn" data-sf="starred"         onclick="setStatusFilter('starred')">&#11088; Gemerkt <span class="sf-cnt" id="cnt-starred">0</span></button>
  <button class="sf-btn" data-sf="applied"         onclick="setStatusFilter('applied')">&#10003; Beworben <span class="sf-cnt" id="cnt-applied">0</span></button>
  <button class="sf-btn" data-sf="archived"        onclick="setStatusFilter('archived')">&#128230; Archiv <span class="sf-cnt" id="cnt-archived">0</span></button>
  <button class="sf-btn" data-sf="all"             onclick="setStatusFilter('all')">&#128203; Alle <span class="sf-cnt" id="cnt-all">0</span></button>
</div>
<div class="grid" id="grid"></div>
</div>

<div id="page-neu" class="page">
  <div class="neu-info" id="neu-info">-</div>
  <div class="grid" id="grid-neu"></div>
</div>

<div id="page-scores" class="page">
  <div class="scores-page">
    <div id="scores-editor"><!-- wird per JS befuellt --></div>
    <div class="scores-toolbar">
      <button class="btn-ghost"   onclick="downloadProfile()">&#128190; Exportieren (profile.json)</button>
      <button class="btn-ghost"   onclick="resetProfile()">&#8635; Auf Standard zurücksetzen</button>
      <span class="scores-status" id="scores-status"></span>
    </div>
    <div style="margin-top:16px;padding:14px 16px;background:#f8f9ff;border:1px solid #e0e4f0;border-radius:10px;font-size:12px;color:#555;line-height:1.7">
      <strong style="color:#1a1a2e">So wird der ge&auml;nderte Score zum neuen Standard:</strong><br>
      Pfad der Quelldatei:<br>
      <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 6px;border-radius:4px;display:inline-block;margin:4px 0">C:\\Users\\joerg\\OneDrive - die-weboptimierer\\Dokumente\\Claude\\Scheduled\\job-briefing-bewe\\profile.json</code><br><br>
      Das ist der <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 4px;border-radius:4px">PROFILE_PATH</code> in <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 4px;border-radius:4px">generate.py</code>.
      Beim n&auml;chsten Lauf von <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 4px;border-radius:4px">generate.py</code> (t&auml;glich automatisch oder manuell)
      wird diese Datei eingelesen und als <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 4px;border-radius:4px">PROFILE_SCORING</code> in die HTML eingebettet &mdash;
      das wird dann der neue &bdquo;Standard zur&uuml;cksetzen&ldquo;-Wert.<br><br>
      <strong>Ablauf:</strong> Im Browser bearbeiten &rarr; Exportieren &rarr; Datei an obigen Pfad kopieren &rarr; <code style="font-size:11px;background:#eef1ff;color:#3a3a8a;padding:2px 4px;border-radius:4px">generate.py</code> l&auml;uft &rarr; neuer Standard ist eingebettet.
    </div>
  </div>
</div>

<div class="footer">Stand {TODAY} &middot; {total} Stellen &middot; {sources} Quellen &middot; automatisch generiert</div>
<script>
const TODAY = '{TODAY}';
const ALL_JOBS = {jobs_json};
const INITIAL_STATUS = {status_json};
const PROFILE_SCORING = {profile_json};
"""

FOOTER = """</script>
</body>
</html>"""

# CLOUD_MODE: nur aktiv wenn explizit CLOUD=1 gesetzt UND GITHUB_ACTIONS gesetzt (Runner-Schutz)
CLOUD_MODE = os.environ.get('CLOUD', '0') == '1' and os.environ.get('GITHUB_ACTIONS') == 'true'

if CLOUD_MODE and os.path.exists(OUT_PATH):
    # Patch-Modus: bestehende index.html mit neuen Daten aktualisieren
    # (bewahrt alle manuellen UI-Erweiterungen wie Absender-Tab, GitHub-API-Save)
    with open(OUT_PATH, encoding='utf-8') as f:
        html = f.read()

    html = re.sub(r"const TODAY = '[^']*';",                f"const TODAY = '{TODAY}';",               html)
    # ALL_JOBS kann ein- oder mehrzeilig sein – [\s\S]*? stoppt am ersten ];
    html = re.sub(r'const ALL_JOBS = \[[\s\S]*?\];',        f'const ALL_JOBS = {jobs_json};',          html)
    html = re.sub(r'const INITIAL_STATUS = \{[\s\S]*?\};',  f'const INITIAL_STATUS = {status_json};',  html)
    html = re.sub(r'const PROFILE_SCORING = \{[\s\S]*?\};', f'const PROFILE_SCORING = {profile_json};',html)
    html = re.sub(r'Zuletzt: \d{4}-\d{2}-\d{2}( \d{2}:\d{2})? &middot; \d+ neue Stellen heute',
                  f'Zuletzt: {NOW} &middot; {new_today} neue Stellen heute', html)
    html = re.sub(r'Stand \d{4}-\d{2}-\d{2} &middot; \d+ Stellen &middot; \d+ Quellen',
                  f'Stand {TODAY} &middot; {total} Stellen &middot; {sources} Quellen', html)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"OK: index.html gepatcht (Cloud-Modus) – {total} Jobs, {new_today} neu heute, Stand {TODAY}")
else:
    # Rebuild-Modus: komplette index.html aus Template neu erzeugen (lokaler Lauf)
    html = HEADER + JS + FOOTER
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"OK: index.html generiert – {total} Jobs, {new_today} neu heute, Stand {TODAY}")
