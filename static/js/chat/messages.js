import { renderMarkdown } from "./markdown.js";
import { extractChartData, renderChart } from "./charts.js";

const messagesEl = document.getElementById("chat-messages");

export function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

export function appendUserMessage(text) {
    const div = document.createElement("div");
    div.className = "user-message";
    div.textContent = text;
    messagesEl.appendChild(div);
    scrollToBottom();
}

export function createAgentTurn() {
    const div = document.createElement("div");
    div.className = "agent-turn";
    const typing = document.createElement("div");
    typing.className = "typing-indicator";
    typing.innerHTML = "<span></span><span></span><span></span>";
    div.appendChild(typing);
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
}

export function removeTyping(turnEl) {
    const typing = turnEl.querySelector(".typing-indicator");
    if (typing) typing.remove();
}

export function appendThought(turnEl, content) {
    removeTyping(turnEl);
    const details = document.createElement("details");
    details.className = "step step-thought";
    const summary = document.createElement("summary");
    summary.textContent = "Thinking...";
    const body = document.createElement("div");
    body.className = "thought-content";
    body.textContent = content;
    details.appendChild(summary);
    details.appendChild(body);
    turnEl.appendChild(details);
    scrollToBottom();
}

export function appendToolCall(turnEl, content) {
    removeTyping(turnEl);
    let parsed;
    try { parsed = JSON.parse(content); } catch { parsed = { tool: content, input: {} }; }
    const details = document.createElement("details");
    details.className = "step step-tool";
    details.open = true;
    const summary = document.createElement("summary");
    summary.textContent = "Tool: " + parsed.tool;
    const inputDiv = document.createElement("div");
    inputDiv.className = "tool-input";
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(parsed.input, null, 2);
    inputDiv.appendChild(pre);
    details.appendChild(summary);
    details.appendChild(inputDiv);
    turnEl.appendChild(details);
    scrollToBottom();
}

export function appendToolResult(turnEl, content) {
    const tools = turnEl.querySelectorAll(".step-tool");
    const lastTool = tools[tools.length - 1];
    if (!lastTool) return;

    const { cleanText, charts } = extractChartData(content);

    const resultDiv = document.createElement("div");
    resultDiv.className = "tool-result";
    const label = document.createElement("div");
    label.className = "tool-result-label";
    label.textContent = "Result";
    const pre = document.createElement("pre");
    pre.textContent = cleanText;
    resultDiv.appendChild(label);
    resultDiv.appendChild(pre);

    for (const chart of charts) {
        renderChart(resultDiv, chart);
    }

    lastTool.appendChild(resultDiv);
    scrollToBottom();
}

export function appendAnswer(turnEl, content) {
    removeTyping(turnEl);
    const div = document.createElement("div");
    div.className = "step step-answer";
    div.innerHTML = renderMarkdown(content);
    turnEl.appendChild(div);
    scrollToBottom();
}

export function appendError(turnEl, content) {
    removeTyping(turnEl);
    const div = document.createElement("div");
    div.className = "step step-error";
    div.textContent = content;
    turnEl.appendChild(div);
    scrollToBottom();
}
