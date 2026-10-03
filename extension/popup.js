// Reads the stored result for the current tab and displays it

document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('open-axiomguard-btn')
    .addEventListener('click', () => window.open('http://localhost:3000', '_blank'));

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  const stored = await chrome.storage.local.get(`result_${tab.id}`);
  const result = stored[`result_${tab.id}`];

  const content = document.getElementById('content');

  if (!result) {
    content.innerHTML = `
      <div class="no-result">
        <div style="font-size:24px;margin-bottom:8px;">🔍</div>
        No analysis yet for this page.<br>
        <span style="font-size:10px;">Navigate to a website to trigger AXIOM//GUARD analysis.</span>
      </div>
    `;
    return;
  }

  const colorMap = {
    'TRUSTED': 'green',
    'CAUTION': 'yellow',
    'WARNING': 'orange',
    'DANGER':  'red'
  };

  const color = colorMap[result.verdict] || 'green';

  content.innerHTML = `
    <div class="verdict-box">
      <div class="verdict-text ${color}">${result.verdict}</div>
      <div class="score-text">Guard Score: ${result.guard_score} / 100</div>
      <div class="domain-text">${result.domain}</div>
      <div class="action-text">${result.action}</div>
    </div>
    <div style="font-size:10px;color:#64748b;text-align:center;">
      Last analyzed: ${new Date(result.timestamp).toLocaleTimeString()}
    </div>
  `;
});