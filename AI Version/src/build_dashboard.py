"""Builds dashboard.html — a fully self-contained interactive dashboard.
Chart.js and the aggregated data are inlined so the file works offline.
Usage: python3 src/build_dashboard.py  (run src/analysis.py first)"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "assets", "dashboard_data.json")))
chartjs = open(os.path.join(ROOT, "assets", "chart.umd.min.js")).read()

HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Employee Performance & Productivity — Analytics Dashboard</title>
<style>
  :root{
    --bg:#0f172a; --card:#1e293b; --card2:#172033; --border:#334155;
    --text:#e2e8f0; --muted:#94a3b8; --sky:#38bdf8; --emerald:#34d399;
    --amber:#fbbf24; --red:#f87171; --violet:#a78bfa; --orange:#fb923c;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,-apple-system,sans-serif;padding:24px 32px 48px}
  header{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between;margin-bottom:22px}
  h1{font-size:26px;font-weight:800;letter-spacing:-0.4px}
  h1 span{color:var(--sky)}
  .sub{color:var(--muted);font-size:13px;margin-top:4px}
  select{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:10px;
         padding:10px 14px;font-size:14px;outline:none;cursor:pointer;min-width:230px}
  select:hover{border-color:var(--sky)}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}
  .kpi{background:linear-gradient(160deg,var(--card),var(--card2));border:1px solid var(--border);
       border-radius:14px;padding:14px 16px}
  .kpi .v{font-size:22px;font-weight:800}
  .kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-top:3px}
  .kpi.sky .v{color:var(--sky)} .kpi.emerald .v{color:var(--emerald)}
  .kpi.amber .v{color:var(--amber)} .kpi.red .v{color:var(--red)}
  .kpi.violet .v{color:var(--violet)} .kpi.orange .v{color:var(--orange)}
  .grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}
  .panel{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 18px 12px}
  .panel h3{font-size:14px;font-weight:700;margin-bottom:2px}
  .panel .note{font-size:11px;color:var(--muted);margin-bottom:8px}
  .c4{grid-column:span 4}.c6{grid-column:span 6}.c3{grid-column:span 3}.c12{grid-column:span 12}
  .chart-wrap{position:relative;height:250px}
  .chart-wrap.tall{height:290px}
  .chart-wrap.short{height:210px}
  .findings{margin-top:26px}
  .findings h2{font-size:19px;margin-bottom:12px}
  .fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
  .finding{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--sky);
           border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.55;color:#cbd5e1}
  .finding b{color:var(--text)}
  .finding.good{border-left-color:var(--emerald)}
  .finding.warn{border-left-color:var(--amber)}
  .finding.bad{border-left-color:var(--red)}
  .badge{display:inline-block;background:var(--card2);border:1px solid var(--border);color:var(--muted);
         border-radius:999px;padding:4px 12px;font-size:11px;margin-left:6px}
  footer{margin-top:30px;color:var(--muted);font-size:12px;border-top:1px solid var(--border);padding-top:14px}
  @media(max-width:1100px){.c4,.c3{grid-column:span 6}}
  @media(max-width:760px){.c4,.c3,.c6{grid-column:span 12}}
</style>
</head>
<body>
<header>
  <div>
    <h1>Employee Performance &amp; Productivity <span>Dashboard</span></h1>
    <div class="sub">100,000 employees · 9 departments · 7 job titles · hires 2014–2024 · fully offline, single-file</div>
  </div>
  <div>
    <select id="deptSel" onchange="render()"></select>
    <span class="badge" id="cntBadge"></span>
  </div>
</header>

<div class="kpis" id="kpis"></div>

<div class="grid">
  <div class="panel c4"><h3>Headcount by Department</h3><div class="note">share of total workforce</div><div class="chart-wrap"><canvas id="cHead"></canvas></div></div>
  <div class="panel c4"><h3>Avg Salary by Department</h3><div class="note">USD / month · mean</div><div class="chart-wrap"><canvas id="cSalDept"></canvas></div></div>
  <div class="panel c4"><h3>Attrition by Department</h3><div class="note">% resigned · all near 10%</div><div class="chart-wrap"><canvas id="cAttDept"></canvas></div></div>

  <div class="panel c6"><h3>Salary by Job Title &amp; Gender</h3><div class="note">no meaningful pay gap — within ±$25 for every title</div><div class="chart-wrap tall"><canvas id="cGender"></canvas></div></div>
  <div class="panel c6"><h3>Salary Drivers (Linear Model, R² = 0.99)</h3><div class="note">pay ≈ job-title premium + $493 per performance point</div><div class="chart-wrap tall"><canvas id="cModel"></canvas></div></div>

  <div class="panel c4"><h3>Salary Distribution</h3><div class="note" id="nSalDist"></div><div class="chart-wrap"><canvas id="cSalDist"></canvas></div></div>
  <div class="panel c4"><h3>Performance Mix</h3><div class="note" id="nPerfMix"></div><div class="chart-wrap"><canvas id="cPerfMix"></canvas></div></div>
  <div class="panel c4"><h3>Workforce Demographics</h3><div class="note">gender mix · selected scope</div><div class="chart-wrap"><canvas id="cGenderPie"></canvas></div></div>

  <div class="panel c4"><h3>Education Mix</h3><div class="note">selected scope</div><div class="chart-wrap"><canvas id="cEduPie"></canvas></div></div>
  <div class="panel c4"><h3>Avg Salary by Tenure</h3><div class="note">salary tracks job title &amp; performance, not seniority</div><div class="chart-wrap"><canvas id="cTenure"></canvas></div></div>
  <div class="panel c4"><h3>Attrition by Remote-Work %</h3><div class="note">flat — remote policy has no attrition signal</div><div class="chart-wrap"><canvas id="cRemote"></canvas></div></div>

  <div class="panel c6"><h3>Attrition vs Satisfaction &amp; Performance</h3><div class="note">no gradient in either dimension</div><div class="chart-wrap"><canvas id="cDrivers"></canvas></div></div>
  <div class="panel c6"><h3>Job Titles in Scope</h3><div class="note">headcount by title</div><div class="chart-wrap"><canvas id="cTitles"></canvas></div></div>
</div>

<section class="findings">
  <h2>Key Findings</h2>
  <div class="fgrid">
    <div class="finding good"><b>Pay equity is healthy.</b> Women earn on average <b>$4.50 more</b> than men company-wide; within every job title the gap stays under <b>±$25</b> (0.4% of pay). No corrective action needed — keep monitoring.</div>
    <div class="finding"><b>Salary is almost fully explained.</b> A linear model of job title + performance + demographics reaches <b>R² = 0.99</b> (MAE ≈ $95). Engineers/Managers earn ≈ <b>+$2,600</b> and each performance point adds ≈ <b>+$493</b>/month. Department, education and gender add ~nothing.</div>
    <div class="finding bad"><b>Attrition is statistically unpredictable here.</b> Both models land at <b>AUC ≈ 0.49</b> (coin-flip). Every segment — satisfaction, performance, tenure, remote work, overtime — sits within <b>9.5%–10.3%</b> of the 10.0% company rate. Leavers cannot be identified from this data; investigate data quality &amp; exit-interview capture.</div>
    <div class="finding warn"><b>Engagement levers show no signal.</b> Training hours, overtime, sick days, team size and remote frequency show |r| &lt; 0.01 against performance and satisfaction. Before investing more in these levers, verify how performance is measured.</div>
    <div class="finding"><b>Departments are remarkably uniform.</b> Headcount (10,956–11,216), avg salary ($6,378–$6,417), performance (2.98–3.02) and attrition (9.6%–10.5%) barely differ across all 9 departments.</div>
    <div class="finding warn"><b>Data looks synthetic.</b> Independent feature generation, uniform segments and a near-perfect salary formula are hallmarks of simulated data. Treat conclusions as a demonstration of the analysis pipeline, not as organizational truth.</div>
  </div>
</section>

<footer>
  Generated by the reproducible pipeline in <code>src/</code> — run <code>python3 src/analysis.py && python3 src/build_dashboard.py</code> to rebuild.
  Models: Logistic Regression &amp; Random Forest (attrition, 80/20 stratified split), OLS (salary). All charts rendered locally with Chart.js 4.4.1 (inlined). Data: Extended_Employee_Performance_and_Productivity_Data.csv (100,000 rows × 20 cols).
</footer>

<script>
"""

