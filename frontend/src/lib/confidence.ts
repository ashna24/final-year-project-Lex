// Maps 50 to 100 percent onto 4 bars so anything at or below 50 shows 1 bar
export function confidencePipCount(confidence: number): number {
  const raw = Math.round((confidence - 50) / 12.5);
  return Math.max(1, Math.min(4, raw));
}
