let pressureChart = null;
let productPressureChart = null;
let purityChart = null;
let flowChart = null;
let accumulatedChart = null;
let purityProductPressureChart = null;
let dewPointChart = null;
/* =========================================================
URL DA API
========================================================= */
console.log(
"telemetry_history.js CARREGADO"
);
document.addEventListener
/* =========================================================
PERÍODO
========================================================= */

function getPeriod() {

const period =
    document.getElementById(
        "periodSelect"
    ).value;

const end = new Date();

const start = new Date();

if (period === "24h") {

    start.setHours(
        start.getHours() - 24
    );

} else if (period === "7d") {

    start.setDate(
        start.getDate() - 7
    );

} else if (period === "30d") {

    start.setDate(
        start.getDate() - 30
    );

}

return {
    start: start.toISOString(),
    end: end.toISOString()
};

}

/* =========================================================
DESTRUIR GRÁFICO
========================================================= */

function destroyChart(chart, canvasId) {

/*
 * Primeiro tenta destruir pela referência.
 */

if (chart) {

    try {

        chart.destroy();

    } catch (error) {

        console.warn(
            "Erro ao destruir gráfico:",
            error
        );

    }
}


/*
 * Depois verifica se o Canvas ainda possui
 * uma instância do Chart.js.
 */

const canvas =
    document.getElementById(
        canvasId
    );

if (!canvas) {
    return null;
}


const existingChart =
    Chart.getChart(canvas);

if (existingChart) {

    console.log(
        `Destruindo gráfico existente: ${canvasId}`
    );

    existingChart.destroy();
}

return null;

}

/* =========================================================
CARREGAR HISTÓRICO
========================================================= */

async function loadHistory() {

    const button = document.getElementById("loadHistory");
    const buttonText = document.getElementById("loadHistoryText");
    const spinner = document.getElementById("loadHistorySpinner");

    // Ativa carregamento
    button.disabled = true;
    buttonText.textContent = "Carregando...";
    spinner.style.display = "inline-block";

const hospital =
    document.getElementById(
        "hospitalSelect"
    ).value;


if (!hospital) {

    alert(
        "Selecione um hospital."
    );

    return;
}


const period =
    getPeriod();


const params =
    new URLSearchParams({

        hospital: hospital,

        start: period.start,

        end: period.end

    });


const url =
    `${TELEMETRY_HISTORY_URL}?${params}`;


console.log(
    "Consultando:",
    url
);


try {

    const response =
        await fetch(url);


    console.log(
        "Status da API:",
        response.status
    );


    if (!response.ok) {

        let errorMessage =
            "Erro ao carregar histórico.";

        try {

            const error =
                await response.json();

            errorMessage =
                error.error ||
                errorMessage;

        } catch (e) {
            // ignora erro ao interpretar JSON
        }

        throw new Error(
            errorMessage
        );
    }


    const result =
        await response.json();


    console.log(
        "Hospital:",
        result.hospital
    );


    console.log(
        "Quantidade de registros:",
        result.data.length
    );


    console.log(
        "Primeiro registro:",
        result.data[0]
    );


    if (
        !result.data ||
        result.data.length === 0
    ) {

        alert(
            "Não existem dados históricos para o período selecionado."
        );

        return;
    }


    renderCharts(
        result.data
    );


} catch (error) {

    console.error(
        "Erro no histórico:",
        error
    );

    alert(
        error.message
    );

} finally {

    // Desativa carregamento
    button.disabled = false;
    buttonText.textContent = "Atualizar";
    spinner.style.display = "none";
}

}

/* =========================================================
RENDERIZAR GRÁFICOS
========================================================= */

function renderCharts(data) {

console.log(
    "Renderizando gráficos:",
    data.length,
    "registros"
);


/*
 * Destrói qualquer gráfico anterior.
 */

pressureChart =
    destroyChart(
        pressureChart,
        "pressureChart"
    );


productPressureChart =
    destroyChart(
        productPressureChart,
        "productPressureChart"
    );


purityChart =
    destroyChart(
        purityChart,
        "purityChart"
    );


flowChart =
    destroyChart(
        flowChart,
        "flowChart"
    );

accumulatedChart =
    destroyChart(
        accumulatedChart,
        "accumulatedChart"
    );

dewPointChart =
    destroyChart(
        dewPointChart,
        "dewPointChart"
    );

purityProductPressureChart =
    destroyChart(
        purityProductPressureChart,
        "purityProductPressureChart"
    );
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
 * Dados
 */

const pressure =
    data.map(
        item =>
            item.pressure
    );


const productPressure =
    data.map(
        item =>
            item.product_pressure
    );


const purity =
    data.map(
        item =>
            item.purity
    );


const flow =
    data.map(
        item =>
            item.flow
    );


/*
 * Criar gráficos
 */

pressureChart =
    createChart(
        "pressureChart",
        labels,
        pressure,
        "Pressão (bar)"
    );


productPressureChart =
    createChart(
        "productPressureChart",
        labels,
        productPressure,
        "Pressão Produto (bar)"
    );


purityChart =
    createChart(
        "purityChart",
        labels,
        purity,
        "Pureza (%)"
    );


flowChart =
    createChart(
        "flowChart",
        labels,
        flow,
        "Fluxo"
    );

accumulatedChart =
    createChart(
        "accumulatedChart",
        labels,
        data.map(
            item => item.accumulated
        ),
        "Acumulado (m³)"
    );

dewPointChart =
    createChart(
        "dewPointChart",
        labels,
        data.map(
            item => item.dew_point
        ),
        "Ponto de Orvalho (°c)"
    );

purityProductPressureChart =
    createCombinedChart(
        "purityProductPressureChart",
        labels,
        productPressure,
        purity
    );
}


