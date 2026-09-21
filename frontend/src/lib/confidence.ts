// Maps 75 to 100 percent onto 4 pips since scores are usually high
export function confidencePipCount(confidence: number): number {
  const raw = Math.ceil((confidence - 75) / 6.25);
  return Math.max(1, Math.min(4, raw));
}
