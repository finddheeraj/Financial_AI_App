import { sessionId, sending, setSessionId, setSending, profileSent, setProfileSent } from "./state.js";
import { getProfile } from "./profile.js";
import { parseSSE } from "./sse.js";
import {
    appendUserMessage, createAgentTurn, removeTyping,
    appendThought, appendToolCall, appendToolResult,
    appendAnswer, appendError,
} from "./messages.js";

const chatInput = document.getElementById("chat-input");
const btnSend = document.getElementById("btn-send");
const sidebar = document.getElementById("sidebar");

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || sending) return;

    setSending(true);
    btnSend.disabled = true;
    chatInput.value = "";
    appendUserMessage(message);

    const body = { message, session_id: sessionId };
    if (!profileSent) {
        body.profile = getProfile();
        setProfileSent(true);
    }

    const turnEl = createAgentTurn();

    try {
        const response = await fetch("/api/agent/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const err = await response.json();
            appendError(turnEl, err.error || "Request failed");
            removeTyping(turnEl);
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const result = parseSSE(buffer);
            buffer = result.remainder;

            for (const event of result.events) {
                const content = event.data.content;
                switch (event.type) {
                    case "session":
                        setSessionId(event.data.session_id);
                        break;
                    case "thought":
                        appendThought(turnEl, content);
                        break;
                    case "tool_call":
                        appendToolCall(turnEl, content);
                        break;
                    case "tool_result":
                        appendToolResult(turnEl, content);
                        break;
                    case "answer":
                        appendAnswer(turnEl, content);
                        break;
                    case "error":
                        appendError(turnEl, content);
                        break;
                    case "done":
                        removeTyping(turnEl);
                        break;
                }
            }
        }
    } catch (e) {
        appendError(turnEl, "Connection error: " + e.message);
    } finally {
        removeTyping(turnEl);
        setSending(false);
        btnSend.disabled = false;
        chatInput.focus();
    }
}

btnSend.addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById("toggle-sidebar").addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
});

document.getElementById("mobile-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
});

document.getElementById("profile-form").addEventListener("change", () => {
    setProfileSent(false);
});
