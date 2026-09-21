import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClauseCard } from "./ClauseCard";
import type { ClassifiedClause, SkippedClause } from "../types";
import { TranslateError } from "../api/translate";

vi.mock("../api/translate", async () => {
  const actual = await vi.importActual<typeof import("../api/translate")>("../api/translate");
  return { ...actual, translateClauseText: vi.fn() };
});

import { translateClauseText } from "../api/translate";

describe("ClauseCard", () => {
  it("renders the badge, kicker, confidence, and explanation for a classified clause in English mode", () => {
    const clause: ClassifiedClause = {
      clause_text: "The tenant shall pay rent on the first of each month.",
      risk_level: "Low",
      confidence_score: 92,
      explanation: "This just means rent is due monthly.",
    };
    render(<ClauseCard clause={clause} index={0} language="en" />);

    expect(screen.getByText(/low risk/i)).toBeInTheDocument();
    expect(screen.getByText("Clause 1")).toBeInTheDocument();
    expect(screen.getByText(/92%/)).toBeInTheDocument();
    expect(screen.getByText(clause.clause_text)).toBeInTheDocument();
  });

  it("renders a neutral skipped state with the reason, and no confidence UI", () => {
    const clause: SkippedClause = {
      clause_text: "Section 4",
      status: "skipped",
      reason: "insufficient content for classification",
    };
    render(<ClauseCard clause={clause} index={3} language="en" />);

    expect(screen.getByText(/not analysed/i)).toBeInTheDocument();
    expect(screen.getByText("insufficient content for classification")).toBeInTheDocument();
    expect(screen.queryByText(/confidence/i)).not.toBeInTheDocument();
  });

  it("shows 'No score' instead of confidence for a classifier Error clause, and never an Urdu block", () => {
    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "Error",
      confidence_score: 0,
      explanation: "Classification failed: could not connect to Ollama.",
    };
    render(<ClauseCard clause={clause} index={0} language="both" />);

    expect(screen.getByText("No score")).toBeInTheDocument();
    expect(screen.queryByText(/اردو/)).not.toBeInTheDocument();
    expect(translateClauseText).not.toHaveBeenCalled();
  });

  it("shows no Urdu block at all in English-only mode, even when explanation_urdu is present", () => {
    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "Medium",
      confidence_score: 70,
      explanation: "Plain English explanation.",
      explanation_urdu: "اردو وضاحت",
    };
    render(<ClauseCard clause={clause} index={0} language="en" />);

    expect(screen.queryByText("اردو وضاحت")).not.toBeInTheDocument();
    expect(translateClauseText).not.toHaveBeenCalled();
  });

  it("shows the already-present Urdu translation with no network call when language is 'both'", () => {
    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "Medium",
      confidence_score: 70,
      explanation: "Plain English explanation.",
      explanation_urdu: "اردو وضاحت",
    };
    render(<ClauseCard clause={clause} index={0} language="both" />);

    expect(screen.getByText("اردو وضاحت")).toBeInTheDocument();
    expect(translateClauseText).not.toHaveBeenCalled();
  });

  it("fetches a translation on demand when language requires Urdu but explanation_urdu is missing", async () => {
    let resolveTranslate: (value: string) => void;
    vi.mocked(translateClauseText).mockReturnValue(
      new Promise((resolve) => {
        resolveTranslate = resolve;
      }),
    );

    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "High",
      confidence_score: 88,
      explanation: "Plain English explanation.",
    };
    render(<ClauseCard clause={clause} index={0} language="ur" />);

    expect(screen.getByText("Translating…")).toBeInTheDocument();
    await waitFor(() => expect(translateClauseText).toHaveBeenCalledWith("Plain English explanation."));

    resolveTranslate!("ترجمہ شدہ متن");
    await waitFor(() => expect(screen.getByText("ترجمہ شدہ متن")).toBeInTheDocument());
  });

  it("treats a null explanation_urdu (upfront translation attempted but failed) as not-yet-fetched", async () => {
    vi.mocked(translateClauseText).mockResolvedValue("کامیاب ترجمہ");

    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "High",
      confidence_score: 88,
      explanation: "Plain English explanation.",
      explanation_urdu: null,
    };
    render(<ClauseCard clause={clause} index={0} language="both" />);

    await waitFor(() => expect(screen.getByText("کامیاب ترجمہ")).toBeInTheDocument());
    expect(translateClauseText).toHaveBeenCalledWith("Plain English explanation.");
  });

  it("shows an inline error near the Urdu block on fetch failure, without touching the rest of the card", async () => {
    vi.mocked(translateClauseText).mockRejectedValue(new TranslateError("Could not reach the Lex server."));

    const clause: ClassifiedClause = {
      clause_text: "Some clause.",
      risk_level: "Low",
      confidence_score: 95,
      explanation: "Plain English explanation.",
    };
    render(<ClauseCard clause={clause} index={0} language="ur" />);

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(screen.getByText(clause.clause_text)).toBeInTheDocument();
  });
});
