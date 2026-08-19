(() => {
  "use strict";

  let radar = null;
  const baseRenderHome = renderHome;

  function escLocal(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }

  function radarBlock() {
    if (!radar) {
      return `
        <div class="section-label">Project Tool Radar</div>
        <div class="card"><div class="loading" style="min-height:0;padding:18px 0">TOOL RADAR…</div></div>
      `;
    }
    const top = (radar.signals || []).slice(0, 3);
    return `
      <div class="section-label">Project Tool Radar (${radar.count || 0})</div>
      <div class="list">
        ${top.map((r) => `
          <a class="row" href="tools.html">
            <div class="row-head"><span class="row-id">${escLocal(r.product)}</span><span class="pill">${escLocal(r.use_type)}</span></div>
          </a>
        `).join("")}
        <a class="row" href="tools.html"><div class="row-title">ALL TOOL SIGNALS →</div></a>
      </div>
    `;
  }

  renderHome = function patchedRenderHome() {
    return baseRenderHome() + radarBlock();
  };

  fetch("tool-radar.json", { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
    .then((payload) => {
      radar = payload;
      if (typeof DATA !== "undefined" && DATA && currentRoute() === "home") render();
    })
    .catch(() => {
      radar = { count: 0, signals: [] };
      if (typeof DATA !== "undefined" && DATA && currentRoute() === "home") render();
    });
})();
