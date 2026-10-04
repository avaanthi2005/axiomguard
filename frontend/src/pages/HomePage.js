import React from 'react';
import { Link } from 'react-router-dom';

const scanRows = [
  { domain: 'www.zonsexample.com', status: 'CLEAN', cve: 0 },
  { domain: 'example.com', status: 'OPEN PORTS', cve: 23 },
  { domain: 'www.tirotexs.com', status: 'CLEAN', cve: 13 },
  { domain: 'marchcanter.com', status: 'CLEAN', cve: 0 },
  { domain: 'oircaxample.com', status: 'CLEAN', cve: 0 },
];

const historyRows = [
  { domain: 'www.centexample.com', status: 'OPEN PORTS', cve: 2, age: 43 },
  { domain: 'www.qfcexample.com', status: 'CLEAN', cve: 19, age: 36 },
  { domain: 'www.dhaxample.com', status: 'OPEN PORTS', cve: 22, age: 29 },
  { domain: 'www.asiaxample.com', status: 'CLEAN', cve: 13, age: 17 },
  { domain: 'www.onxample.com', status: 'OPEN PORTS', cve: 12, age: 18 },
];

const phishFlags = [
  { label: 'Detected typosquatting (domain)', domain: 'www.accesses-penpmes.com' },
  { label: 'Detected typosquatting (subdomain)', domain: 'bookawels.com' },
  { label: 'Suspicious spoof senders', domain: 'suspicioustlc.com' },
];

const guardConnections = ['Connections-slo', 'Connection', 'Backdoors', 'Connections', 'Connects', 'Hiddenlististe', 'DNS leak/exeirt', 'Critical entrypoint'];
const barHeights = [40, 65, 30, 80, 50, 90, 35, 70, 55, 25, 60, 45];
const barColors = ['#25d9ef', '#a875ff', '#36dfa8', '#ff9f5a'];

function NetworkGlobe() {
  return (
    <svg viewBox="0 0 420 420" className="ag-globe" aria-hidden="true">
      <defs><radialGradient id="ag-globe-glow" cx="50%" cy="45%" r="60%"><stop offset="0%" stopColor="#00d4ff33" /><stop offset="100%" stopColor="#00d4ff00" /></radialGradient></defs>
      <circle cx="210" cy="210" r="190" fill="url(#ag-globe-glow)" />
      <g className="ag-globe-rotate" stroke="#285078" strokeWidth="1" fill="none"><circle cx="210" cy="210" r="150" /><ellipse cx="210" cy="210" rx="150" ry="55" /><ellipse cx="210" cy="210" rx="150" ry="105" /><ellipse cx="210" cy="210" rx="55" ry="150" /><ellipse cx="210" cy="210" rx="105" ry="150" /></g>
      <g fill="none" strokeWidth="1.4"><path className="ag-arc" d="M120,150 Q210,60 300,180" stroke="#ff557e" /><path className="ag-arc ag-delay-1" d="M90,240 Q210,320 320,230" stroke="#ff557e" /><path className="ag-arc ag-delay-2" d="M140,300 Q210,250 280,120" stroke="#ff557e" /></g>
      <circle cx="120" cy="150" r="5" className="ag-dot ag-red" /><circle cx="300" cy="180" r="5" className="ag-dot ag-red" /><circle cx="90" cy="240" r="6" className="ag-dot ag-purple" /><circle cx="320" cy="230" r="4" className="ag-dot ag-red" /><circle cx="140" cy="300" r="6" className="ag-dot ag-purple" /><circle cx="280" cy="120" r="4" className="ag-dot ag-red" />
    </svg>
  );
}

function MiniMap({ dotColor = '#25d9ef', lineColor = '#25d9ef' }) {
  return (
    <svg viewBox="0 0 300 140" className="ag-mini-map" aria-hidden="true">
      <g stroke="#285078" strokeWidth=".6" opacity=".6">{Array.from({ length: 6 }).map((_, i) => <line key={`h${i}`} x1="0" y1={i * 24} x2="300" y2={i * 24} />)}{Array.from({ length: 10 }).map((_, i) => <line key={`v${i}`} x1={i * 30} y1="0" x2={i * 30} y2="140" />)}</g>
      <path d="M40,100 Q150,20 260,60" fill="none" stroke={lineColor} strokeWidth="1.2" className="ag-arc" /><path d="M60,40 Q150,110 230,110" fill="none" stroke={lineColor} strokeWidth="1.2" className="ag-arc ag-delay-1" />
      <circle cx="40" cy="100" r="4" className="ag-dot" style={{ fill: dotColor }} /><circle cx="260" cy="60" r="4" className="ag-dot" style={{ fill: dotColor }} /><circle cx="60" cy="40" r="4" className="ag-dot" style={{ fill: dotColor }} /><circle cx="230" cy="110" r="4" className="ag-dot" style={{ fill: dotColor }} />
    </svg>
  );
}

