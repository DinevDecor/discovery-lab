(() => {
  "use strict";

  const screen = document.getElementById("tool-screen");
  const title = document.getElementById("tool-title");
  const toggle = document.getElementById("tool-language-toggle");
  let language = localStorage.getItem("machine-console-language") === "en" ? "en" : "bg";
  let data = { count: 0, signals: [] };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const fmtDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleDateString(language === "bg" ? "bg-BG" : "en-US", { year: "numeric", month: "short", day: "numeric" });
  };
  const t = (en, bg) => language === "bg" ? bg : en;
  const field = (row, name) => row[`${name}_${language}`] || row[`${name}_en`] || "—";

  function card(row) {
    const source = row.source_url
      ? `<a href="${esc(row.source_url)}" target="_blank" rel="noopener">${esc(t("source", "източник"))} ↗</a>`
      : `<span>${esc(t("source email", "изходен имейл"))}: ${esc(fmtDate(row.source_email_ts))}</span>`;
    return `
      <div class="card" style="margin-bottom:14px">
        <div class="row-head">
          <span class="row-id">${esc(row.product)}</span>
          <span class="pill">${esc(row.use_type)}</span>
        </div>
        <div class="fact-grid" style="margin-top:12px">
          <div class="fact"><dt>${esc(t("Project fit", "Подходящ проект"))}</dt><dd>${esc(field(row, "project_fit"))}</dd></div>
          <div class="fact"><dt>${esc(t("Build vs buy", "Build vs buy"))}</dt><dd class="muted">${esc(field(row, "build_vs_buy"))}</dd></div>
          <div class="fact"><dt>${esc(t("Why it matters", "Защо има значение"))}</dt><dd class="muted">${esc(field(row, "why_it_matters"))}</dd></div>
          <div class="fact"><dt>${esc(t("Cheapest test", "Най-евтин тест"))}</dt><dd class="muted">${esc(field(row, "cheapest_test"))}</dd></div>
          <div class="fact"><dt>${esc(t("Risk / overlap", "Риск / припокриване"))}</dt><dd class="muted">${esc(field(row, "risk_overlap"))}</dd></div>
          <div class="fact"><dt>${esc(t("Verdict", "Вердикт"))}</dt><dd><b>${esc(field(row, "verdict"))}</b></dd></div>
          <div class="fact"><dt>${esc(t("Original Product Hunt description", "Оригинално описание от Product Hunt"))}</dt><dd class="muted">${esc(row.source_description || "—")}</dd></div>
        </div>
        <div class="evidence-strip">
          ${source}
          <span>${esc(row.source_subject || "")}</span>
          <span>${esc(row.signal_id)}</span>
        </div>
      </div>
    `;
  }

  function render() {
    document.documentElement.lang = language;
    title.textContent = t("Project Tool Radar", "Project Tool Radar");
    toggle.textContent = language === "bg" ? "BG · EN" : "EN · BG";
    if (!data.signals.length) {
      screen.innerHTML = `<div class="empty-state">${esc(t("No useful tool signals recorded yet.", "Все още няма записани полезни tool сигнали."))}</div>`;
      return;
    }
    screen.innerHTML = `
      <div class="section-label">${data.count} ${esc(t("recorded tool signals", "записани tool сигнала"))}</div>
      <div class="not-reached-card" style="margin-bottom:16px">
        <div class="nr-label">${esc(t("Read-only derived stream", "Read-only derived stream"))}</div>
        <p>${esc(t(
          "These are project-fit evaluations of external tools. They are not Business Candidate evidence and never change CA/BCA lifecycle state.",
          "Това са оценки доколко външни инструменти пасват на нашите проекти. Те не са доказателство за Business Candidate и никога не променят CA/BCA lifecycle state."
        ))}</p>
      </div>
      ${data.signals.map(card).join("")}
    `;
  }

  toggle.addEventListener("click", () => {
    language = language === "bg" ? "en" : "bg";
    localStorage.setItem("machine-console-language", language);
    render();
  });

  fetch("tool-radar.json", { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
    .then((payload) => { data = payload; render(); })
    .catch((err) => {
      screen.innerHTML = `<div class="empty-state">${esc(t("Could not load Tool Radar", "Tool Radar не можа да се зареди"))}: ${esc(err.message)}</div>`;
    });
})();
