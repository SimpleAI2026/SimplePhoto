// Open the PhotoCraft editor as an extension page (full tab).
const EDITOR_PATH = "editor/index.html";

async function openEditor(query = "") {
  const url = chrome.runtime.getURL(EDITOR_PATH) + query;
  await chrome.tabs.create({ url });
}

chrome.action.onClicked.addListener(() => {
  openEditor().catch((err) => console.error("openEditor failed", err));
});

chrome.runtime.onInstalled.addListener(() => {
  console.info("SimplePhoto installed; click the action icon to open the editor.");
});