function AxiomGauge({ score = 92 }) {
  const pct = Math.min(1, Math.max(0, (score - 90) / 40));
  const angle = -90 + pct * 180;
  const color = score >= 120 ? '#36dfa8' : score >= 105 ? '#ffc267' : score >= 95 ? '#ff9f5a' : '#ff557e';
  return <div className="ag-gauge-wrap"><svg viewBox="0 0 200 110" width="180"><path d="M10,100 A90,90 0 0,1 190,100" fill="none" stroke="#234263" strokeWidth="14" strokeLinecap="round" /><path d="M10,100 A90,90 0 0,1 190,100" fill="none" stroke={color} strokeWidth="14" strokeLinecap="round" strokeDasharray={`${pct * 283} 283`} /><g transform={`rotate(${angle} 100 100)`}><line x1="100" y1="100" x2="100" y2="30" stroke="#fff" strokeWidth="3" /></g><circle cx="100" cy="100" r="6" fill="#fff" /></svg><div className="ag-score-number" style={{ color }}>{score}</div><div className="ag-score-label">AXIOMSCORE</div></div>;
}

function StatusBadge({ status }) { return <span className={`ag-badge ${status === 'CLEAN' ? 'ag-badge-green' : 'ag-badge-orange'}`}>{status}</span>; }

function GlassPanel({ children, className = '' }) { return <section className={`ag-panel ${className}`}>{children}</section>; }

