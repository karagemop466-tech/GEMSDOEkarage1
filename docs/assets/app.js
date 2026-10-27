/* GitHub-only source-revision monitor. No scores, organizer data, or release
   permission are inferred from a revision check. */
(() => {
  "use strict";
  const button = document.getElementById("refresh-sources");
  const status = document.getElementById("feed-status");
  const chips = Array.from(document.querySelectorAll("[data-source-repo][data-source-ref]"));
  if (!button || !status || chips.length === 0) return;
  let running = false;

  async function checkChip(chip) {
    const target = chip.querySelector("[data-source-state]");
    const repo = chip.dataset.sourceRepo;
    const expected = chip.dataset.sourceRef;
    if (!target || !/^buffedlizard55-lab\/GEMSDOE(?:24|25|27|28|30|31|32|33|36)$/.test(repo) || !/^[0-9a-f]{40}$/.test(expected)) {
      if (target) { target.textContent = "Unavailable"; target.dataset.state = "unknown"; }
      return "unknown";
    }
    target.textContent = "Checking…";
    target.dataset.state = "unknown";
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`https://api.github.com/repos/${repo}/commits/main`, {
        headers: { Accept: "application/vnd.github+json" }, cache: "no-store", signal: controller.signal
      });
      if (!response.ok) throw new Error(`GitHub HTTP ${response.status}`);
      const body = await response.json();
      if (!/^[0-9a-f]{40}$/.test(body.sha || "")) throw new Error("Missing commit SHA");
      const same = body.sha === expected;
      target.textContent = same ? "At audit pin" : "Changed · re-audit";
      target.dataset.state = same ? "same" : "changed";
      return same ? "same" : "changed";
    } catch (_) {
      target.textContent = "Unavailable";
      target.dataset.state = "unknown";
      return "unknown";
    } finally {
      window.clearTimeout(timer);
    }
  }

  async function refresh() {
    if (running) return;
    running = true;
    button.disabled = true;
    status.textContent = "Checking peer GitHub revisions…";
    try {
      const results = await Promise.all(chips.map(checkChip));
      const same = results.filter(value => value === "same").length;
      const changed = results.filter(value => value === "changed").length;
      const unknown = results.filter(value => value === "unknown").length;
      status.textContent = `Checked ${new Date().toISOString().replace("T", " ").replace(/\.\d{3}Z$/, " UTC")} · ${same} at audit pin · ${changed} changed · ${unknown} unavailable. Changed or unavailable is not a pass.`;
    } finally {
      running = false;
      button.disabled = false;
    }
  }
  button.addEventListener("click", refresh);
  refresh();
})();
