const OWNER = "buffedlizard55-lab";
const PROJECT = "GEMSDOE32";
const REPO_API = `https://api.github.com/repos/${OWNER}/${PROJECT}`;
const README_API = `${REPO_API}/contents/README.md?ref=main`;

function cleanMarkdown(value) {
  return value
    .replace(/<br\s*\/?>/gi, " · ")
    .replace(/<[^>]*>/g, "")
    .replace(/\*\*/g, "")
    .replace(/`/g, "")
    .replace(/\\\|/g, "|")
    .replace(/\s+/g, " ")
    .trim();
}

function firstCodeSpan(value) {
  return value.match(/`([^`]+)`/)?.[1]?.trim() ?? "";
}

function safeUniqueness(value) {
  const text = cleanMarkdown(value);
  const historicalNo = /(?:Hist|Champ):\s*NO/i.test(text);
  const latestNo = /;\s*[^;:]+:\s*NO/i.test(text);
  const latestYes = /;\s*[^;:]+:\s*YES/i.test(text);
  if (historicalNo && latestNo) {
    return "Historical entry: source report says not unique; newest artifact also fails the listed overlap check.";
  }
  if (historicalNo && latestYes) {
    return "Historical entry: source report says not unique; newest artifact passes a listed subset check, but is not release-approved.";
  }
  if (historicalNo) {
    return "Historical entry: source report says not unique; see linked report for current-artifact details.";
  }
  return "See linked source report; no independent raster comparison was run here.";
}

function safeDecision(value) {
  const text = cleanMarkdown(value);
  if (/ALREADY SUBMITTED/i.test(text)) {
    return "NO — already submitted; not eligible for resubmission";
  }
  if (/DO NOT SUBMIT/i.test(text)) {
    return "NO — do not submit; see linked source report for gate rationale";
  }
  return "No approved download decision in this feed; review source report";
}

export function latestReportPathFromReadme(readme) {
  const matches = [...readme.matchAll(/\((docs\/research\/[^\s)]+(?:nine-site|executive-summary)[^\s)]*\.md)(?:#[^)]*)?\)/gi)];
  if (!matches.length) throw new Error("No linked nine-site research report found in source README");
  return matches[0][1];
}

export function parseFocusSiteTable(markdown) {
  const lines = markdown.split(/\r?\n/);
  const headingIndex = lines.findIndex((line) =>
    /Nine-Site Executive Decision Table/i.test(line),
  );
  if (headingIndex < 0) throw new Error("Nine-site table heading not found");

  const rows = [];
  for (const line of lines.slice(headingIndex + 1)) {
    if (!line.trim().startsWith("|")) {
      if (rows.length) break;
      continue;
    }
    const cells = line.split("|").slice(1, -1).map((cell) => cell.trim());
    if (cells.length < 6 || /^\s*:?-{2,}/.test(cells[0])) continue;

    const site = cells[0].match(/\bGEMSDOE\d+\b/)?.[0];
    if (!site) continue;
    rows.push({
      site,
      historicalArtifact: firstCodeSpan(cells[1]) || "Not listed",
      newestArtifact: firstCodeSpan(cells[2]) || "Not listed",
      uniqueness: safeUniqueness(cells[4]),
      decision: safeDecision(cells[5]),
    });
  }

  if (rows.length !== 9) {
    throw new Error(`Expected 9 focus-site rows; found ${rows.length}`);
  }
  return rows;
}

async function fetchGitHubText(url) {
  const response = await fetch(url, {
    headers: {
      Accept: "application/vnd.github.raw+json",
    },
  });
  if (!response.ok) {
    throw new Error(`GitHub API returned HTTP ${response.status}`);
  }
  return response.text();
}

function addCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  row.append(cell);
}

function displayRows(rows) {
  const tbody = document.querySelector("#live-feed-rows");
  if (!tbody) return;
  tbody.replaceChildren();
  for (const item of rows) {
    const row = document.createElement("tr");
    addCell(row, item.site);
    addCell(row, item.newestArtifact);
    addCell(row, item.uniqueness);
    addCell(row, item.decision);
    tbody.append(row);
  }
}

function displayFeedError(message) {
  const tbody = document.querySelector("#live-feed-rows");
  if (!tbody) return;
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 4;
  cell.textContent = message;
  row.append(cell);
  tbody.replaceChildren(row);
}

export async function refreshLiveFeed() {
  const status = document.querySelector("#live-feed-status");
  if (!status) return;
  status.textContent = "Refreshing the owner-maintained public source report…";

  try {
    const readmeText = await fetchGitHubText(README_API);
    const reportPath = latestReportPathFromReadme(readmeText);
    const reportUrl = `https://github.com/${OWNER}/${PROJECT}/blob/main/${reportPath}`;
    const encodedPath = reportPath.split("/").map(encodeURIComponent).join("/");
    const reportText = await fetchGitHubText(`${REPO_API}/contents/${encodedPath}?ref=main`);
    const rows = parseFocusSiteTable(reportText);
    displayRows(rows);
    const reportLink = document.querySelector("#live-source-report");
    if (reportLink) reportLink.href = reportUrl;
    const checkedAt = new Date().toISOString().replace("T", " ").replace(".000Z", " UTC");
    status.textContent = `Live source check succeeded at ${checkedAt}. The report path linked from the current GEMSDOE32 README is ${reportPath}. This is owner-maintained status, not an organizer score or receipt.`;
  } catch (error) {
    displayFeedError("No current feed data loaded. Use the linked source report directly; prior rows are not retained as current.");
    status.textContent = `Live refresh unavailable (${error.message}). The feed has been cleared rather than showing a stale snapshot.`;
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("#refresh-live-feed");
    button?.addEventListener("click", refreshLiveFeed);
    refreshLiveFeed();
  });
}
