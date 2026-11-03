const EDITOR_PATH = "editor/index.html";

async function openEditor(query = "") {
  const url = chrome.runtime.getURL(EDITOR_PATH) + query;
  await chrome.tabs.create({ url });
}

chrome.action.onClicked.addListener(() => {
  openEditor().catch(console.error);
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "open-editor") {
    openEditor(msg.query || "")
      .then(() => sendResponse({ ok: true }))
      .catch((e) => sendResponse({ ok: false, error: String(e) }));
    return true;
  }
});
