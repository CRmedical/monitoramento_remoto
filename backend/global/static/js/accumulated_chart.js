let accumulatedChart = null;


async function loadAccumulatedHistory() {

    const canvas =
        document.getElementById("accumulatedChart");

    if (!canvas) {
        console.log(
            "Canvas accumulatedChart não encontrado."
        );
        return;
    }


    try {

        const response =
            await fetch(
                ACCUMULATED_HISTORY_URL
            );


        if (!response.ok) {

            throw new Error(
                "Erro ao carregar histórico do acumulado."
            );
        }


        const result =
            await response.json();


        console.log(
            "Histórico do acumulado:",
            result
        );


        if (
            !result.data ||
            result.data.length === 0
        ) {

            console.log(
                "Não existem dados históricos de acumulado."
            );

            return;
        }


        renderAccumulatedChart(
            result.data
        );


    } catch (error) {

        console.error(
            "Erro no gráfico de acumulado:",
            error
        );

    }

}


function renderAccumulatedChart(data) {

    const canvas =
        document.getElementById(
            "accumulatedChart"
        );


    if (!canvas) {
        return;
    }


    /*
     * Destrói gráfico anterior
     */

    if (accumulatedChart) {

        accumulatedChart.destroy();

        accumulatedChart = null;
    }


    /*
     * Segurança adicional
     */

    const existingChart =
        Chart.getChart(canvas);


    if (existingChart) {

        existingChart.destroy();

    }


    /*
     * Labels
     */

    const labels =
        data.map(
            item =>
                new Date(
                    item.timestamp
                )
        );


    /*
     * Valores
     */

    const values =
        data.map(
            item =>
                item.accumulated
        );


    /*
     * Criação
     */

    accumulatedChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Fluxo Acumulado (m³)",

                            data: values,

                            tension: 0.25,

                            pointRadius: 0,

                            pointHoverRadius: 5,

                            borderWidth: 2,

                            spanGaps: true

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,


                    interaction: {

                        mode: "index",

                        intersect: false

                    },


                    scales: {

                        x: {

                            type: "category",

                            ticks: {

                                autoSkip: true,

                                maxTicksLimit: 8,

                                maxRotation: 0,

                                minRotation: 0,

                                callback:
                                    function(
                                        value,
                                        index
                                    ) {

                                        const date =
                                            labels[index];


                                        if (!date) {
                                            return "";
                                        }


                                        return date
                                            .toLocaleString(
                                                "pt-BR",
                                                {
                                                    day: "2-digit",
                                                    month: "2-digit",
                                                    hour: "2-digit",
                                                    minute: "2-digit"
                                                }
                                            );

                                    }

                            }

                        },


                        y: {

                            beginAtZero: false,

                            title: {

                                display: true,

                                text:
                                    "Acumulado (m³)"

                            }

                        }

                    },


                    plugins: {

                        legend: {

                            display: true,

                            position: "top"

                        },


                        tooltip: {

                            callbacks: {

                                title:
                                    function(
                                        tooltipItems
                                    ) {

                                        if (
                                            !tooltipItems.length
                                        ) {
                                            return "";
                                        }


                                        const index =
                                            tooltipItems[0]
                                                .dataIndex;


                                        const date =
                                            labels[index];


                                        return date
                                            .toLocaleString(
                                                "pt-BR"
                                            );

                                    },


                                label:
                                    function(
                                        context
                                    ) {

                                        const value =
                                            context.parsed.y;


                                        return (
                                            " Acumulado: " +
                                            Number(value)
                                                .toFixed(2) +
                                            " m³"
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

}


/*
 * Carrega quando a página estiver pronta
 */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAccumulatedHistory();

    }
);