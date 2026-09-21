import type { ClauseResult } from "../types";
import { isSkipped } from "../types";

const RANK: Record<string, number> = { High: 0, Medium: 1, Low: 2, Error: 3 };

export interface RankedClause {
  clause: ClauseResult;
  // Position in the document starting at 0 so Clause N always means the Nth clause found
  // It does not change when the cards are sorted by risk
  originalIndex: number;
}

export function sortedByRisk(clauses: ClauseResult[]): RankedClause[] {
  return clauses
    .map((clause, originalIndex) => ({ clause, originalIndex }))
    .sort((a, b) => {
      const rankA = isSkipped(a.clause) ? 4 : RANK[a.clause.risk_level];
      const rankB = isSkipped(b.clause) ? 4 : RANK[b.clause.risk_level];
      return rankA - rankB || a.originalIndex - b.originalIndex;
    });
}

export interface RiskCounts {
  high: number;
  medium: number;
  low: number;
  notAnalysed: number;
}

export function countByRisk(clauses: ClauseResult[]): RiskCounts {
  const counts: RiskCounts = { high: 0, medium: 0, low: 0, notAnalysed: 0 };
  for (const clause of clauses) {
    if (isSkipped(clause) || clause.risk_level === "Error") {
      counts.notAnalysed += 1;
    } else if (clause.risk_level === "High") {
      counts.high += 1;
    } else if (clause.risk_level === "Medium") {
      counts.medium += 1;
    } else {
      counts.low += 1;
    }
  }
  return counts;
}

export function orientationSentence(counts: RiskCounts): string {
  const needCare = counts.high + counts.medium;
  if (needCare === 0) {
    return "Nothing here needs urgent attention. This looks like a fairly standard agreement.";
  }
  const clauseWord = needCare === 1 ? "clause needs" : "clauses need";
  return `${needCare} ${clauseWord} care before you sign. The rest look ordinary for this kind of agreement.`;
}
