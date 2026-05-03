import { renderChart } from "../shared/charts.js";
import { attachWhatIfPanels } from "../shared/whatif.js";

export function renderMarkdown(text) {
    if (typeof marked === "undefined") return text;
    return marked.parse(text, { breaks: true, gfm: true });
}

export function showResults(title) {
    document.getElementById("results-section").classList.remove("hidden");
    document.getElementById("results-title").textContent = title;
    const content = document.getElementById("results-content");
    content.innerHTML = "";
    content.classList.remove("markdown-rendered");
    const chartContainer = document.getElementById("charts-container");
    if (chartContainer) chartContainer.innerHTML = "";
    document.getElementById("loading").classList.remove("hidden");
    setButtonsDisabled(true);
}

export function hideLoading() {
    document.getElementById("loading").classList.add("hidden");
    setButtonsDisabled(false);
}

export function setButtonsDisabled(disabled) {
    document.querySelectorAll(".btn").forEach(btn => btn.disabled = disabled);
}

export function showError(message) {
    hideLoading();
    const content = document.getElementById("results-content");
    content.innerHTML = `<div class="error-message">${message}</div>`;
}

export function renderResultContent(text) {
    const el = document.getElementById("results-content");
    el.innerHTML = renderMarkdown(text);
    el.classList.add("markdown-rendered");
}

export function renderCharts(charts) {
    if (!charts || charts.length === 0) return;
    const container = document.getElementById("charts-container");
    if (!container) return;
    container.innerHTML = "";
    const instances = [];
    for (const chart of charts) {
        instances.push(renderChart(container, chart));
    }
    attachWhatIfPanels(container, instances, charts);
}

export function clearResults() {
    document.getElementById("results-section").classList.add("hidden");
    document.getElementById("results-content").innerHTML = "";
    const chartContainer = document.getElementById("charts-container");
    if (chartContainer) chartContainer.innerHTML = "";
}
