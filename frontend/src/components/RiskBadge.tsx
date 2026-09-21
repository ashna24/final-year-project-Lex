import type { RiskLevel } from "../types";

const LABELS: Record<RiskLevel, string> = {
  High: "High risk",
  Medium: "Medium risk",
  Low: "Low risk",
  Error: "Analysis error",
};

interface RiskBadgeProps {
  level: RiskLevel;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  return <span className={`risk-badge risk-badge--${level.toLowerCase()}`}>{LABELS[level]}</span>;
}

export function SkippedBadge() {
  return <span className="risk-badge risk-badge--skipped">Not analysed</span>;
}
