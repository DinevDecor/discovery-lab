// Bulgarian-first DISPLAY layer for Machine Console.
//
// This file never changes canonical data. It reads one derived static cache
// and replaces only exact source text that has a matching translation.
// Missing/stale translations fall back to the original source text.
// The BG/EN control always makes the original available.

(() => {
  "use strict";

  const CACHE_URL = "translations-bg.json";
  const ORIGINAL = new WeakMap();
  let translations = new Map();
  let applying = false;
  let language = localStorage.getItem("machine-console-language") === "en" ? "en" : "bg";

  const STATUS_BG = new Map([
    ["WATCH", "WATCH · НАБЛЮДЕНИЕ"],
    ["ADVANCE", "ADVANCE · ПРОДЪЛЖАВА"],
    ["REJECT", "REJECT · ОТХВЪРЛЕНО"],
    ["OPEN", "OPEN · ОТВОРЕН"],
    ["RESOLVED", "RESOLVED · РЕШЕН"],
    ["INSUFFICIENT_DATA", "INSUFFICIENT_DATA · НЕДОСТАТЪЧНИ ДАННИ"],
    ["SUPPORTED_BY_SOURCE", "SUPPORTED_BY_SOURCE · ПОДКРЕПЕНО ОТ ИЗТОЧНИКА"],
    ["CHALLENGED_BY_SOURCE", "CHALLENGED_BY_SOURCE · ОСПОРЕНО ОТ ИЗТОЧНИКА"],
    ["SCHEMA_AMBIGUITY", "SCHEMA_AMBIGUITY · НЕЯСНОТА В СХЕМАТА"],
  ]);

  function translatedCore(core) {
    if (translations.has(core)) return translations.get(core);
    if (STATUS_BG.has(core)) return STATUS_BG.get(core);

    // Source quotes are rendered with typographic quote marks around the
    // canonical text. Translate the exact inner source while preserving the
    // visible quote marks.
    const quoted = core.match(/^([“‘\"'])(.*)([”’\"'])$/s);
    if (quoted && translations.has(quoted[2])) {
      return `${quoted[1]}${translations.get(quoted[2])}${quoted[3]}`;
    }
    return core;
  }

  function translateTextNode(node) {
    if (!ORIGINAL.has(node)) ORIGINAL.set(node, node.nodeValue || "");
    const source = ORIGINAL.get(node);
    if (language === "en") {
      if (node.nodeValue !== source) node.nodeValue = source;
      return;
    }

    const match = source.match(/^(\s*)([\s\S]*?)(\s*)$/);
    if (!match) return;
    const core = match[2];
    if (!core) return;
    const bg = translatedCore(core);
    const next = `${match[1]}${bg}${match[3]}`;
    if (node.nodeValue !== next) node.nodeValue = next;
  }

  function applyTranslations(root = document.body) {
    if (!root || applying) return;
    applying = true;
    try {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
          return node.nodeValue && node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
        },
      });
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(translateTextNode);
      document.documentElement.lang = language === "bg" ? "bg" : "en";
      updateToggle();
    } finally {
      applying = false;
    }
  }

  function updateToggle() {
    const button = document.getElementById("language-toggle");
    if (!button) return;
    button.textContent = language === "bg" ? "BG · EN" : "EN · BG";
    button.setAttribute("aria-label", language === "bg" ? "Покажи оригинала на английски" : "Покажи българския превод");
    button.title = language === "bg" ? "Покажи оригинала" : "Покажи български";
  }

  function installToggle() {
    if (document.getElementById("language-toggle")) return;
    const button = document.createElement("button");
    button.id = "language-toggle";
    button.type = "button";
    button.addEventListener("click", () => {
      language = language === "bg" ? "en" : "bg";
      localStorage.setItem("machine-console-language", language);
      applyTranslations(document.body);
    });
    Object.assign(button.style, {
      position: "fixed",
      top: "calc(env(safe-area-inset-top, 0px) + 10px)",
      right: "12px",
      zIndex: "9999",
      border: "1px solid rgba(70,84,110,.28)",
      borderRadius: "999px",
      background: "rgba(255,255,255,.94)",
      color: "#33456B",
      padding: "7px 10px",
      font: "600 11px/1 'IBM Plex Mono', monospace",
      letterSpacing: ".05em",
      boxShadow: "0 2px 10px rgba(35,45,65,.10)",
      WebkitBackdropFilter: "blur(8px)",
      backdropFilter: "blur(8px)",
    });
    document.body.appendChild(button);
    updateToggle();
  }

  async function loadTranslations() {
    try {
      const response = await fetch(CACHE_URL, { cache: "no-cache" });
      if (!response.ok) return;
      const data = await response.json();
      const next = new Map();
      Object.values(data.entries || {}).forEach((entry) => {
        if (!entry || typeof entry.source !== "string" || typeof entry.bg !== "string") return;
        if (!entry.source || !entry.bg) return;
        next.set(entry.source, entry.bg);
      });
      translations = next;
    } catch (_) {
      // Translation is optional display data. English source remains usable.
    }
  }

  function observeRenders() {
    const observer = new MutationObserver(() => applyTranslations(document.body));
    observer.observe(document.body, { childList: true, subtree: true });
  }

  async function boot() {
    installToggle();
    observeRenders();
    await loadTranslations();
    applyTranslations(document.body);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
