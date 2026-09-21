export type RiskLevel = "High" | "Medium" | "Low" | "Error";

export interface ClassifiedClause {
  clause_text: string;
  risk_level: RiskLevel;
  confidence_score: number;
  explanation: string;
  explanation_urdu?: string | null;
}

export interface SkippedClause {
  clause_text: string;
  status: "skipped";
  reason: string;
}

export type ClauseResult = ClassifiedClause | SkippedClause;

export function isSkipped(clause: ClauseResult): clause is SkippedClause {
  return "status" in clause && clause.status === "skipped";
}

export type Screen = "upload" | "loading" | "results";

// One global switch that sets the language for every clause card
export type Language = "en" | "both" | "ur";

// null = no error shown. The other three map onto the three specified error blocks.
export type ErrorKind = "none" | "type" | "server" | null;
