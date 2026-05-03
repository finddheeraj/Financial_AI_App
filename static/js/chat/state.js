export let sessionId = null;
export let profileSent = false;
export let sending = false;

export function setSessionId(id) { sessionId = id; }
export function setProfileSent(val) { profileSent = val; }
export function setSending(val) { sending = val; }
