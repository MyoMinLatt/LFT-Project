let currentDevice = null;
let customMode = false;

function loadTable() {
    if (!currentDevice) return;

    let selectedDate = selectedDate || "";
    let datetimeParam = "";

    if (customMode && selectedDate) {
        const hour = document.getElementById("hourSelect").value;
        const minute = document.getElementById("minuteSelect").value;
        datetimeParam = `${selectedDate} ${hour}:${minute}`;
    }

    fetch(`/device_popup?device=${currentDevice}&date=${selectedDate}&datetime=${datetimeParam}`)
        .then(res => res.json())
        .then(data => {

            let html = "";

            if (customMode && data.custom) {
                const c = data.custom;
                html = `
                <table>
                <tr><th>Date</th><th>Date</th><th>Value</th><th>Avg</th><th>Max</th><th>Min</th></tr>
                <tr>
                    <td>${c.date}</td>
                    <td>${c.time}</td>
                    <td>${c.value ?? '-'}</td>
                    <td>${c.avg ?? '-'}</td>
                    <td>${c.max ?? '-'}</td>
                    <td>${c.min ?? '-'}</td>
                </tr>
                </table>`;
            } else {
                let t = data.today || {};
                let s = data.selected;

                html = `
                <table>
                <tr><th>Time</th><th>Latest</th><th>Recent</th><th>Avg30m</th><th>Avg1hr</th><th>Avg1d</th><th>Max</th><th>Min</th></tr>
                <tr>
                    <td>Today</td>
                    <td>${t.latest}</td>
                    <td>${t.recent}</td>
                    <td>${t.avg30m}</td>
                    <td>${t.avg1hr}</td>
                    <td>${t.avg1d}</td>
                    <td>${t.max}</td>
                    <td>${t.min}</td>
                </tr>
                ${s ? `<tr>
                    <td>${selectedDate}</td>
                    <td>${s.latest}</td>
                    <td>${s.recent}</td>
                    <td>${s.avg30m}</td>
                    <td>${s.avg1hr}</td>
                    <td>${s.avg1d}</td>
                    <td>${s.max}</td>
                    <td>${s.min}</td>
                </tr>` : ""}
                </table>`;
            }

            document.getElementById("popupTable").innerHTML = html;
        });
}