import { getProfile } from "./profile.js";
import { showResults, hideLoading, showError, renderResultContent, renderCharts, clearResults } from "./results.js";

async function postJSON(endpoint, body) {
    const response = await fetch(`/api/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error ? JSON.stringify(err.error) : "Request failed");
    }
    return response.json();
}

async function getRecommendations() {
    showResults("Financial Recommendations");
    try {
        const data = await postJSON("recommendations", getProfile());
        renderResultContent(data.advice);
        renderCharts(data.charts);
    } catch (e) {
        showError(e.message);
    } finally {
        hideLoading();
    }
}

async function getInvestmentInsights() {
    showResults("Investment Insights");
    try {
        const data = await postJSON("investment-insights", getProfile());
        renderResultContent(data.advice);
        renderCharts(data.charts);
    } catch (e) {
        showError(e.message);
    } finally {
        hideLoading();
    }
}

async function getFinancialPlan() {
    showResults("Financial Plan");
    try {
        const data = await postJSON("financial-plan", getProfile());
        renderResultContent(data.advice);
        renderCharts(data.charts);
    } catch (e) {
        showError(e.message);
    } finally {
        hideLoading();
    }
}

async function streamFinancialPlan() {
    showResults("Financial Plan (Streaming)");
    const content = document.getElementById("results-content");

    try {
        const response = await fetch("/api/financial-plan/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getProfile()),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error ? JSON.stringify(err.error) : "Request failed");
        }

        hideLoading();
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const payload = line.slice(6).trim();
                    if (payload === "[DONE]") break;
                    try {
                        const parsed = JSON.parse(payload);
                        fullText += parsed.token;
                        content.textContent = fullText;
                        content.scrollTop = content.scrollHeight;
                    } catch {}
                }
            }
        }

        renderResultContent(fullText);
    } catch (e) {
        showError(e.message);
    }
}

async function askQuestion() {
    const question = document.getElementById("custom-question").value.trim();
    if (!question) return;

    showResults("Custom Question");
    try {
        const body = getProfile();
        body.question = question;
        const data = await postJSON("ask", body);
        renderResultContent(data.advice);
        renderCharts(data.charts);
    } catch (e) {
        showError(e.message);
    } finally {
        hideLoading();
    }
}

document.getElementById("btn-recommendations").addEventListener("click", getRecommendations);
document.getElementById("btn-insights").addEventListener("click", getInvestmentInsights);
document.getElementById("btn-plan").addEventListener("click", getFinancialPlan);
document.getElementById("btn-stream").addEventListener("click", streamFinancialPlan);
document.getElementById("btn-ask").addEventListener("click", askQuestion);
document.getElementById("btn-clear").addEventListener("click", clearResults);
document.getElementById("custom-question").addEventListener("keydown", e => {
    if (e.key === "Enter") askQuestion();
});
