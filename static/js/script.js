// static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
  const scanBtn = document.querySelector(".btn-primary");
  const recoverBtn = document.querySelector(".btn-success");
  if (scanBtn) scanBtn.addEventListener("click", scanFiles);
  if (recoverBtn) recoverBtn.addEventListener("click", recoverSelected);

  // Close modal on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closePreview();
  });

  // Close modal when clicking outside content
  const modal = document.getElementById("previewModal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closePreview();
    });
  }
});

// === STATUS & SPINNER ===
function setStatus(text) {
  const status = document.getElementById("status");
  if (status) status.textContent = text;
}

function toggleSpinner(show) {
  const spinner = document.getElementById("loading-spinner");
  if (!spinner) return;
  spinner.classList.toggle("hidden", !show);
}

// === FILE BROWSING ===
function browseDrive() {
  fetch("/browse_drive")
    .then((r) => r.json())
    .then((data) => {
      if (data && data.path) document.getElementById("drive").value = data.path;
    })
    .catch((err) => console.error("browseDrive error:", err));
}

function browseSave() {
  fetch("/browse_save")
    .then((r) => r.json())
    .then((data) => {
      if (data && data.path) document.getElementById("saveDir").value = data.path;
    })
    .catch((err) => console.error("browseSave error:", err));
}

// === SCAN (with filters) ===
function scanFiles() {
  const drive = document.getElementById("drive").value;
  const fileType = document.getElementById("fileType").value;
  const minSize = document.getElementById("minSize") ? document.getElementById("minSize").value : null;
  const maxSize = document.getElementById("maxSize") ? document.getElementById("maxSize").value : null;
  const startDate = document.getElementById("startDate") ? document.getElementById("startDate").value : null;
  const endDate = document.getElementById("endDate") ? document.getElementById("endDate").value : null;

  if (!drive) {
    alert("Please select a drive/path to scan.");
    return;
  }

  setStatus("Starting scan...");
  toggleSpinner(true);

  fetch("/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      drive: drive,
      file_type: fileType,
      min_size: minSize,
      max_size: maxSize,
      start_date: startDate,
      end_date: endDate
    }),
  })
    .then((r) => r.json())
    .then((data) => {
      toggleSpinner(false);
      if (data && data.job_id) {
        setStatus("Scan started — please wait...");
        pollProgress("scan", data.job_id, updateResultsOnComplete);
      } else if (data && data.files) {
        renderResults(data.files);
        setStatus("Scan complete.");
      } else {
        setStatus("Scan started.");
      }
    })
    .catch((err) => {
      toggleSpinner(false);
      console.error("scanFiles error:", err);
      setStatus("Scan failed — check server logs.");
    });
}

// === RECOVER ===
function recoverSelected() {
  const saveDir = document.getElementById("saveDir").value;
  if (!saveDir) {
    alert("Please select a save directory.");
    return;
  }

  const checkboxes = document.querySelectorAll("#results input[type='checkbox']:checked");
  if (checkboxes.length === 0) {
    alert("Please select at least one file to recover.");
    return;
  }

  const files = Array.from(checkboxes).map((cb) => ({ path: cb.dataset.path }));
  setStatus("Starting recovery...");
  toggleSpinner(true);

  fetch("/recover", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ save_dir: saveDir, files: files }),
  })
    .then((r) => r.json())
    .then((data) => {
      toggleSpinner(false);
      if (data && data.job_id) {
        setStatus("Recovery started — please wait...");
        pollProgress("recover", data.job_id, (job) => {
          // Show number of recovered files if available
          const recovered = (job && job.recovered) ? job.recovered.length : 'unknown';
          alert(`Recovery finished. Files recovered: ${recovered}`);
          setStatus("Recovery complete.");
        });
      } else if (data && data.recovered) {
        alert("Recovered " + data.recovered.length + " files.");
        setStatus("Recovery complete.");
      } else {
        setStatus("Recovery request sent.");
      }
    })
    .catch((err) => {
      toggleSpinner(false);
      console.error("recoverSelected error:", err);
      setStatus("Recovery failed — check server logs.");
    });
}

// === PROGRESS POLLING ===
function pollProgress(type, job_id, onComplete) {
  const progressBar = document.getElementById("progressBar");

  const poll = () => {
    fetch("/progress")
      .then((r) => r.json())
      .then((data) => {
        const value = data[type] || 0;
        if (progressBar) progressBar.style.width = value + "%";
        if (value >= 100) {
          // fetch job result
          fetch(`/job_result?job_id=${encodeURIComponent(job_id)}`)
            .then((r) => r.json())
            .then((job) => {
              if (onComplete) onComplete(job);
            })
            .catch((e) => {
              console.error("job_result fetch error:", e);
              if (onComplete) onComplete({});
            });
        } else {
          setTimeout(poll, 600);
        }
      })
      .catch((err) => {
        console.error("pollProgress error:", err);
        setTimeout(poll, 1000);
      });
  };

  poll();
}

