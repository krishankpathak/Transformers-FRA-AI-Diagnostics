let chart;

function plotComparison(freq, mag) {

    const ctx = document.getElementById("fraChart");

    if (chart) chart.destroy();

    const healthy = mag.map((v, i) => v + Math.sin(i/10)*3);

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: freq,
            datasets: [
                {
                    label: "Measured FRA",
                    data: mag,
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "Reference",
                    data: healthy,
                    borderDash: [5,5],
                    tension: 0.3
                }
            ]
        }
    });
}