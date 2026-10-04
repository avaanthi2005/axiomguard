// AXIOM//GUARD — Background Service Worker
// Fires every time a new page loads
// Sends URL to your FastAPI backend for analysis

const API_URL = "https://axiomguard.onrender.com/api/guard/analyze";

// Skip these URLs — no need to analyze them
const SKIP_URLS = [
  "chrome://", "chrome-extension://", "about:", "data:",
  "localhost", "127.0.0.1", "file://", "axiomguard-brown.vercel.app", "axiomguard.onrender.com"
];

function shouldSkip(url) {
  return SKIP_URLS.some(skip => url.startsWith(skip) || url.includes(skip));
}

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only fire when page finishes loading
  if (changeInfo.status !== "complete") return;
  if (!tab.url) return;
  if (shouldSkip(tab.url)) return;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url, source: "extension" })
    });

    if (!response.ok) return;

    const result = await response.json();

    // Save result to chrome storage (popup reads from here)
    await chrome.storage.local.set({
      [`result_${tabId}`]: {
        url: tab.url,
        verdict: result.verdict,
        guard_score: result.guard_score,
        color: result.color,
        action: result.action,
        domain: result.domain,
        timestamp: new Date().toISOString()
      }
    });

    // Send result to content script to show UI on page
    await chrome.tabs.sendMessage(tabId, {
      type: "GUARD_RESULT",
      data: result
    });

    // Update extension icon badge
    const badgeColors = {
      "TRUSTED": "#10b981",
      "CAUTION": "#f59e0b",
      "WARNING": "#f97316",
      "DANGER":  "#ef4444"
    };

    chrome.action.setBadgeText({
      text: String(Math.round(result.guard_score)),
      tabId: tabId
    });

    chrome.action.setBadgeBackgroundColor({
      color: badgeColors[result.verdict] || "#64748b",
      tabId: tabId
    });

  } catch (err) {
    // Backend not running — fail silently
    console.log("AXIOM//GUARD: Backend not reachable", err.message);
  }
});