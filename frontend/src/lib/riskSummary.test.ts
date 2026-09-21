import { describe, expect, it } from "vitest";
import { countByRisk, orientationSentence, sortedByRisk } from "./riskSummary";
import type { ClauseResult } from "../types";

const CLAUSES: ClauseResult[] = [
  { clause_text: "a", risk_level: "Low", confidence_score: 90, explanation: "a" },
  { clause_text: "b", status: "skipped", reason: "too short" },
  { clause_text: "c", risk_level: "High", confidence_score: 88, explanation: "c" },
  { clause_text: "d", risk_level: "Medium", confidence_score: 80, explanation: "d" },
  { clause_text: "e", risk_level: "Error", confidence_score: 0, explanation: "e" },
];

describe("countByRisk", () => {
  it("buckets skipped and Error clauses together as not analysed", () => {
    expect(countByRisk(CLAUSES)).toEqual({ high: 1, medium: 1, low: 1, notAnalysed: 2 });
  });
});

describe("sortedByRisk", () => {
  it("orders High, Medium, Low, Error, then skipped last, preserving original order within a tier", () => {
    const ordered = sortedByRisk(CLAUSES).map(({ clause }) => clause.clause_text);
    expect(ordered).toEqual(["c", "d", "a", "e", "b"]);
  });

  it("keeps each clause's original document position, independent of its display order", () => {
    const ordered = sortedByRisk(CLAUSES);
    // c is High and was the 3rd clause in the document but is shown first
    expect(ordered[0]).toEqual({ clause: CLAUSES[2], originalIndex: 2 });
    // b was skipped and was the 2nd clause in the document but is shown last
    expect(ordered[4]).toEqual({ clause: CLAUSES[1], originalIndex: 1 });
  });
});

describe("orientationSentence", () => {
  it("names the count of clauses needing care when there are any", () => {
    expect(orientationSentence({ high: 1, medium: 1, low: 3, notAnalysed: 0 })).toBe(
      "2 clauses need care before you sign. The rest look ordinary for this kind of agreement.",
    );
  });

  it("uses singular phrasing for exactly one", () => {
    expect(orientationSentence({ high: 1, medium: 0, low: 3, notAnalysed: 0 })).toBe(
      "1 clause needs care before you sign. The rest look ordinary for this kind of agreement.",
    );
  });

  it("gives reassuring copy when nothing needs care", () => {
    expect(orientationSentence({ high: 0, medium: 0, low: 5, notAnalysed: 0 })).toBe(
      "Nothing here needs urgent attention. This looks like a fairly standard agreement.",
    );
  });
});
