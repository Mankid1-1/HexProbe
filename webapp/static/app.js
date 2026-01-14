const repoForm = document.getElementById("repo-form");
const runForm = document.getElementById("run-form");
const repoSelect = document.getElementById("repo-select");
const refreshButton = document.getElementById("refresh");
const runsContainer = document.getElementById("runs");
const repoCount = document.getElementById("repo-count");
const runCount = document.getElementById("run-count");

const renderRuns = (runs) => {
  if (!runs.length) {
    runsContainer.innerHTML = "<p class=\"empty\">No probes yet. Launch a run to get started.</p>";
    return;
  }
  runsContainer.innerHTML = runs
    .map((run) => {
      const findings = run.result.findings
        .map(
          (finding) =>
            `<li><strong>${finding.category}</strong> — ${finding.message} ${
              finding.location ? `<em>${finding.location}</em>` : ""
            }</li>`
        )
        .join("");
      const approvals = Object.entries(run.approvals)
        .map(
          ([name, approved]) =>
            `<li class=\"approval\"><span>${name}</span><span class=\"badge ${
              approved ? "badge-pass" : "badge-fail"
            }\">${approved ? "Approved" : "Flagged"}</span></li>`
        )
        .join("");
      return `
        <div class="run-card">
          <div class="run-header">
            <div>
              <span class="run-title">${run.repo_name}</span>
              <span class="run-subtitle">${run.probe_name}</span>
            </div>
            <span class="badge badge-${run.result.severity}">${run.result.severity}</span>
          </div>
          <div class="run-body">
            <div class="run-section">
              <h3>Findings</h3>
              <ul>${findings}</ul>
            </div>
            <div class="run-section">
              <h3>Agent approvals</h3>
              <ul>${approvals}</ul>
            </div>
          </div>
        </div>`;
    })
    .join("");
};

const refreshState = async () => {
  const response = await fetch("/api/state");
  const state = await response.json();
  repoCount.textContent = state.repos.length;
  runCount.textContent = state.runs.length;
  repoSelect.innerHTML =
    "<option value=\"\" disabled selected>Select a repo</option>" +
    state.repos
      .map(
        (repo) => `<option value="${repo.id}">${repo.name} — ${repo.path}</option>`
      )
      .join("");
  renderRuns(state.runs);
};

repoForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(repoForm);
  const payload = Object.fromEntries(formData.entries());
  const response = await fetch("/api/repos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    repoForm.reset();
    await refreshState();
  } else {
    const error = await response.json();
    alert(error.error || "Failed to add repo");
  }
});

runForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(runForm);
  const payload = Object.fromEntries(formData.entries());
  const response = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    await refreshState();
  } else {
    const error = await response.json();
    alert(error.error || "Failed to run probe");
  }
});

refreshButton.addEventListener("click", refreshState);
