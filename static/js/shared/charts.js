const DEFAULT_PALETTE = [
    "#00AEEF", "#00857C", "#003D6B", "#FF8042", "#FFBB28",
    "#8884D8", "#82CA9D", "#FFC658", "#A4DE6C", "#D0ED57",
];

const LINE_COLORS = ["#003D6B", "#00AEEF"];

export function formatINR(value) {
    if (value >= 1_00_00_000) return "₹" + (value / 1_00_00_000).toFixed(1) + "Cr";
    if (value >= 1_00_000) return "₹" + (value / 1_00_000).toFixed(1) + "L";
    if (value >= 1_000) return "₹" + (value / 1_000).toFixed(1) + "K";
    return "₹" + value;
}

export function extractChartData(text) {
    const re = /\[CHART_DATA\]([\s\S]*?)\[\/CHART_DATA\]/g;
    const charts = [];
    let match;
    while ((match = re.exec(text)) !== null) {
        try { charts.push(JSON.parse(match[1].trim())); } catch {}
    }
    const cleanText = text.replace(re, "").trim();
    return { cleanText, charts };
}

function buildChartConfig(chartData) {
    const colors = chartData.colors || DEFAULT_PALETTE.slice(0, chartData.labels.length);

    if (chartData.type === "pie") {
        return {
            type: "pie",
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.datasets[0].data,
                    backgroundColor: colors,
                    borderWidth: 1,
                    borderColor: "#fff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: { display: true, text: chartData.title, font: { size: 14, weight: "600" } },
                    legend: { position: "right", labels: { font: { size: 11 }, padding: 12 } },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                                return `${ctx.label}: ${formatINR(ctx.parsed)} (${pct}%)`;
                            },
                        },
                    },
                },
            },
        };
    }

    if (chartData.type === "bar") {
        return {
            type: "bar",
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.datasets[0].label || "",
                    data: chartData.datasets[0].data,
                    backgroundColor: colors,
                    borderWidth: 1,
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: chartData.title, font: { size: 14, weight: "600" } },
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => formatINR(ctx.parsed.y) } },
                },
                scales: {
                    y: { beginAtZero: true, ticks: { callback: v => formatINR(v) } },
                },
            },
        };
    }

    if (chartData.type === "line") {
        return {
            type: "line",
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets.map((ds, i) => ({
                    label: ds.label,
                    data: ds.data,
                    borderColor: LINE_COLORS[i % LINE_COLORS.length],
                    backgroundColor: LINE_COLORS[i % LINE_COLORS.length] + "20",
                    fill: i === 1,
                    tension: 0.3,
                    pointRadius: chartData.labels.length > 20 ? 0 : 3,
                })),
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: chartData.title, font: { size: 14, weight: "600" } },
                    tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${formatINR(ctx.parsed.y)}` } },
                },
                scales: {
                    y: { beginAtZero: true, ticks: { callback: v => formatINR(v) } },
                },
            },
        };
    }

    return { type: chartData.type, data: {}, options: {} };
}

export function renderChart(containerEl, chartData) {
    if (typeof Chart === "undefined") return null;
    const wrapper = document.createElement("div");
    wrapper.className = "chart-wrapper";
    const canvas = document.createElement("canvas");
    wrapper.appendChild(canvas);
    containerEl.appendChild(wrapper);
    return new Chart(canvas.getContext("2d"), buildChartConfig(chartData));
}
