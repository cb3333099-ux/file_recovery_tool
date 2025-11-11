// 🌙 Toggle dark mode
document.addEventListener("DOMContentLoaded", () => {
    const themeBtn = document.getElementById("themeToggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            themeBtn.textContent = document.body.classList.contains("dark-mode")
                ? "☀️ Light Mode"
                : "🌙 Dark Mode";
        });
    }
});

function browseDrive() {
    fetch('/browse_drive')
        .then(r => r.json())
        .then(data => document.getElementById('drive').value = data.path);
}

function browseSave() {
    fetch('/browse_save')
        .then(r => r.json())
        .then(data => document.getElementById('saveDir').value = data.path);
}

function scanFiles() {
    const drive = document.getElementById('drive').value;
    const fileType = document.getElementById('fileType').value;
    if (!drive) return alert("Please select a drive");

    document.getElementById('status').textContent = "Scanning for deleted files...";
    fetch(`/scan_files?drive=${encodeURIComponent(drive)}&fileType=${encodeURIComponent(fileType)}`)
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById('fileList');
            list.innerHTML = '';
            data.files.forEach(file => {
                const option = document.createElement('option');
                option.textContent = `${file.modified_time} - ${file.path} (${file.size || 'unknown'} KB)`;
                list.appendChild(option);
            });
            document.getElementById('status').textContent = "Scanning complete.";
        });
}

function recoverFiles() {
    const saveDir = document.getElementById('saveDir').value;
    const selectedFiles = Array.from(document.getElementById('fileList').selectedOptions).map(o => o.textContent);
    if (!saveDir) return alert("Select a save directory");
    if (!selectedFiles.length) return alert("Select files to recover");

    document.getElementById('status').textContent = "Recovering...";
    fetch('/recover_files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ saveDir, files: selectedFiles }),
    })
    .then(r => r.json())
    .then(() => {
        document.getElementById('status').textContent = "Recovery complete.";
    });
}

// 🗑️ Delete Permanently
function deleteFiles() {
    const selectedFiles = Array.from(document.getElementById('fileList').selectedOptions).map(o => o.textContent);
    if (!selectedFiles.length) return alert("Select files to delete permanently!");

    if (confirm("Are you sure you want to delete these files permanently?")) {
        fetch('/delete_files', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: selectedFiles }),
        })
        .then(() => {
            alert("Files deleted successfully!");
            scanFiles(); // refresh list
        });
    }
}
