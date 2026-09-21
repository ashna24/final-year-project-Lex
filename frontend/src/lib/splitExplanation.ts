// The design wants a short title and a body so the first sentence becomes the title
// If there is no clean break the whole text is the title and there is no body
const SENTENCE_BREAK = /^(.{10,140}?[.!?])\s+(.+)$/s;

export function splitExplanation(explanation: string): { title: string; body: string | null } {
  const match = SENTENCE_BREAK.exec(explanation.trim());
  if (match) {
    return { title: match[1], body: match[2] };
  }
  return { title: explanation.trim(), body: null };
}
