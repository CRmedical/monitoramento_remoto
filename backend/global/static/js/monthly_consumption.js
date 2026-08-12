async function loadMonthlyConsumption() {

    const tbody =
        document.getElementById(
            "monthlyConsumptionBody"
        );

    if (!tbody) {
        return;
    }

    try {

        const response =
            await fetch(
                MONTHLY_CONSUMPTION_URL
            );

        if (!response.ok) {

            throw new Error(
                "Erro ao carregar consumo."
            );

        }

        const result =
            await response.json();

        tbody.innerHTML = "";

        if (
            !result.data ||
            result.data.length === 0
        ) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="2">
                        Nenhum histórico disponível.
                    </td>
                </tr>
            `;

            return;
        }

        result.data.forEach(item => {

            const row =
                document.createElement("tr");

            const mes =
                String(item.mes)
                    .padStart(2, "0");

            row.innerHTML = `
                <td>
                    ${mes}/${item.ano} - 
                </td>

                <td>
                    ${Number(item.consumo)
                        .toLocaleString(
                            "pt-BR",
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }
                        )}
                    m³
                </td>
            `;

            tbody.appendChild(row);

        });

    } catch (error) {

        console.error(
            "Erro no consumo mensal:",
            error
        );

        tbody.innerHTML = `
            <tr>
                <td colspan="2">
                    Erro ao carregar histórico.
                </td>
            </tr>
        `;
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadMonthlyConsumption();

    }
);