let currentPump = null;
let customMode = false;

function loadPumpData() {

    if (!currentPump) return;

    const date = document.getElementById("selected-date").value;
    let datetimeParam = "";

    if (customMode && date) {
        const hour = document.getElementById("hourSelect").value;
        const minute = document.getElementById("minuteSelect").value;
        datetimeParam = `${date} ${hour}:${minute}`;
    }

    fetch(`/api/pump-popup?pump=${currentPump}&date=${date}&datetime=${datetimeParam}`)
        .then(res => res.json())
        .then(data => {

            let tbody = document.getElementById("pump-tbody");
            tbody.innerHTML = "";

            if (customMode && data.custom) {
                let c = data.custom;

                tbody.innerHTML = `
                <tr>
                    <td>${c.date}</td>
                    <td>${c.time}</td>
                    <td>${c.value ?? '-'}</td>
                    <td>${c.avg ?? '-'}</td>
                    <td>${c.max ?? '-'}</td>
                    <td>${c.min ?? '-'}</td>
                </tr>`;
                return;
            }

            if (data.today) addRow("Today", data.today, tbody);
            if (data.selected) addRow("Selected", data.selected, tbody);
        });
}

function addRow(label, v, tbody) {
    let tr = document.createElement("tr");
    tr.innerHTML = `
        <td>${label}</td>
        <td>${v.latest ?? '-'}</td>
        <td>${v.recent ?? '-'}</td>
        <td>${v.avg30m ?? '-'}</td>
        <td>${v.avg1hr ?? '-'}</td>
        <td>${v.avg1d ?? '-'}</td>
        <td>${v.max ?? '-'}</td>
        <td>${v.min ?? '-'}</td>
    `;
    tbody.appendChild(tr);
}