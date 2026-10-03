// AXIOM//GUARD — Content Script
// Injects warning UI directly into the visited webpage

// Listen for verdict from background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "GUARD_RESULT") return;

  const result = message.data;
  const verdict = result.verdict;

  // Remove any existing AXIOMGUARD UI
  const existing = document.getElementById("axiomguard-overlay");
  if (existing) existing.remove();

  // Only show UI for CAUTION, WARNING, DANGER
  if (verdict === "TRUSTED") return;

  // Build the UI based on verdict
  if (verdict === "CAUTION") {
    showBanner(result);
  } else if (verdict === "WARNING") {
    showPopup(result);
  } else if (verdict === "DANGER") {
    showOverlay(result);
  }
});

// CAUTION — small yellow banner at top of page
function showBanner(result) {
  const banner = document.createElement("div");
  banner.id = "axiomguard-overlay";
  banner.style.cssText = `
    position: fixed; top: 0; left: 0; right: 0; z-index: 999999;
    background: #f59e0b; color: #0a0e1a;
    padding: 10px 20px; font-family: 'Segoe UI', sans-serif;
    font-size: 13px; font-weight: 600;
    display: flex; align-items: center; justify-content: space-between;
  `;
  banner.innerHTML = `
    <span>⚠️ AXIOM//GUARD: CAUTION — Minor concerns detected on this site (Score: ${result.guard_score}/100)</span>
    <button id="axiomguard-close-btn"
      style="background:none;border:none;cursor:pointer;font-size:16px;color:#0a0e1a;font-weight:bold;">✕</button>
  `;
  document.body.prepend(banner);
  banner.querySelector('#axiomguard-close-btn').addEventListener('click', () => banner.remove());
}

// WARNING — orange popup on right side
function showPopup(result) {
  const popup = document.createElement("div");
  popup.id = "axiomguard-overlay";
  popup.style.cssText = `
    position: fixed; bottom: 20px; right: 20px; z-index: 999999;
    background: #1a2235; border: 2px solid #f97316;
    border-radius: 12px; padding: 20px; width: 320px;
    font-family: 'Segoe UI', sans-serif; color: #ffffff;
    box-shadow: 0 8px 30px #f9731644;
  `;

  const signals = [
    ...(result.static_analysis?.signals || []),
    ...(result.behavior_analysis?.signals || [])
  ].slice(0, 3);

  const signalsHTML = signals.map(s =>
    `<div style="font-size:11px;color:#94a3b8;margin-top:4px;">⚠ ${s.description}</div>`
  ).join('');

  popup.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <span style="color:#f97316;font-weight:800;font-size:14px;letter-spacing:2px;">⚔ AXIOM//GUARD</span>
      <button id="axiomguard-close-btn"
        style="background:none;border:none;cursor:pointer;color:#64748b;font-size:16px;">✕</button>
    </div>
    <div style="font-size:22px;font-weight:900;color:#f97316;letter-spacing:2px;">WARNING</div>
    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">Guard Score: ${result.guard_score}/100</div>
    <div style="font-size:12px;color:#ffffff;margin-top:8px;">${result.action}</div>
    ${signalsHTML}
    <div style="margin-top:12px;display:flex;gap:8px;">
      <button id="axiomguard-report-btn"
        style="flex:1;background:#f97316;color:#0a0e1a;border:none;border-radius:6px;padding:8px;font-weight:700;cursor:pointer;font-size:12px;">
        VIEW FULL REPORT
      </button>
      <button id="axiomguard-dismiss-btn"
        style="background:#1e3a5f;color:#94a3b8;border:none;border-radius:6px;padding:8px;cursor:pointer;font-size:12px;">
        DISMISS
      </button>
    </div>
  `;
  document.body.appendChild(popup);
  popup.querySelector('#axiomguard-close-btn').addEventListener('click', () => popup.remove());
  popup.querySelector('#axiomguard-report-btn').addEventListener('click', () => window.open('http://localhost:3000/guard', '_blank'));
  popup.querySelector('#axiomguard-dismiss-btn').addEventListener('click', () => popup.remove());
}

// DANGER — full red page overlay
function showOverlay(result) {
  const overlay = document.createElement("div");
  overlay.id = "axiomguard-overlay";
  overlay.style.cssText = `
    position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 999999;
    background: #0a0e1aee; display: flex; align-items: center; justify-content: center;
    font-family: 'Segoe UI', sans-serif;
  `;

  const signals = [
    ...(result.static_analysis?.signals || []),
    ...(result.behavior_analysis?.signals || [])
  ].slice(0, 4);

  const signalsHTML = signals.map(s =>
    `<div style="background:#ef444422;border:1px solid #ef4444;border-radius:6px;padding:8px 12px;margin-top:8px;font-size:12px;color:#ef4444;">
      ⚠ ${s.description}
    </div>`
  ).join('');

  overlay.innerHTML = `
    <div style="background:#111827;border:2px solid #ef4444;border-radius:16px;padding:40px;max-width:500px;width:90%;text-align:center;box-shadow:0 20px 60px #ef444444;">
      <div style="font-size:14px;font-weight:800;color:#ef4444;letter-spacing:3px;margin-bottom:12px;">⚔ AXIOM//GUARD</div>
      <div style="font-size:40px;font-weight:900;color:#ef4444;letter-spacing:3px;">DANGER</div>
      <div style="font-size:14px;color:#94a3b8;margin:8px 0;">Guard Score: ${result.guard_score}/100 — ${result.domain}</div>
      <div style="font-size:14px;color:#ffffff;margin:16px 0;">${result.action}</div>
      <div style="text-align:left;">${signalsHTML}</div>
      <div style="margin-top:24px;display:flex;gap:12px;justify-content:center;">
        <button id="axiomguard-report-btn"
          style="background:#ef4444;color:#ffffff;border:none;border-radius:8px;padding:12px 24px;font-weight:700;cursor:pointer;font-size:13px;letter-spacing:1px;">
          VIEW FULL REPORT
        </button>
        <button id="axiomguard-dismiss-btn"
          style="background:#1e3a5f;color:#94a3b8;border:none;border-radius:8px;padding:12px 24px;cursor:pointer;font-size:12px;">
          I understand — proceed anyway
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.querySelector('#axiomguard-report-btn').addEventListener('click', () => window.open('http://localhost:3000/guard', '_blank'));
  overlay.querySelector('#axiomguard-dismiss-btn').addEventListener('click', () => overlay.remove());
}