import React, { useEffect, useMemo, useState } from 'react';
import api from '../api/client';

function VerdictBadge({ verdict }) {
  const tone = verdictColor(verdict);
  return <span className={`agh-verdict agh-verdict-${tone}`}>{verdict || 'UNKNOWN'}</span>;
}

function verdictColor(verdict) {
  if (!verdict) return 'gray';
  const value = verdict.toUpperCase();
  if (value === 'CRITICAL' || value === 'DANGER' || value === 'DANGEROUS') return 'red';
  if (value === 'HIGH' || value === 'WARNING') return 'orange';
  if (value === 'MEDIUM' || value === 'CAUTION' || value === 'SUSPICIOUS') return 'yellow';
  return 'green';
}

function ModuleIcon({ module }) {
  const value = String(module || '').toUpperCase();
  if (value.includes('PHISH')) return <span className="agh-module-icon agh-green">◉</span>;
  if (value.includes('GUARD')) return <span className="agh-module-icon agh-purple">◇</span>;
  return <span className="agh-module-icon agh-cyan">⌁</span>;
}

function formatDate(value) {
  if (!value) return 'Unknown time';
  return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
}

function getScore(history) {
  const scores = history.map(item => Number(item.score)).filter(Number.isFinite);
  if (!scores.length) return '—';
  return (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1);
}

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [actionError, setActionError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  const fetchHistory = () => {
    setLoading(true);
    setActionError('');
    api.get('/api/history')
      .then(res => setHistory(res.data.history || []))
      .catch(() => setActionError('Unable to load history. Make sure the backend is running.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchHistory(); }, []);

  const filteredHistory = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return history.filter(item => {
      const matchesQuery = !normalizedQuery || [item.target, item.module, item.verdict].some(value => String(value || '').toLowerCase().includes(normalizedQuery));
      const matchesFilter = filter === 'ALL' || verdictColor(item.verdict).toUpperCase() === filter;
      return matchesQuery && matchesFilter;
    });
  }, [history, query, filter]);

  const dangerousCount = history.filter(item => ['red', 'orange'].includes(verdictColor(item.verdict))).length;
  const cleanCount = history.filter(item => verdictColor(item.verdict) === 'green').length;
  const moduleCount = new Set(history.map(item => item.module).filter(Boolean)).size;

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this history entry?')) return;
    setDeletingId(id);
    setActionError('');
    try {
      await api.delete(`/api/history/${id}`);
      setHistory(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      setActionError('Failed to delete entry. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Clear ALL scan history? This cannot be undone.')) return;
    setActionError('');
    try {
      await api.delete('/api/history');
      setHistory([]);
    } catch (err) {
      setActionError('Failed to clear history. Please try again.');
    }
  };

  return (
    <>
      <style>{`
        .agh-page{--agh-text:#f5f9ff;--agh-muted:#8ea3c2;--agh-cyan:#27d9ef;position:relative;width:min(1240px,calc(100% - 42px));margin:0 auto;padding:42px 0 80px;color:var(--agh-text);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}.agh-page,.agh-page *{box-sizing:border-box}.agh-page::before{content:'';position:fixed;z-index:-2;inset:0;pointer-events:none;background:radial-gradient(circle at 8% 12%,rgba(0,116,255,.2),transparent 27rem),radial-gradient(circle at 88% 56%,rgba(30,217,239,.11),transparent 27rem),linear-gradient(135deg,#02050d,#07152b 54%,#02050e)}.agh-page::after{content:'';position:fixed;z-index:-1;inset:0;pointer-events:none;opacity:.12;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 75%)}
        .agh-head{display:flex;align-items:flex-end;justify-content:space-between;gap:25px;margin-bottom:30px}.agh-overline{margin:0 0 12px;color:#62e6f7;font-size:11px;font-weight:800;letter-spacing:2.8px;text-transform:uppercase}.agh-title{margin:0;font-size:clamp(42px,6vw,70px);line-height:.96;letter-spacing:-4px}.agh-title em{color:var(--agh-cyan);font-style:normal;text-shadow:0 0 25px rgba(39,217,239,.3)}.agh-intro{max-width:420px;margin:0;color:var(--agh-muted);font-size:14px;line-height:1.8;text-align:right}.agh-sync{display:inline-flex;align-items:center;gap:8px;padding:9px 13px;margin-bottom:15px;color:#96b4d1;border:1px solid rgba(139,204,255,.21);border-radius:999px;background:rgba(30,71,112,.23);font-size:10px}.agh-sync-dot{width:7px;height:7px;border-radius:50%;background:#42e0aa;box-shadow:0 0 13px #42e0aa}
        .agh-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}.agh-stat{position:relative;padding:20px 21px;overflow:hidden;border:1px solid rgba(136,198,249,.2);border-radius:20px;background:linear-gradient(140deg,rgba(20,51,88,.55),rgba(5,17,37,.64));box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 15px 35px rgba(0,0,0,.17);backdrop-filter:blur(18px)}.agh-stat::after{content:'';position:absolute;right:-35px;bottom:-52px;width:115px;height:115px;border-radius:50%;background:var(--agh-stat-glow);filter:blur(25px);opacity:.45}.agh-stat-label{display:block;color:#6f89a9;font-size:9px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase}.agh-stat-value{display:block;margin-top:9px;color:#e9f6ff;font-size:27px;font-weight:800;letter-spacing:-1px}.agh-stat-note{display:block;margin-top:5px;color:#7690ae;font-size:10px}.agh-cyan-stat{--agh-stat-glow:#16cce9}.agh-red-stat{--agh-stat-glow:#ff557e}.agh-green-stat{--agh-stat-glow:#36dfa8}.agh-purple-stat{--agh-stat-glow:#a875ff}
        .agh-shell{position:relative;padding:24px;overflow:hidden;border:1px solid rgba(133,199,255,.25);border-radius:29px;background:linear-gradient(135deg,rgba(13,39,73,.63),rgba(4,14,31,.76));box-shadow:0 26px 80px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.14);backdrop-filter:blur(25px)}.agh-shell-top{display:flex;align-items:center;justify-content:space-between;gap:17px;margin-bottom:21px}.agh-shell-title{display:flex;align-items:center;gap:11px}.agh-shell-title-icon{display:grid;place-items:center;width:38px;height:38px;color:#6fe8f6;border:1px solid rgba(93,221,255,.32);border-radius:12px;background:rgba(20,148,255,.14);box-shadow:0 0 20px rgba(22,183,255,.18)}.agh-shell-title h2{margin:0 0 4px;font-size:17px;letter-spacing:-.5px}.agh-shell-title p{margin:0;color:#7089a8;font-size:10px}.agh-clear{padding:10px 13px;color:#ff8ba2;font:inherit;font-size:10px;font-weight:800;letter-spacing:.8px;border:1px solid rgba(255,91,125,.32);border-radius:10px;background:rgba(125,20,49,.17);cursor:pointer;transition:.2s}.agh-clear:hover{background:rgba(184,29,65,.28);box-shadow:0 0 20px rgba(255,65,105,.15)}
        .agh-controls{display:flex;gap:10px;margin-bottom:20px}.agh-search-wrap{position:relative;flex:1}.agh-search-icon{position:absolute;left:15px;top:50%;color:#75a0c6;transform:translateY(-50%)}.agh-search{width:100%;height:47px;padding:0 15px 0 42px;color:#e9f8ff;font:inherit;font-size:12px;outline:none;border:1px solid rgba(132,192,243,.2);border-radius:12px;background:rgba(2,12,28,.55);transition:.2s}.agh-search::placeholder{color:#68809f}.agh-search:focus{border-color:#32d4ed;box-shadow:0 0 0 4px rgba(34,209,235,.1)}.agh-filter{height:47px;padding:0 13px;color:#9ab3d0;font:inherit;font-size:11px;border:1px solid rgba(132,192,243,.2);border-radius:12px;background:rgba(2,12,28,.55);outline:none}.agh-filter option{color:#07152a;background:#d9e8f5}
        .agh-table-wrap{overflow-x:auto;border:1px solid rgba(129,185,233,.14);border-radius:17px;background:rgba(2,12,27,.34)}.agh-table{width:100%;min-width:720px;border-collapse:collapse;font-size:12px}.agh-table th{padding:15px 16px;color:#6482a3;font-size:9px;font-weight:800;letter-spacing:1.3px;text-align:left;background:rgba(17,46,78,.37)}.agh-table td{padding:15px 16px;border-top:1px solid rgba(131,183,232,.09);color:#b2c5dc}.agh-table tr{transition:.2s}.agh-table tbody tr:hover{background:rgba(37,148,221,.08)}.agh-index{color:#5b83aa;font-weight:800}.agh-target{max-width:290px;color:#e0efff!important;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.agh-time{color:#8399b5!important;font-size:11px}.agh-verdict{display:inline-flex;padding:6px 8px;border-radius:7px;font-size:9px;font-weight:800;letter-spacing:.7px}.agh-verdict-red{color:#ff91a8;background:rgba(255,64,108,.14)}.agh-verdict-orange{color:#ffd08a;background:rgba(255,168,60,.14)}.agh-verdict-yellow{color:#ffe89a;background:rgba(252,210,60,.14)}.agh-verdict-green{color:#72edbd;background:rgba(42,220,151,.13)}.agh-verdict-gray{color:#b0bdd0;background:rgba(140,159,184,.14)}.agh-delete{padding:6px;color:#637b99;font:inherit;font-size:14px;border:0;border-radius:8px;background:transparent;cursor:pointer;transition:.2s}.agh-delete:hover{color:#ff7897;background:rgba(255,68,108,.12)}.agh-delete:disabled{cursor:wait;opacity:.45}.agh-empty{display:grid;place-items:center;padding:75px 20px;text-align:center}.agh-empty-orb{display:grid;place-items:center;width:68px;height:68px;margin-bottom:17px;color:#61deef;border:1px solid rgba(87,221,255,.4);border-radius:50%;background:rgba(28,159,234,.12);box-shadow:0 0 35px rgba(35,190,255,.23);font-size:27px;animation:agh-pulse 3s ease-in-out infinite}.agh-empty h3{margin:0 0 8px;font-size:17px}.agh-empty p{margin:0;color:#7890ad;font-size:12px}.agh-error{margin-bottom:18px;padding:12px 14px;color:#ff9daf;border:1px solid rgba(255,96,130,.24);border-radius:11px;background:rgba(124,23,51,.18);font-size:12px}.agh-loading{display:grid;place-items:center;padding:75px 20px;color:#83b8db;font-size:12px}.agh-spinner{width:27px;height:27px;margin-bottom:12px;border:2px solid rgba(85,202,244,.2);border-top-color:#50ddf2;border-radius:50%;animation:agh-spin 1s linear infinite}.agh-results-note{margin-top:14px;color:#607b9b;font-size:10px;text-align:right}.agh-module-icon{display:inline-grid;place-items:center;width:29px;height:29px;border:1px solid currentColor;border-radius:9px;background:rgba(48,161,238,.12);font-size:13px}.agh-cyan{color:#5be1f0}.agh-green{color:#5be3ae}.agh-purple{color:#c29dff}
        @keyframes agh-spin{to{transform:rotate(360deg)}}@keyframes agh-pulse{0%,100%{transform:scale(1);opacity:.8}50%{transform:scale(1.08);opacity:1}}
        @media(max-width:800px){.agh-head{align-items:flex-start;flex-direction:column}.agh-intro{text-align:left}.agh-summary{grid-template-columns:1fr 1fr}.agh-shell{padding:16px}.agh-controls{flex-direction:column}.agh-filter{width:100%}}@media(max-width:480px){.agh-page{width:calc(100% - 24px);padding-top:24px}.agh-title{font-size:47px;letter-spacing:-3px}.agh-summary{gap:9px}.agh-stat{padding:16px 13px}.agh-stat-value{font-size:22px}.agh-shell-top{align-items:flex-start}.agh-clear{font-size:9px}.agh-table th,.agh-table td{padding:13px 11px}}
      `}</style>

      <main className="agh-page">
        <header className="agh-head"><div><div className="agh-sync"><span className="agh-sync-dot" /> Secure archive / synchronized</div><p className="agh-overline">Forensic activity archive</p><h1 className="agh-title">Your security<br /><em>timeline.</em></h1></div><p className="agh-intro">Every scan, verdict, and signal in one secure view. Search past investigations, review risk patterns, and keep your security decisions close at hand.</p></header>

        <section className="agh-summary"><div className="agh-stat agh-cyan-stat"><span className="agh-stat-label">Total investigations</span><strong className="agh-stat-value">{history.length}</strong><span className="agh-stat-note">All recorded activity</span></div><div className="agh-stat agh-red-stat"><span className="agh-stat-label">Needs attention</span><strong className="agh-stat-value">{dangerousCount}</strong><span className="agh-stat-note">High-risk findings</span></div><div className="agh-stat agh-green-stat"><span className="agh-stat-label">Clear verdicts</span><strong className="agh-stat-value">{cleanCount}</strong><span className="agh-stat-note">No immediate threat</span></div><div className="agh-stat agh-purple-stat"><span className="agh-stat-label">Average score</span><strong className="agh-stat-value">{getScore(history)}</strong><span className="agh-stat-note">Across scored scans</span></div></section>

        <section className="agh-shell">
          <div className="agh-shell-top"><div className="agh-shell-title"><span className="agh-shell-title-icon">⌁</span><div><h2>Investigation history</h2><p>{moduleCount || 0} active modules · encrypted local archive</p></div></div>{!loading && history.length > 0 && <button className="agh-clear" onClick={handleClearAll}>CLEAR ARCHIVE</button>}</div>
          {actionError && <div className="agh-error">{actionError}</div>}
          {!loading && history.length > 0 && <div className="agh-controls"><div className="agh-search-wrap"><span className="agh-search-icon">⌕</span><input className="agh-search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search target, module, or verdict..." /></div><select className="agh-filter" value={filter} onChange={e => setFilter(e.target.value)}><option value="ALL">All verdicts</option><option value="GREEN">Clear</option><option value="YELLOW">Caution</option><option value="ORANGE">Warning</option><option value="RED">Critical</option></select></div>}

          {loading && <div className="agh-loading"><span className="agh-spinner" />Loading secure history...</div>}
          {!loading && history.length === 0 && <div className="agh-empty"><div className="agh-empty-orb">⌁</div><h3>Your timeline is clear.</h3><p>Run a scan to create your first security record.</p></div>}
          {!loading && history.length > 0 && filteredHistory.length === 0 && <div className="agh-empty"><div className="agh-empty-orb">⌕</div><h3>No matching investigations.</h3><p>Try a different search term or verdict filter.</p></div>}
          {!loading && filteredHistory.length > 0 && <><div className="agh-table-wrap"><table className="agh-table"><thead><tr><th>#</th><th>MODULE</th><th>TARGET</th><th>VERDICT</th><th>SCORE</th><th>TIME</th><th /></tr></thead><tbody>{filteredHistory.map((item, i) => <tr key={item.id}><td className="agh-index">{item.id || i + 1}</td><td><ModuleIcon module={item.module} /></td><td className="agh-target" title={item.target}>{item.target}</td><td><VerdictBadge verdict={item.verdict} /></td><td>{Number.isFinite(Number(item.score)) ? Number(item.score).toFixed(1) : 'N/A'}</td><td className="agh-time">{formatDate(item.created_at)}</td><td><button className="agh-delete" onClick={() => handleDelete(item.id)} disabled={deletingId === item.id} title="Delete entry">{deletingId === item.id ? '…' : '×'}</button></td></tr>)}</tbody></table></div><p className="agh-results-note">Showing {filteredHistory.length} of {history.length} investigations</p></>}
        </section>
      </main>
    </>
  );
}
