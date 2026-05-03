export function renderMarkdown(text) {
    if (typeof marked === "undefined") return text;
    return marked.parse(text, { breaks: true, gfm: true });
}