/* =========================================================
CRIAR GRÁFICO
========================================================= */

function createChart(
canvasId,
labels,
data,
label
) {

const canvas =
    document.getElementById(
        canvasId
    );


if (!canvas) {

    console.error(
        `Canvas não encontrado: ${canvasId}`
    );

    return null;
}


/*
 * Segurança adicional:
 *
 * se já existir qualquer gráfico associado
 * a esse Canvas, destrói antes de criar outro.
 */

const existingChart =
    Chart.getChart(canvas);


if (existingChart) {

    console.log(
        `Removendo gráfico existente: ${canvasId}`
    );

    existingChart.destroy();
}


return new Chart(
    canvas,
    {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {

                    label: label,

                    data: data,

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

                        callback: function(value, index) {

                            const date =
                                labels[index];

                            if (!date) {
                                return "";
                            }

                            return date.toLocaleString(
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

                    beginAtZero: false

                }

            },

            plugins: {

                legend: {

                    display: true

                },

                tooltip: {

                    callbacks: {

                        title: function(
                            tooltipItems
                        ) {

                            if (
                                !tooltipItems.length
                            ) {
                                return "";
                            }

                            const index =
                                tooltipItems[0].dataIndex;

                            const date =
                                labels[index];

                            return date.toLocaleString(
                                "pt-BR"
                            );
                        }

                    }

                }

            }

        }

    }
);

}

/* =========================================================
EVENTOS
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "DOM carregado."
        );


        /* =====================================================
           BOTÃO ATUALIZAR
        ===================================================== */

        const button =
            document.getElementById(
                "loadHistory"
            );


        console.log(
            "Botão encontrado:",
            button
        );


        if (!button) {

            console.error(
                "Botão #loadHistory não encontrado."
            );

            return;
        }


        button.addEventListener(
            "click",
            () => {

                console.log(
                    "BOTÃO ATUALIZAR CLICADO"
                );

                loadHistory();

            }
        );


        /* =====================================================
           PESQUISA DE HOSPITAL
        ===================================================== */

        const hospitalSearch =
            document.getElementById(
                "hospitalSearch"
            );


        const hospitalSelect =
            document.getElementById(
                "hospitalSelect"
            );


        if (
            hospitalSearch &&
            hospitalSelect
        ) {

            hospitalSearch.addEventListener(
                "input",
                function () {

                    const search =
                        this.value
                            .toLowerCase()
                            .trim();


                    const options =
                        hospitalSelect.querySelectorAll(
                            "option"
                        );


                    options.forEach(
                        option => {

                            /*
                             * Mantém a opção
                             * "Selecione um hospital"
                             */

                            if (!option.value) {
                                return;
                            }


                            const name =
                                option.textContent
                                    .toLowerCase()
                                    .trim();


                            option.hidden =
                                search !== "" &&
                                !name.includes(search);

                        }
                    );


                    /*
                     * Se o hospital atualmente selecionado
                     * não corresponde à pesquisa,
                     * limpa a seleção.
                     */

                    const selectedOption =
                        hospitalSelect.options[
                            hospitalSelect.selectedIndex
                        ];


                    if (
                        selectedOption &&
                        selectedOption.value &&
                        search !== "" &&
                        !selectedOption.textContent
                            .toLowerCase()
                            .includes(search)
                    ) {

                        hospitalSelect.value = "";

                    }

                }
            );

        }

    }
);



// criação do grafico combinado

function createCombinedChart(
    canvasId,
    labels,
    productPressure,
    purity
) {

    const canvas =
        document.getElementById(
            canvasId
        );


    if (!canvas) {

        console.error(
            `Canvas não encontrado: ${canvasId}`
        );

        return null;
    }


    /*
     * Segurança contra duplicação
     */

    const existingChart =
        Chart.getChart(canvas);


    if (existingChart) {

        existingChart.destroy();
    }


    return new Chart(
        canvas,
        {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {
                        label: "Pressão do Produto",

                        data: productPressure,

                        yAxisID: "yPressure",

                        tension: 0.25,

                        pointRadius: 0,

                        pointHoverRadius: 5,

                        borderWidth: 2,

                        spanGaps: true
                    },

                    {
                        label: "Pureza",

                        data: purity,

                        yAxisID: "yPurity",

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


                                    const period =
                                        document
                                            .getElementById(
                                                "periodSelect"
                                            )
                                            .value;


                                    if (
                                        period === "24h"
                                    ) {

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


                                    return date
                                        .toLocaleDateString(
                                            "pt-BR",
                                            {
                                                day: "2-digit",
                                                month: "2-digit"
                                            }
                                        );
                                }

                        }

                    },


                    /*
                     * Eixo da pressão
                     */

                    yPressure: {

                        type: "linear",

                        position: "left",

                        beginAtZero: false,

                        title: {

                            display: true,

                            text:
                                "Pressão do Produto (bar)"

                        }

                    },


                    /*
                     * Eixo da pureza
                     */

                    yPurity: {

                        type: "linear",

                        position: "right",

                        beginAtZero: false,

                        title: {

                            display: true,

                            text:
                                "Pureza (%)"

                        },


                        /*
                         * Evita que a grade do segundo eixo
                         * fique sobreposta à primeira.
                         */

                        grid: {

                            drawOnChartArea: false

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
                                }

                        }

                    }

                }

            }

        }
    );
}