export default function HomePage() {
  return (
    <>
      <style>{`
        .ag-home { --ag-text:#f5f9ff; --ag-muted:#8ea3c2; --ag-cyan:#25d9ef; position:relative; width:min(1280px,calc(100% - 42px)); margin:0 auto; padding:42px 0 80px; color:var(--ag-text); font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
        .ag-home,.ag-home *{box-sizing:border-box}.ag-home::before{content:'';position:fixed;z-index:-2;inset:0;pointer-events:none;background:radial-gradient(circle at 10% 28%,rgba(0,108,255,.2),transparent 28rem),radial-gradient(circle at 86% 4%,rgba(28,215,238,.13),transparent 25rem),linear-gradient(135deg,#02050d,#07152b 52%,#02050e)}.ag-home::after{content:'';position:fixed;z-index:-1;inset:0;pointer-events:none;opacity:.12;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 75%)}
        .ag-home-header{display:flex;align-items:flex-end;justify-content:space-between;gap:30px;margin-bottom:34px}.ag-overline{margin:0 0 12px;color:#63e7f7;font-size:11px;font-weight:800;letter-spacing:2.8px;text-transform:uppercase}.ag-home-title{margin:0;font-size:clamp(42px,6vw,72px);line-height:.95;letter-spacing:-4px}.ag-home-title em{color:var(--ag-cyan);font-style:normal;text-shadow:0 0 24px rgba(37,217,239,.3)}.ag-home-subtitle{max-width:455px;margin:0;color:var(--ag-muted);font-size:14px;line-height:1.75;text-align:right}.ag-system-pill{display:inline-flex;align-items:center;gap:8px;padding:9px 13px;margin-bottom:15px;color:#93badb;border:1px solid rgba(141,207,255,.22);border-radius:999px;background:rgba(31,71,112,.23);font-size:10px}.ag-system-dot{width:7px;height:7px;border-radius:50%;background:#42e0aa;box-shadow:0 0 13px #42e0aa}
        .ag-modules{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:18px}.ag-module{position:relative;min-height:210px;padding:25px;text-decoration:none;overflow:hidden;border:1px solid rgba(126,202,255,.22);border-radius:24px;background:linear-gradient(145deg,rgba(22,54,91,.56),rgba(6,18,39,.65));box-shadow:inset 0 1px 0 rgba(255,255,255,.13),0 18px 40px rgba(0,0,0,.18);transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease;backdrop-filter:blur(18px)}.ag-module::after{content:'';position:absolute;right:-60px;bottom:-80px;width:180px;height:180px;border-radius:50%;background:var(--module-glow);filter:blur(33px);opacity:.4}.ag-module:hover{transform:translateY(-6px);border-color:rgba(103,215,255,.5);box-shadow:inset 0 1px 0 rgba(255,255,255,.2),0 26px 55px rgba(0,0,0,.3),0 0 25px var(--module-glow)}.ag-module-cyan{--module-glow:#00c7ff}.ag-module-green{--module-glow:#10c889}.ag-module-purple{--module-glow:#a875ff}.ag-module-icon{display:grid;place-items:center;width:43px;height:43px;margin-bottom:24px;color:#d4f8ff;border:1px solid currentColor;border-radius:14px;background:rgba(41,177,255,.14);font-size:18px;box-shadow:0 0 22px var(--module-glow)}.ag-module h3{position:relative;z-index:1;margin:0 0 10px;font-size:14px;letter-spacing:1.1px}.ag-module p{position:relative;z-index:1;margin:0;color:#8fa5c2;font-size:12px;line-height:1.7}.ag-module-arrow{position:absolute;z-index:2;right:22px;top:23px;color:#6b8bab;font-size:21px}
        .ag-dashboard{position:relative;padding:26px;overflow:hidden;border:1px solid rgba(132,199,255,.25);border-radius:30px;background:linear-gradient(135deg,rgba(13,38,72,.65),rgba(4,14,31,.75));box-shadow:0 26px 80px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.15);backdrop-filter:blur(26px)}.ag-dashboard::before{content:'';position:absolute;left:38%;top:-280px;width:420px;height:420px;border-radius:50%;background:rgba(23,158,255,.13);filter:blur(40px)}.ag-dashboard-head{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.ag-dashboard-head h2{margin:0;font-size:16px;letter-spacing:-.3px}.ag-dashboard-head p{margin:0;color:#6f89aa;font-size:11px}.ag-dashboard-head span{color:#56dfc6}.ag-dashboard-grid{position:relative;z-index:1;display:grid;grid-template-columns:1.08fr .92fr;gap:17px;align-items:start}.ag-panel{position:relative;align-self:start;padding:22px;overflow:hidden;border:1px solid rgba(137,193,244,.17);border-radius:21px;background:linear-gradient(140deg,rgba(21,49,84,.58),rgba(6,17,36,.66));box-shadow:inset 0 1px 0 rgba(255,255,255,.09),0 14px 30px rgba(0,0,0,.14);backdrop-filter:blur(16px)}.ag-panel::after{content:'';position:absolute;right:-90px;top:-90px;width:180px;height:180px;border-radius:50%;background:rgba(50,184,255,.07);filter:blur(22px)}.ag-panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}.ag-panel-title{display:flex;align-items:center;gap:9px;color:#a9c4e1;font-size:12px;font-weight:800;letter-spacing:1.4px}.ag-panel-title b{color:var(--panel-color,#5ee3f4);font-weight:800}.ag-panel-meta{color:#657e9e;font-size:10px}.ag-table{width:100%;border-collapse:collapse;font-size:11px}.ag-table th{padding:0 5px 10px;color:#627c9d;font-size:9px;font-weight:700;letter-spacing:1px;text-align:left}.ag-table td{padding:10px 5px;border-top:1px solid rgba(131,183,232,.09);color:#b6c7dd}.ag-table td:first-child{color:#dceaff}.ag-badge{display:inline-flex;padding:5px 7px;border-radius:7px;font-size:8px;font-weight:800;letter-spacing:.7px}.ag-badge-green{color:#6be5b5;background:rgba(43,215,154,.12)}.ag-badge-orange{color:#ffc267;background:rgba(255,169,62,.13)}.ag-gauge-wrap{position:relative;width:190px;margin:4px auto -13px;text-align:center}.ag-score-number{position:absolute;left:0;right:0;bottom:14px;font-size:30px;font-weight:800}.ag-score-label{position:absolute;left:0;right:0;bottom:0;color:#6883a4;font-size:8px;font-weight:800;letter-spacing:1.6px}.ag-globe-card{min-height:360px}.ag-globe{position:absolute;right:-14px;top:-13px;width:370px;opacity:.82}.ag-globe-rotate{transform-origin:210px 210px;animation:ag-globe-spin 22s linear infinite}.ag-arc{stroke-dasharray:10 12;animation:ag-dash 4s linear infinite}.ag-delay-1{animation-delay:-1.4s}.ag-delay-2{animation-delay:-2.5s}.ag-dot{animation:ag-dot-pulse 1.8s ease-in-out infinite}.ag-red{fill:#ff557e}.ag-purple{fill:#a875ff}.ag-globe-caption{position:relative;z-index:1;max-width:190px;padding-top:216px}.ag-globe-caption small{display:block;margin-bottom:8px;color:#637c9d;font-size:9px;font-weight:800;letter-spacing:1.6px}.ag-globe-caption h3{margin:0 0 9px;font-size:21px;letter-spacing:-.8px}.ag-globe-caption p{margin:0;color:#7e96b4;font-size:11px;line-height:1.6}.ag-signal{position:relative;z-index:1;margin-top:9px;padding:10px 12px;border-left:2px solid #ff557e;border-radius:0 9px 9px 0;background:rgba(128,22,51,.16)}.ag-signal strong{display:block;color:#ff91a9;font-size:10px}.ag-signal span{display:block;margin-top:4px;color:#6f87a5;font-size:10px}.ag-wide{grid-column:1/-1}.ag-wide-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.ag-chart-label{margin:0 0 9px;color:#687f9d;font-size:9px;font-weight:800;letter-spacing:1.4px}.ag-bars{display:flex;align-items:flex-end;gap:6px;height:105px;padding:8px 0;border-bottom:1px solid rgba(128,179,227,.15)}.ag-bar{flex:1;min-width:4px;border-radius:4px 4px 1px 1px;box-shadow:0 0 10px currentColor;opacity:.82;animation:ag-bar-breathe 3s ease-in-out infinite alternate}.ag-history{margin-top:18px}.ag-ai{grid-column:1/-1;border-color:rgba(168,117,255,.3);background:linear-gradient(140deg,rgba(57,34,99,.3),rgba(6,17,36,.7))}.ag-ai p{margin:0;color:#99acca;font-size:12px;line-height:1.7}.ag-guard-tags{margin-top:14px;color:#6d85a3;font-size:10px;line-height:1.9}
        @keyframes ag-globe-spin{to{transform:rotate(360deg)}}@keyframes ag-dash{to{stroke-dashoffset:-90}}@keyframes ag-dot-pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 2px currentColor)}50%{opacity:.35;filter:drop-shadow(0 0 9px currentColor)}}@keyframes ag-bar-breathe{to{opacity:.45;transform:scaleY(.9)}}
        @media(max-width:900px){.ag-home-header{align-items:flex-start;flex-direction:column}.ag-home-subtitle{text-align:left}.ag-modules{grid-template-columns:1fr}.ag-dashboard-grid{grid-template-columns:1fr}.ag-globe-card{min-height:300px}.ag-wide{grid-column:auto}}@media(max-width:600px){.ag-home{width:calc(100% - 24px);padding-top:24px}.ag-home-title{font-size:47px;letter-spacing:-3px}.ag-dashboard{padding:14px;border-radius:23px}.ag-panel{padding:17px}.ag-wide-grid{grid-template-columns:1fr}.ag-globe{right:-70px;top:5px;width:330px;opacity:.46}.ag-globe-caption{padding-top:205px}.ag-table{font-size:10px}.ag-table th:nth-child(1),.ag-table td:nth-child(1){max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
      `}</style>

      <main className="ag-home">
        <header className="ag-home-header"><div><div className="ag-system-pill"><span className="ag-system-dot" /> AxiomGuard intelligence network / online</div><p className="ag-overline">Security command center</p><h1 className="ag-home-title">Guard what<br /><em>matters.</em></h1></div><p className="ag-home-subtitle">An AI-powered cybersecurity intelligence platform that turns complex signals into clear, actionable protection across your digital surface.</p></header>

        <section className="ag-modules">
          <Link to="/scan" className="ag-module ag-module-cyan"><span className="ag-module-arrow">↗</span><div className="ag-module-icon">⌁</div><h3 style={{ color: '#5ee3f4' }}>AXIOM//SCAN</h3><p>Audit domains for open ports, SSL issues, DNS misconfigurations, and known CVEs. Get your AxiomScore instantly.</p></Link>
          <Link to="/phish" className="ag-module ag-module-green"><span className="ag-module-arrow">↗</span><div className="ag-module-icon">◉</div><h3 style={{ color: '#52e5ae' }}>AXIOM//PHISH</h3><p>Detect phishing, typosquatting, obfuscation, and spoofed senders before they reach your people.</p></Link>
          <Link to="/guard" className="ag-module ag-module-purple"><span className="ag-module-arrow">↗</span><div className="ag-module-icon">◇</div><h3 style={{ color: '#c49aff' }}>AXIOM//GUARD</h3><p>Analyze website behavior for hidden iframes, obfuscated JavaScript, suspicious scripts, and more.</p></Link>
        </section>

        <section className="ag-dashboard">
          <div className="ag-dashboard-head"><div><h2>Live protection overview</h2><p>Aggregated telemetry from your security modules</p></div><span>● SYSTEM HEALTHY</span></div>
          <div className="ag-dashboard-grid">
            <GlassPanel><div className="ag-panel-head"><div className="ag-panel-title" style={{ '--panel-color': '#5ee3f4' }}><b>⌁</b> AXIOM//SCAN</div><span className="ag-panel-meta">LAST 24 HOURS</span></div><table className="ag-table"><thead><tr><th>DOMAIN</th><th>STATUS</th><th>CVE</th></tr></thead><tbody>{scanRows.map(r => <tr key={r.domain}><td>{r.domain}</td><td><StatusBadge status={r.status} /></td><td>{r.cve}</td></tr>)}</tbody></table><AxiomGauge score={92} /></GlassPanel>
            <GlassPanel className="ag-globe-card"><div className="ag-panel-head"><div className="ag-panel-title" style={{ '--panel-color': '#ff6d8c' }}><b>◎</b> THREAT MAP</div><span className="ag-panel-meta">GLOBAL ACTIVITY</span></div><NetworkGlobe /><div className="ag-globe-caption"><small>EXTERNAL SIGNALS</small><h3>6 active vectors</h3><p>Threat telemetry is being correlated across your monitored surface.</p></div></GlassPanel>
            <GlassPanel><div className="ag-panel-head"><div className="ag-panel-title" style={{ '--panel-color': '#52e5ae' }}><b>◉</b> AXIOM//PHISH</div><span className="ag-panel-meta">3 FLAGS</span></div><MiniMap dotColor="#ff557e" lineColor="#52e5ae88" />{phishFlags.map(f => <div className="ag-signal" key={f.domain}><strong>{f.label}</strong><span>{f.domain}</span></div>)}</GlassPanel>
            <GlassPanel><div className="ag-panel-head"><div className="ag-panel-title" style={{ '--panel-color': '#c49aff' }}><b>◇</b> AXIOM//GUARD</div><span className="ag-panel-meta">REAL-TIME</span></div><div className="ag-wide-grid"><div><p className="ag-chart-label">VULNERABILITY TIMELINE</p><div className="ag-bars">{barHeights.map((h, i) => <div key={i} className="ag-bar" style={{ height: `${h}%`, background: barColors[i % barColors.length], color: barColors[i % barColors.length], animationDelay: `${i * -.18}s` }} />)}</div></div><div><p className="ag-chart-label">FIREWALL RULES STATUS</p><MiniMap dotColor="#c49aff" lineColor="#c49aff88" /></div></div><div className="ag-guard-tags">{guardConnections.join('  ·  ')}</div></GlassPanel>
            <GlassPanel className="ag-wide ag-history"><div className="ag-panel-head"><div className="ag-panel-title"><b>⌁</b> SCAN HISTORY</div><span className="ag-panel-meta">RECENT ACTIVITY</span></div><table className="ag-table"><thead><tr><th>DOMAIN</th><th>STATUS</th><th>CVE</th><th>AGE</th></tr></thead><tbody>{historyRows.map(r => <tr key={r.domain}><td>{r.domain}</td><td><StatusBadge status={r.status} /></td><td>{r.cve}</td><td>{r.age}d</td></tr>)}</tbody></table></GlassPanel>
          </div>
        </section>
      </main>
    </>
  );
}
