(function () {
  var STORAGE_KEY = "simplephoto-tutorials-lang";
  var PREFS_KEY = "photocraft.preferences";
  var SUPPORTED = ["en", "ja", "zh-hans", "zh-hant", "fr", "ko", "de"];
  var SET = {};
  SUPPORTED.forEach(function (c) { SET[c] = true; });

  function candidates(tag) {
    if (!tag) return [];
    var base = String(tag).split(/[.@]/)[0].replace(/_/g, "-").toLowerCase();
    if (base === "c" || base === "posix") return ["en"];
    var parts = base.split("-").filter(Boolean);
    if (!parts.length) return [];
    var primary = parts[0];
    var out = [];
    for (var n = parts.length; n >= 1; n--) out.push(parts.slice(0, n).join("-"));
    if (primary === "zh" && parts.indexOf("hans") < 0 && parts.indexOf("hant") < 0) {
      var script = (parts.indexOf("tw") >= 0 || parts.indexOf("hk") >= 0 || parts.indexOf("mo") >= 0) ? "zh-hant" : "zh-hans";
      out.splice(out.length - 1, 0, script);
    }
    if (primary === "pt" && out.indexOf("pt-br") < 0) out.splice(out.length - 1, 0, "pt-br");
    if (primary === "sr" && out.indexOf("sr-latn") < 0) out.splice(out.length - 1, 0, "sr-latn");
    if ((primary === "no" || primary === "nn") && out.indexOf("nb") < 0) out.splice(out.length - 1, 0, "nb");
    return out;
  }

  function mapTag(tag) {
    var list = candidates(tag);
    for (var i = 0; i < list.length; i++) {
      if (SET[list[i]]) return list[i];
    }
    return null;
  }

  function isSupported(code) {
    return !!(code && SET[String(code).toLowerCase()]);
  }

  function fromPrefs() {
    try {
      var raw = localStorage.getItem(PREFS_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      var lang = data && data.interface && data.interface.language;
      if (typeof lang === "string" && lang && lang.toLowerCase() !== "auto") return mapTag(lang);
    } catch (e) {}
    return null;
  }

  function fromNavigator() {
    var nav = navigator.languages && navigator.languages.length
      ? navigator.languages
      : [navigator.language || "en"];
    for (var i = 0; i < nav.length; i++) {
      var mapped = mapTag(nav[i]);
      if (mapped) return mapped;
    }
    return null;
  }

  function resolveLang() {
    var params = new URLSearchParams(window.location.search);
    var q = params.get("lang");
    if (q && q.toLowerCase() !== "auto") {
      var mapped = isSupported(q) ? q.toLowerCase() : mapTag(q);
      // Honor ?lang= from the editor; fall back to English when that locale has no tutorial.
      return mapped || "en";
    }
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (isSupported(saved)) return saved;
    } catch (e) {}
    return fromPrefs() || fromNavigator() || "en";
  }

  function persist(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  function currentFolderLang() {
    var parts = window.location.pathname.split("/").filter(Boolean);
    var i = parts.lastIndexOf("tutorials");
    if (i >= 0 && parts[i + 1] && SET[parts[i + 1]]) return parts[i + 1];
    return null;
  }

  function currentPage() {
    var file = window.location.pathname.split("/").pop() || "index.html";
    if (!file || file.indexOf(".html") < 0) return "index.html";
    return file;
  }

  var folder = currentFolderLang();
  var isTrampoline = document.body && document.body.classList.contains("trampoline");

  if (isTrampoline || !folder) {
    var lang = resolveLang();
    persist(lang);
    var target = lang + "/" + (isTrampoline ? "index.html" : currentPage());
    window.location.replace(target);
    return;
  }

  // On a per-language page: honor ?lang= if it names a different locale.
  var params = new URLSearchParams(window.location.search);
  var q = params.get("lang");
  if (q && q.toLowerCase() !== "auto") {
    var mapped = isSupported(q) ? q.toLowerCase() : mapTag(q);
    if (!mapped) mapped = "en";
    if (mapped !== folder) {
      persist(mapped);
      window.location.replace("../" + mapped + "/" + currentPage());
      return;
    }
  }
  persist(folder);

  var select = document.querySelector(".lang select");
  if (select) {
    select.value = folder;
    select.addEventListener("change", function () {
      var next = select.value;
      if (!isSupported(next) || next === folder) return;
      persist(next);
      window.location.href = "../" + next + "/" + currentPage();
    });
  }
})();
