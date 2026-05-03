export function parseSSE(buffer) {
    const blocks = buffer.split("\n\n");
    const remainder = blocks.pop();
    const events = [];
    for (const block of blocks) {
        if (!block.trim()) continue;
        let eventType = "message";
        let data = "";
        for (const line of block.split("\n")) {
            if (line.startsWith("event: ")) eventType = line.slice(7).trim();
            else if (line.startsWith("data: ")) data += line.slice(6);
        }
        if (data) {
            try { events.push({ type: eventType, data: JSON.parse(data) }); }
            catch { events.push({ type: eventType, data: { content: data } }); }
        }
    }
    return { events, remainder };
}
