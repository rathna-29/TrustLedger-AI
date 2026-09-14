"use strict";
const $ = (sel, root) => (root || document).querySelector(sel);
const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
const esc = (s) =>
  String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
const MONO = (s) => `<span class="mono">${esc(s)}</span>`;

const DECISION_ORDER = [
  { key: "EXECUTE", id: "kpiExec" },
  { key: "CONSTRAIN", id: "kpiConstrain" },
  { key: "ESCALATE", id: "kpiEscalate" },
  { key: "BLOCK", id: "kpiBlock" },
];
const DECISION_COLORS = {
  EXECUTE: "#3ddc97",
  CONSTRAIN: "#ffb454",
  ESCALATE: "#f66f7a",
  BLOCK: "#f0163f",
};
const RISK_COLOR = (n) => (n < 25 ? "#3ddc97" : n < 50 ? "#ffb454" : n < 75 ? "#f66f7a" : "#f0163f");

async function jfetch(url, opts) {
  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data && data.error) || res.statusText);
  return data;
}
async function jpost(url, body) {
  return jfetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
}

function showToast(msg, kind) {
  let t = $("#toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "toast";
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = "toast " + (kind || "info");
  clearTimeout(t._h);
  t._h = setTimeout(() => (t.className = "toast"), 2600);
}

/* ========================================================= */
/*  KPI overview                                             */
/* ========================================================= */
async function loadKs() {
  const d = await jfetch("/api/overview");
  const dist = d.decision_distribution || {};
  const total = DECISION_ORDER.reduce((a, k) => a + (dist[k.key] || 0), 0) || 1;

  DECISION_ORDER.forEach((it) => {
    const card = $("#" + it.id);
    if (!card) return;
    const num = card.querySelector(".kpi-num");
    const bar = card.querySelector(".kpi-track i");
    if (num) num.textContent = dist[it.key] || 0;
    if (bar) {
      bar.style.width = Math.round(((dist[it.key] || 0) / total) * 100) + "%";
      bar.style.background = it.color || DECISION_COLORS[it.key];
    }
  });

  const rate = Math.round((d.escalation_rate || 0) * 10) / 10;
  const rk = $("#kpiRate");
  if (rk) {
    const rn = rk.querySelector(".kpi-num");
    if (rn) {
      rn.textContent = rate + "%";
      rn.style.color = RISK_COLOR(rate * 5);
    }
    const rb = rk.querySelector(".kpi-track i");
    if (rb) {
      rb.style.width = Math.min(100, rate) + "%";
      rb.style.background = RISK_COLOR(rate * 5);
    }
  }

  const pill = $("#ledgerStatus");
  if (pill) {
    pill.textContent = d.ledger_integrity_ok ? "Ledger: verified" : "Ledger: TAMPERED";
    pill.className = "ledger-pill " + (d.ledger_integrity_ok ? "ok" : "bad");
  }

  const ts = $("#lastUpdated");
  if (ts) ts.textContent = new Date().toLocaleTimeString();
  return d;
}

/* ========================================================= */
/*  Scenario buttons + run                                   */
/* ========================================================= */
async function loadScenarios() {
  const d = await jfetch("/api/scenarios");
  const wrap = $("#scenarioButtons");
  if (!wrap) return;
  wrap.innerHTML = Object.keys(d || {})
    .map((k) => `<button type="button" class="scenario-chip" data-key="${esc(k)}">${esc((d[k] && d[k].short) || k)}</button>`)
    .join("");
  wrap.querySelectorAll(".scenario-chip").forEach((b) =>
    b.addEventListener("click", () => runScenario(b.dataset.key))
  );
}

async function runScenario(key) {
  const out = $("#scenarioResult");
  if (out) {
    out.className = "scenario-result pending";
    out.textContent = "Tracing through 15 modules...";
  }
  try {
    const d = await jfetch("/api/scenarios");
    const s = d[key];
    if (!s) throw new Error("unknown scenario: " + key);
    const r = await jpost("/agent/intent", {
      payload: s.payload,
      token: s.token,
    });
    renderResult(r([[esc(r.decision)]]));
    renderPipeline(r);
    refreshAll();
  } catch (err) {
    if (out) {
      out.className = "scenario-result error";
      out.textContent = "Scenario failed: " + err.message;
    }
  }
}

function renderResult(r) {
  const out = $("#scenarioResult");
  if (!out) return;
  out.className = "scenario-result show";
  out.innerHTML = `<div class="sr-decision" style="color:${DECISION_COLORS[r.decision] || "#fff"}">${esc(r.decision)}</div>
    <div class="sr-meta">risk ${Math.round(r.risk_score || 0)} · ${esc(r.reason || "")}</div>
    <pre class="sr-body">${esc(JSON.stringify(r.evidence || {}, null, 2))}</pre>`;
}

function renderPipeline(r) {
  const stages = (r.pipeline_stages || []).map(
    (s) => `<div class="stage-chip s-${esc(s.level || "ok")}">
      <span class="s-label">${esc(s.label || "")}</span>
      <span class="s-detail">${esc(s.detail || "")}</span>
    </div>`
  ).join("");
  const grid = $("#pipelineStages");
  if (grid) grid.innerHTML = stages || `<div class="stage-chip idle">No trace yet</div>`;

  const banner = $("#pipelineBiz");
  if (banner) {
    banner.className = "banner " + ((r.pipeline_stages || []).length ? "show" : "empty");
    banner.textContent = (r.pipeline_stages || []).length
      ? `${r.pipeline_stages.length} modules traced · ledger ${r.ledger_hash ? "sealed" : "pending"}`
      : "Run a scenario to trace the security loop through all 15 modules.";
  }
}

/* ========================================================= */
/*  Tables: transactions + agents                            */
/* ========================================================= */
async function loadTxns() {
  const rows = await jfetch("/api/transactions");
  const tb = $("#txnTable tbody");
  if (!tb) return;
  tb.innerHTML = (rows || [])
    .slice(0, 30)
    .map((r) => `<tr>
        <td class="mono">${esc(r.txn_id || "-")}</td>
        <td>${esc(r.agent_id || "-")}</td>
        <td class="mono">${money(r.amount_sats)}</td>
        <td class="mono">${esc(r.counterparty || "-")}</td>
        <td><span class="risk-cell" style="color:${RISK_COLOR(r.risk_score)}">${Math.round(r.risk_score || 0)}</span></td>
        <td><span class="dec-cell" style="color:${DECISION_COLORS[r.decision] || "#aaa"}">${esc(r.decision || "-")}</span></td>
      </tr>`)
    .join("");
}

function money(sat) {
  return ((Number(sat) || 0) / 1e8).toFixed(2);
}

async function loadAgents() {
  const rows = await jfetch("/api/agents");
  const tb = $("#agentTable tbody");
  if (!tb) return;
  tb.innerHTML = (rows || [])
    .map((a) => `<tr>
        <td class="mono">${esc(a.agent_id || "-")}</td>
        <td>${esc(a.role || "-")}</td>
        <td class="mono">${esc(a.baseline || "-")}</td>
        <td class="mono">${money(a.today_spent)}</td>
        <td>${a.txn_count || 0}</td>
      </tr>`)
    .join("");
}

/* ========================================================= */
/*  Review queue + blocked                                   */
/* ========================================================= */
async function loadReview() {
  const rows = await jfetch("/api/review-queue");
  const cnt = $("#reviewCount");
  if (cnt) cnt.textContent = (rows || []).length + " pending";
  const list = $("#reviewList");
  if (!list) return;
  list.innerHTML = (rows || [])
    .slice(0, 6)
    .map((r) => `<div class="rc-card">
        <div class="rc-top">
          <span class="mono">${esc(r.txn_id || "-")}</span>
          <span class="risk-cell" style="color:${RISK_COLOR(r.risk_score)}">${Math.round(r.risk_score || 0)}</span>
        </div>
        <div class="rc-sub">${esc(r.agent_id || "")} · ${esc(r.reason || "")}</div>
        <div class="rc-actions">
          <button data-id="${esc(r.txn_id)}" data-act="approve">Approve</button>
          <button data-id="${esc(r.txn_id)}" data-act="escalate">Escalate</button>
          <button data-id="${esc(r.txn_id)}" data-act="block" class="danger">Block</button>
        </div>
      </div>`)
    .join("");
  list.querySelectorAll("button").forEach((b) =>
    b.addEventListener("click", () => resolveReview(b.dataset.act, b.dataset.id))
  );
}

async function resolveReview(action, txnId) {
  try {
    await jpost("/api/review/" + encodeURIComponent(txnId), { action });
    showToast("Review " + action + ": " + txnId, "ok");
    await Promise.all([loadReview(), loadBlocked(), loadLedger(), loadKs()]);
  } catch (err) {
    showToast("Review failed: " + err.message, "bad");
  }
}

async function loadBlocked() {
  const rows = await jfetch("/api/blocked");
  const cnt = $("#blockedCount");
  if (cnt) cnt.textContent = (rows || []).length + " blocked";
  const list = $("#blockedList");
  if (list) {
    list.innerHTML = (rows || [])
      .slice(0, 6)
      .map((r) => `<div class="bc-card">${MONO(r.txn_id || "-")} <span class="risk-cell" style="color:${RISK_COLOR(r.risk_score)}">${Math.round(r.risk_score || 0)}</span></div>`)
      .join("");
  }
}

/* ========================================================= */
/*  Ledger + charts                                          */
/* ========================================================= */
async function loadLedger() {
  const d = await jfetch("/api/ledger");
  const cnt = $("#ledgerCount");
  if (cnt) cnt.textContent = (d.ledger || []).length + " entries";
  const pill = $("#ledgerStatus");
  if (pill) {
    pill.textContent = d.integrity_ok ? "Ledger: verified" : "Ledger: TAMPERED";
    pill.className = "ledger-pill " + (d.integrity_ok ? "ok" : "bad");
  }
  const list = $("#ledgerList");
  if (list) {
    list.innerHTML = (d.ledger || [])
      .slice(-8)
      .reverse()
      .map((e) => `<div class="ledger-card">
        <div class="lc-head"><span class="mono">${esc(e.block_id || "-")}</span><span class="mono">${esc((e.hash || "").slice(0, 14))}</span></div>
        <div class="lc-sub">${esc(e.agent_id || "")} · ${esc(e.decision || "")}</div>
      </div>`)
      .join("");
  }
}

let mixChart = null;
let incidentChart = null;

function renderCharts(d) {
  const dist = d.decision_distribution || {};
  if (window.Chart) {
    const labels = ["EXECUTE", "CONSTRAIN", "ESCALATE", "BLOCK"];
    const values = labels.map((k) => dist[k] || 0);
    const colors = labels.map((k) => DECISION_COLORS[k]);
    if (mixChart) mixChart.destroy();
    const mc = $("#mixChart");
    if (mc) {
      mixChart = new Chart(mc.getContext("2d"), {
        type: "doughnut",
        data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
        options: {
          plugins: { legend: { display: false } },
          cutout: "62%",
        },
      });
    }
  }
}

async function refreshAll() {
  try {
    const d = await loadKs();
    await Promise.all([
      loadTxns(),
      loadAgents(),
      loadReview(),
      loadBlocked(),
      loadLedger(),
    ]);
    renderCharts(d);
    const ts = $("#lastUpdated");
    if (ts) ts.textContent = new Date().toLocaleTimeString();
  } catch (err) {
    showToast("Refresh failed: " + err.message, "bad");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadScenarios();
  refreshAll();
  const btn = $("#refreshBtn");
  if (btn) btn.addEventListener("click", refreshAll);
  const auto = $("#autoRefresh");
  if (auto) {
    auto.addEventListener("change", () => {
      if (auto._t) clearInterval(auto._t);
      auto._t = auto.checked ? setInterval(refreshAll, 25000) : null;
    });
  }
});
