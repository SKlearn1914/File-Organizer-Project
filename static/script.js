function showLoading(show) {
    document.getElementById("loading").style.display = show ? "block" : "none";
}

function updateProgress(percent) {
    const bar = document.getElementById("progressBar");
    bar.style.width = percent + "%";
}

function showProgress(show) {
    document.getElementById("progressContainer").style.display = show ? "block" : "none";
}
function addCategory() {
    let name = document.getElementById("categoryName").value;
    let exts = document.getElementById("categoryExt").value;

    if (!name || !exts) {
        alert("Enter both fields");
        return;
    }

    let extList = exts.split(",").map(e => e.trim().toLowerCase());

    fetch('/add-category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, extensions: extList })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                loadCategories();
            } else {
                alert(data.message);
            }
        });
}
function removeCategory(name) {
    fetch('/remove-category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
        .then(res => res.json())
        .then(() => loadCategories());
}
function loadCategories() {
    fetch('/get-categories')
        .then(res => res.json())
        .then(data => {
            let box = document.getElementById("categoryList");
            box.innerHTML = "";

            for (let key in data) {
                let div = document.createElement("div");

                div.innerHTML = `
                <b>${key}</b>: ${data[key].join(", ")}
                <button style="background-color: purple;" onclick="removeCategory('${key}')">❌</button>
            `;

                box.appendChild(div);
            }
        });
}
window.onload = loadCategories;
function setFolder() {
    let path = document.getElementById("folderPath").value;

    fetch('/set-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                alert("✅ " + data.message);
            } else {
                alert("❌ " + data.message);
            }
        });
}
function preview() {
    showLoading(true);

    fetch('/preview')
        .then(res => res.json())
        .then(data => {
            showLoading(false);

            let output = "";
            data.forEach(item => {
                output += `${item.file} → ${item.category}\n`;
            });

            document.getElementById("output").innerText = output;
        });
}

function organize() {
    showLoading(true);
    showProgress(true);

    let progress = 0;
    let interval = setInterval(() => {
        if (progress < 90) {
            progress += 10;
            updateProgress(progress);
        }
    }, 300);

    fetch('/organize', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            clearInterval(interval);
            updateProgress(100);

            setTimeout(() => {
                showLoading(false);
                showProgress(false);
                updateProgress(0);
                alert("Organized: " + data.total);
            }, 500);
        });
}

function undo() {
    fetch('/undo', { method: 'POST' })
        .then(res => res.json())
        .then(() => alert("Undo Done"));
}

function exportCSV() {
    window.location.href = '/export';
}
// Load default categories visually (optional)
