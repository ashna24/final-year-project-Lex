import { useEffect, useState } from "react";
import type { ClauseResult, Language } from "../types";
import { isSkipped } from "../types";
import { RiskBadge, SkippedBadge } from "./RiskBadge";
import { confidencePipCount } from "../lib/confidence";
import { queueTranslation } from "../lib/translationQueue";

interface ClauseCardProps {
  clause: ClauseResult;
  index: number;
  language: Language;
}

function ConfidencePips({ confidence }: { confidence: number }) {
  const filled = confidencePipCount(confidence);
  return (
    <span className="clause-card__confidence">
      <span className="clause-card__confidence-label">Confidence {confidence}%</span>
      <span className="clause-card__pips" aria-hidden="true">
        {[0, 1, 2, 3].map((i) => (
          <span key={i} className={`clause-card__pip${i < filled ? " clause-card__pip--on" : ""}`} />
        ))}
      </span>
    </span>
  );
}

// Gets Urdu on demand when the language needs it and the clause has none yet
function useUrduExplanation(explanation: string, explanationUrdu: string | null | undefined, needed: boolean) {
  const [fetched, setFetched] = useState<string | null>(null);
  const [state, setState] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    if (!needed || explanationUrdu || fetched || state === "loading") return;
    let cancelled = false;
    // eslint-disable-next-line react/set-state-in-effect -- starts the fetch as soon as it is needed
    setState("loading");
    queueTranslation(explanation)
      .then((translation) => {
        if (!cancelled) {
          setFetched(translation);
          setState("idle");
        }
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- fetched and state are only read as a guard here
  }, [needed, explanationUrdu, explanation]);

  return { text: explanationUrdu ?? fetched, state };
}

export function ClauseCard({ clause, index, language }: ClauseCardProps) {
  const kicker = `Clause ${index + 1}`;
  const skipped = isSkipped(clause);

  const wantsUrdu = language === "both" || language === "ur";
  const showEnglish = language === "en" || language === "both";
  const isError = !skipped && clause.risk_level === "Error";

  // Hooks cannot be skipped so this runs for skipped clauses too but fetches nothing
  const urdu = useUrduExplanation(
    skipped ? "" : clause.explanation,
    skipped ? null : clause.explanation_urdu,
    !skipped && wantsUrdu && !isError,
  );

  if (skipped) {
    return (
      <article className="clause-card" data-risk="skipped">
        <div className="clause-card__meta">
          <SkippedBadge />
          <span className="clause-card__kicker">{kicker}</span>
        </div>
        <p className="clause-card__section-label">Original wording</p>
        <h3 className="clause-card__title">{clause.clause_text}</h3>
        <p className="clause-card__section-label">Explanation</p>
        <p className="clause-card__explanation">{clause.reason}</p>
      </article>
    );
  }

  return (
    <article className="clause-card" data-risk={clause.risk_level.toLowerCase()}>
      <div className="clause-card__meta">
        <RiskBadge level={clause.risk_level} />
        <span className="clause-card__kicker">{kicker}</span>
        {!isError && (
          <div className="clause-card__meta-right">
            <ConfidencePips confidence={clause.confidence_score} />
          </div>
        )}
        {isError && <span className="clause-card__meta-right clause-card__no-score">No score</span>}
      </div>

      <p className="clause-card__section-label">Original wording</p>
      <h3 className="clause-card__title">{clause.clause_text}</h3>

      {showEnglish && (
        <>
          <p className="clause-card__section-label">Explanation</p>
          <p className="clause-card__explanation">{clause.explanation}</p>
        </>
      )}

      {wantsUrdu && !isError && (
        <div className="clause-card__urdu-block">
          <div className="clause-card__urdu-header">
            <span className="clause-card__urdu-kicker">اردو · Urdu</span>
            <span className="clause-card__urdu-direction">Right to left</span>
          </div>
          {urdu.state === "loading" && <p className="clause-card__urdu-status">Translating…</p>}
          {urdu.state === "error" && (
            <p className="clause-card__urdu-status clause-card__urdu-status--error" role="alert">
              Couldn't translate this clause. Try again shortly.
            </p>
          )}
          {urdu.text && (
            <p className="clause-card__explanation clause-card__explanation--urdu" dir="rtl" lang="ur">
              {urdu.text}
            </p>
          )}
        </div>
      )}
    </article>
  );
}
