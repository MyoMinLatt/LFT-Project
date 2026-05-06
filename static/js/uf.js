// ==========================================
// GLOBAL STATE
// ==========================================

window.currentDevice = null;
window.currentParameter = null;
window.currentInterval = "30min";
window.currentStart = "";
window.currentEnd = "";


// ==========================================
// DEVICE BUTTON CLICK
// ==========================================

function selectDevice(parameter, device) {

    // If clicking same device again → TOGGLE OFF
    if (window.currentDevice === device &&
        window.currentParameter === parameter) {

        clearGraph();
        window.currentDevice = null;
        window.currentParameter = null;
        return;
    }

    // Otherwise activate
    window.currentDevice = device;
    window.currentParameter = parameter;

    loadData();
}


// ==========================================
// INTERVAL BUTTON CLICK
// ==========================================

function setInterval(interval) {

    window.currentInterval = interval;

    // Only reload if device is selected
    if (window.currentDevice && window.currentParameter) {
        loadData();
    }
}


// ==========================================
// CUSTOM TIME RANGE
// ==========================================

function loadCustomRange() {

    const start = document.getElementById("startTime").value;
    const end = document.getElementById("endTime").value;

    if (!start || !end) {
        alert("Please select both start and end time.");
        return;
    }

    window.currentStart = start;
    window.currentEnd = end;

    if (window.currentDevice && window.currentParameter) {
        loadData();
    }
}


// ==========================================
// LOAD DATA FROM BACKEND
// ==========================================

function loadData() {

    fetch(`/api/uf-data?parameter=${encodeURIComponent(window.currentParameter)}`
        + `&device=${encodeURIComponent(window.currentDevice)}`
        + `&interval=${window.currentInterval}`
        + `&start=${window.currentStart}`
        + `&end=${window.currentEnd}`)

    .then(response => response.json())
    .then(data => {

        if (!data.timestamps || data.timestamps.length === 0) {
            clearGraph();
            return;
        }

        updateGraph(data.timestamps, data.values);
        updateTable(data);
    })
    .catch(error => {
        console.error("UF FETCH ERROR:", error);
        clearGraph();
    });
}


// ==========================================
// CLEAR GRAPH + TABLE
// ==========================================

function clearGraph() {

    if (window.ufChart) {
        window.ufChart.destroy();
    }

    document.getElementById("latestValue").innerText = "-";
    document.getElementById("meanValue").innerText = "-";
    document.getElementById("minValue").innerText = "-";
    document.getElementById("maxValue").innerText = "-";
    document.getElementById("dataTime").innerText = "-";
}


// ==========================================
// UPDATE GRAPH
// ==========================================

function updateGraph(labels, values) {

    const ctx = document.getElementById("ufChart").getContext("2d");

    if (window.ufChart) {
        window.ufChart.destroy();
    }

    window.ufChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: window.currentParameter,
                data: values,
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}


// ==========================================
// UPDATE KEY-VALUE TABLE
// ==========================================

function updateTable(data) {

    document.getElementById("latestValue").innerText = data.latest;
    document.getElementById("meanValue").innerText = data.mean;
    document.getElementById("minValue").innerText = data.min;
    document.getElementById("maxValue").innerText = data.max;
    document.getElementById("dataTime").innerText = data.data_time;
}