HTML_TAIL = """
</script>
</body>
</html>
"""

JS = r"""
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Segoe UI',system-ui,sans-serif";
Chart.defaults.plugins.legend.labels.boxWidth = 12;
const GRID = { color: '#28374f' };
const C = { sky:'#38bdf8', emerald:'#34d399', amber:'#fbbf24', red:'#f87171',
            violet:'#a78bfa', orange:'#fb923c', slate:'#64748b', teal:'#2dd4bf' };
const CHARTS = {};
const kpisEl = document.getElementById('kpis');
const cntBadge = document.getElementById('cntBadge');

function scope(){ return deptSel.value === 'All' ? DATA.all : DATA.depts[deptSel.value]; }

function fmtMoney(v){ return '$' + Number(v).toLocaleString('en-US'); }

function kpiCards(){
  const s = scope(), k = DATA.kpis;
  const cards = [
    ['sky',    s.headcount.toLocaleString('en-US'), 'Employees in scope'],
    ['emerald',fmtMoney(s.avg_salary),              'Avg monthly salary'],
    ['violet', s.avg_performance.toFixed(2),        'Avg performance (1–5)'],
    ['amber',  s.attrition.toFixed(1) + '%',        'Attrition rate'],
    ['sky',    s.avg_satisfaction.toFixed(2),       'Avg satisfaction'],
    ['orange', s.avg_hours.toFixed(1) + 'h',        'Avg work hours/wk'],
    ['red',    s.high_perf_pct.toFixed(1) + '%',    'High performers (4–5)'],
    ['emerald',s.avg_tenure.toFixed(1) + 'y',       'Avg tenure'],
    ['violet', s.avg_training.toFixed(0) + 'h',     'Avg training hours'],
    ['amber',  s.avg_projects.toFixed(1),           'Avg projects handled'],
  ];
  kpisEl.innerHTML = cards.map(([c,v,l]) =>
    `<div class="kpi ${c}"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');
  cntBadge.textContent = 'scope: ' + (deptSel.value === 'All' ? 'company' : deptSel.value);
}

function mk(id, cfg){
  if (CHARTS[id]) CHARTS[id].destroy();
  CHARTS[id] = new Chart(document.getElementById(id), cfg);
}

function render(){
  const s = scope();
  kpiCards();

  // 1. headcount by department (always company view, highlight selection)
  const dNames = Object.keys(DATA.depts);
  const hl = deptSel.value;
  mk('cHead', { type:'bar',
    data:{ labels:dNames, datasets:[{ data:dNames.map(d=>DATA.depts[d].headcount),
      backgroundColor:dNames.map(d=> d===hl ? C.sky : '#33507a'), borderRadius:5 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:{display:false},ticks:{maxRotation:60,minRotation:45,font:{size:9}}}, y:{grid:GRID, ticks:{callback:v=>(v/1000)+'k'}} } } });

  // 2. salary by dept
  mk('cSalDept', { type:'bar',
    data:{ labels:dNames, datasets:[{ data:dNames.map(d=>DATA.salary_by_dept[d]),
      backgroundColor:dNames.map(d=> d===hl ? C.emerald : '#2e5d4f'), borderRadius:5 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:{display:false},ticks:{maxRotation:60,minRotation:45,font:{size:9}}},
               y:{grid:GRID, suggestedMin:6000, suggestedMax:6600, ticks:{callback:v=>'$'+v}} } } });

  // 3. attrition by dept
  mk('cAttDept', { type:'bar',
    data:{ labels:dNames, datasets:[{ data:dNames.map(d=>DATA.attrition_by_dept[d]),
      backgroundColor:dNames.map(d=> d===hl ? C.amber : '#6b5a2e'), borderRadius:5 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>c.parsed.y+'% resigned'}}},
      scales:{ x:{grid:{display:false},ticks:{maxRotation:60,minRotation:45,font:{size:9}}},
               y:{grid:GRID, suggestedMin:8.5, suggestedMax:11.5, ticks:{callback:v=>v+'%'}} } } });

  // 4. gender × title salary
  const titles = Object.keys(DATA.gender_by_title).sort();
  const genders = Object.keys(DATA.gender_by_title[titles[0]]);
  const gColors = {Male:C.sky, Female:C.violet, 'Non-binary/Other':C.orange};
  mk('cGender', { type:'bar',
    data:{ labels:titles, datasets:genders.map(g=>({ label:g,
      data:titles.map(t=>DATA.gender_by_title[t][g]), backgroundColor:gColors[g]||C.slate, borderRadius:4 })) },
    options:{ maintainAspectRatio:false,
      scales:{ x:{grid:{display:false},ticks:{font:{size:10}}}, y:{grid:GRID, ticks:{callback:v=>'$'+v}} } } });

  // 5. salary model drivers
  const drv = [['Engineer',2600],['Manager',2599],['Consultant',1951],['Developer',1300],
               ['Specialist',650],['Perf point',493],['Technician',-648],['Everything else','~0']];
  mk('cModel', { type:'bar',
    data:{ labels:drv.map(d=>d[0]), datasets:[{ data:drv.map(d=>d[1]),
      backgroundColor:drv.map(d=> typeof d[1]==='number' ? (d[1]>=0?C.emerald:C.red) : C.slate), borderRadius:4 }] },
    options:{ indexAxis:'y', maintainAspectRatio:false, plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=> typeof c.parsed.x==='number' ? (c.parsed.x>=0?'+':'')+'$'+c.parsed.x+'/mo' : 'under $3'}}},
      scales:{ x:{grid:GRID, ticks:{callback:v=>'$'+v}}, y:{grid:{display:false},ticks:{font:{size:10}}} } } });

  // 6. salary distribution (scope)
  mk('cSalDist', { type:'bar',
    data:{ labels:DATA.salary_bin_labels.map(b=>'$'+b), datasets:[{ data:s.salary_bins,
      backgroundColor:C.sky, borderRadius:3 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:{display:false},ticks:{maxRotation:60,minRotation:45,font:{size:8},
        callback:(v,i)=> i%2===0 ? '$'+DATA.salary_bin_labels[i] : ''}}, y:{grid:GRID, ticks:{callback:v=>(v/1000)+'k'}} } } });
  document.getElementById('nSalDist').textContent =
    'scope mean ' + fmtMoney(s.avg_salary) + ' · median ' + fmtMoney(s.median_salary);

  // 7. performance mix (scope)
  const perfColors = ['#ef4444','#fb923c','#fbbf24','#4ade80','#22c55e'];
  mk('cPerfMix', { type:'bar',
    data:{ labels:['Score 1','Score 2','Score 3','Score 4','Score 5'],
      datasets:[{ data:['1','2','3','4','5'].map(k=>s.perf_dist[k]||0), backgroundColor:perfColors, borderRadius:4 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:{display:false}}, y:{grid:GRID, ticks:{callback:v=>(v/1000)+'k'}} } } });
  document.getElementById('nPerfMix').textContent =
    s.high_perf_pct.toFixed(1) + '% rate 4–5 · avg ' + s.avg_performance.toFixed(2);

  // 8. gender pie
  mk('cGenderPie', { type:'doughnut',
    data:{ labels:Object.keys(s.gender), datasets:[{ data:Object.values(s.gender),
      backgroundColor:[C.sky,C.violet,C.orange], borderColor:'#1e293b', borderWidth:2 }] },
    options:{ maintainAspectRatio:false, cutout:'58%',
      plugins:{legend:{position:'bottom'}, tooltip:{callbacks:{
        label:c=>c.label+': '+(c.parsed*100/s.headcount).toFixed(1)+'%'}}} } });

  // 9. education pie
  const eduColors = {Bachelor:C.teal, 'High School':C.amber, Master:C.violet, PhD:C.emerald};
  mk('cEduPie', { type:'doughnut',
    data:{ labels:Object.keys(s.education), datasets:[{ data:Object.values(s.education),
      backgroundColor:Object.keys(s.education).map(k=>eduColors[k]||C.slate),
      borderColor:'#1e293b', borderWidth:2 }] },
    options:{ maintainAspectRatio:false, cutout:'58%',
      plugins:{legend:{position:'bottom'}, tooltip:{callbacks:{
        label:c=>c.label+': '+(c.parsed*100/s.headcount).toFixed(1)+'%'}}} } });

  // 10. salary by tenure (scope)
  const tenK = Object.keys(s.tenure_salary).map(Number).sort((a,b)=>a-b);
  mk('cTenure', { type:'line',
    data:{ labels:tenK.map(k=>k+'y'), datasets:[{ data:tenK.map(k=>s.tenure_salary[k]),
      borderColor:C.violet, backgroundColor:'rgba(167,139,250,.15)', fill:true, tension:.3, pointRadius:3 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:{display:false}}, y:{grid:GRID, suggestedMin:5800, suggestedMax:7000, ticks:{callback:v=>'$'+v}} } } });

  // 11. remote attrition (scope)
  const remK = Object.keys(s.remote_attrition).map(Number).sort((a,b)=>a-b);
  mk('cRemote', { type:'line',
    data:{ labels:remK.map(k=>k+'%'), datasets:[{ data:remK.map(k=>s.remote_attrition[k]),
      borderColor:C.emerald, backgroundColor:'rgba(52,211,153,.12)', fill:true, tension:.3, pointRadius:4 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>c.parsed.y+'% resigned'}}},
      scales:{ x:{grid:{display:false},title:{display:true,text:'remote frequency'}},
               y:{grid:GRID, suggestedMin:8, suggestedMax:12, ticks:{callback:v=>v+'%'}} } } });

  // 12. attrition drivers
  const satD = DATA.attrition_drivers['Satisfaction bucket'];
  const perfD = DATA.attrition_drivers['Performance score'];
  mk('cDrivers', { type:'bar',
    data:{ labels:['Sat 1–2','Sat 2–3','Sat 3–4','Sat 4–5','Perf 1','Perf 2','Perf 3','Perf 4','Perf 5'],
      datasets:[{ label:'Attrition %',
        data:[satD['1–2 (low)'],satD['2–3'],satD['3–4'],satD['4–5 (high)'],
              perfD['1'],perfD['2'],perfD['3'],perfD['4'],perfD['5']],
        backgroundColor:['#7c6bd6','#7c6bd6','#7c6bd6','#7c6bd6','#5b8cc8','#5b8cc8','#5b8cc8','#5b8cc8','#5b8cc8'],
        borderRadius:4 }] },
    options:{ maintainAspectRatio:false, plugins:{legend:{display:false},
      annotation:undefined, tooltip:{callbacks:{label:c=>c.parsed.y+'% resigned'}}},
      scales:{ x:{grid:{display:false},ticks:{font:{size:9},maxRotation:45,minRotation:30}},
               y:{grid:GRID, suggestedMin:9, suggestedMax:11, ticks:{callback:v=>v+'%'}} } } });

  // 13. job titles in scope
  const tNames = Object.keys(s.job_titles).sort();
  mk('cTitles', { type:'bar',
    data:{ labels:tNames, datasets:[{ data:tNames.map(t=>s.job_titles[t]),
      backgroundColor:C.teal, borderRadius:4 }] },
    options:{ indexAxis:'y', maintainAspectRatio:false, plugins:{legend:{display:false}},
      scales:{ x:{grid:GRID, ticks:{callback:v=>(v/1000)+'k'}}, y:{grid:{display:false},ticks:{font:{size:10}}} } } });
}

// init
const deptSel = document.getElementById('deptSel');
['All', ...Object.keys(DATA.depts)].forEach(d=>{
  const o = document.createElement('option');
  o.value = d; o.textContent = d === 'All' ? '🏢  All departments' : d;
  deptSel.appendChild(o);
});
render();
"""

html = (HTML_HEAD
        + "const DATA = " + json.dumps(data) + ";\n"
        + chartjs + "\n"
        + JS
        + HTML_TAIL)

out = os.path.join(ROOT, "dashboard.html")
with open(out, "w") as f:
    f.write(html)
print("wrote", out, f"({os.path.getsize(out)/1024:.0f} KB)")
