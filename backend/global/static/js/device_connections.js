async function loadDeviceConnections() {

    try {

        const response =
            await fetch(
                DEVICE_CONNECTIONS_URL
            );

        if (!response.ok) {

            throw new Error(
                "Erro ao carregar dispositivos."
            );
        }

        const result =
            await response.json();

        renderDevices(
            result.devices
        );

    } catch (error) {

        console.error(
            "Erro:",
            error
        );

    }
}


function renderDevices(devices) {

    const tbody =
        document.getElementById(
            "device-list"
        );

    tbody.innerHTML = "";


    let online = 0;
    let offline = 0;


    devices.forEach(device => {

        if (device.status === "online") {

            online++;

        } else {

            offline++;

        }


        const row =
            document.createElement("tr");


        const statusLabel =
            device.status === "online"
                ? "ONLINE"
                : "OFFLINE";


        const statusClass =
            device.status === "online"
                ? "status-online"
                : "status-offline";


        let ultimoEvento = "-";


        if (device.ultimo_evento) {

            const date =
                new Date(
                    device.ultimo_evento
                );

            ultimoEvento =
                date.toLocaleString(
                    "pt-BR"
                );
        }


        row.innerHTML = `

            <td>
                <strong>
                    ${escapeHtml(device.hospital)}
                </strong>
            </td>

            <td>

                <span class="
                    connection-status
                    ${statusClass}
                ">

                    <span class="status-dot"></span>

                    ${statusLabel}

                </span>

            </td>

            <td>
                ${ultimoEvento}
            </td>
        `;


        tbody.appendChild(row);

    });


    document.getElementById(
        "total-devices"
    ).textContent = devices.length;


    document.getElementById(
        "online-devices"
    ).textContent = online;


    document.getElementById(
        "offline-devices"
    ).textContent = offline;
}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDeviceConnections();


        document
            .getElementById(
                "refresh-devices"
            )
            .addEventListener(
                "click",
                loadDeviceConnections
            );


        /*
         * Atualização automática
         */

        setInterval(
            loadDeviceConnections,
            10000
        );

    }
);