// === RENDER RESULTS + SUMMARY ===
function renderResults(files) {
  const results = document.getElementById("results");
  const summary = document.getElementById("summary");
  results.innerHTML = "";
  if (summary) summary.classList.add("hidden");

  if (!files || files.length === 0) {
    results.innerHTML = "<p>No files found.</p>";
    return;
  }

  // Summary
  const counts = {};
  files.forEach((f) => {
    const ext = (f.path.split(".").pop() || "").toLowerCase();
    counts[ext] = (counts[ext] || 0) + 1;
  });

  if (summary) {
    let summaryHtml = "<h3>📊 Scan Summary</h3><ul>";
    Object.entries(counts).forEach(([ext, count]) => {
      summaryHtml += `<li><strong>${ext ? ext.toUpperCase() : 'NO EXT'}</strong>: ${count}</li>`;
    });
    summaryHtml += "</ul>";
    summary.innerHTML = summaryHtml;
    summary.classList.remove("hidden");
  }

  // File list
  files.forEach((f) => {
    const name = f.path.split(/[\\/]/).pop();
    const size = f.size_kb ? `${f.size_kb} KB` : '';
    const row = document.createElement("div");
    row.className = "result-row";
    row.innerHTML = `
      <label style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;width:100%">
        <input type="checkbox" data-path="${escapeHtml(f.path)}">
        <div style="display:flex;flex-direction:column;flex:1;min-width:220px;">
          <span class="file-name">${escapeHtml(name)}</span>
          <small class="file-path">${escapeHtml(f.path)}</small>
        </div>
        <div style="display:flex;gap:8px;align-items:center;white-space:nowrap">
          <small class="file-size">📦 ${escapeHtml(size)}</small>
          <button class="btn-preview" onclick="previewFile('${f.path.replace(/\\/g, '\\\\')}')">👁️ Preview</button>
        </div>
      </label>
    `;
    results.appendChild(row);
  });
}

function updateResultsOnComplete(job) {
  if (job && job.files) {
    renderResults(job.files);
    setStatus("Scan complete.");
  } else if (job && job.status === "error") {
    setStatus("Scan failed.");
    alert("Scan error: " + (job.error || "unknown"));
  } else {
    setStatus("Scan complete.");
  }
}

// === PREVIEW (calls /preview) ===
function previewFile(path) {
  const preview = document.getElementById("previewContent");
  const modal = document.getElementById("previewModal");
  if (!preview || !modal) return;
  preview.innerHTML = "<p>Loading preview...</p>";
  modal.classList.remove("hidden");

  fetch(`/preview?path=${encodeURIComponent(path)}`)
    .then((r) => r.json())
    .then((data) => {
      if (!data) {
        preview.innerHTML = "<p>Preview not available.</p>";
        return;
      }
      if (data.type === "image" && data.content) {
        preview.innerHTML = `<img src="${data.content}" alt="Image preview" style="max-width:100%;border-radius:8px;">`;
      } else if (data.type === "text" && data.content) {
        preview.innerHTML = `<pre>${escapeHtml(data.content)}</pre>`;
      } else if (data.error) {
        preview.innerHTML = `<p style="color:red;">${escapeHtml(data.error)}</p>`;
      } else {
        preview.innerHTML = "<p>Preview not available.</p>";
      }
    })
    .catch((err) => {
      console.error("Preview error:", err);
      preview.innerHTML = "<p>Preview failed to load.</p>";
    });
}

function closePreview() {
  const modal = document.getElementById("previewModal");
  if (modal) modal.classList.add("hidden");
}

// === UTIL ===
function escapeHtml(text) {
  if (!text) return "";
  return String(text).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

/* ======================
   DRAGGABLE & RESIZABLE MODAL
   ====================== */
let offsetX, offsetY, isDragging = false, isResizing = false;

function startDrag(e) {
  // require the drag-handle target (only start drag when clicking header)
  if (!e) return;
  // check if click was inside the drag-handle element or modal-header
  const target = e.target;
  if (!target.classList.contains("drag-handle") && !target.classList.contains("modal-header")) {
    return;
  }

  const modal = document.getElementById("modalContent");
  if (!modal) return;
  isDragging = true;
  offsetX = e.clientX - modal.offsetLeft;
  offsetY = e.clientY - modal.offsetTop;
  modal.style.position = "absolute";
  document.addEventListener("mousemove", dragModal);
  document.addEventListener("mouseup", stopDrag);
}

function dragModal(e) {
  if (!isDragging) return;
  const modal = document.getElementById("modalContent");
  if (!modal) return;
  let left = e.clientX - offsetX;
  let top = e.clientY - offsetY;

  // keep modal within viewport bounds
  const pad = 8;
  left = Math.max(pad, Math.min(left, window.innerWidth - modal.offsetWidth - pad));
  top = Math.max(pad, Math.min(top, window.innerHeight - modal.offsetHeight - pad));

  modal.style.left = left + "px";
  modal.style.top = top + "px";
}

function stopDrag() {
  isDragging = false;
  document.removeEventListener("mousemove", dragModal);
  document.removeEventListener("mouseup", stopDrag);
}

function startResize(e) {
  e.stopPropagation();
  const modal = document.getElementById("modalContent");
  if (!modal) return;
  isResizing = true;
  const startWidth = modal.offsetWidth;
  const startHeight = modal.offsetHeight;
  const startX = e.clientX;
  const startY = e.clientY;

  function doResize(ev) {
    if (!isResizing) return;
    const minW = 300, minH = 200;
    let newW = startWidth + (ev.clientX - startX);
    let newH = startHeight + (ev.clientY - startY);
    newW = Math.max(minW, newW);
    newH = Math.max(minH, newH);
    // keep within viewport
    newW = Math.min(window.innerWidth - 40, newW);
    newH = Math.min(window.innerHeight - 40, newH);
    modal.style.width = newW + "px";
    modal.style.height = newH + "px";
  }

  function stopResize() {
    isResizing = false;
    document.removeEventListener("mousemove", doResize);
    document.removeEventListener("mouseup", stopResize);
  }

  document.addEventListener("mousemove", doResize);
  document.addEventListener("mouseup", stopResize);
}
