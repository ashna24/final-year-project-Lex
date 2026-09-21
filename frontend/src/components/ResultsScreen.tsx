import type { ClauseResult, Language } from "../types";
import { LanguageSwitch } from "./LanguageSwitch";
import { SummaryStrip } from "./SummaryStrip";
import { ClauseCard } from "./ClauseCard";
import { countByRisk, orientationSentence, sortedByRisk } from "../lib/riskSummary";

interface ResultsScreenProps {
  documentName: string;
  results: ClauseResult[];
  language: Language;
  onLanguageChange: (language: Language) => void;
  onAnalyseAnother: () => void;
}

export function ResultsScreen({
  documentName,
  results,
  language,
  onLanguageChange,
  onAnalyseAnother,
}: ResultsScreenProps) {
  const counts = countByRisk(results);
  const ordered = sortedByRisk(results);

  return (
    <div className="results-screen">
      <div className="results-header">
        <div className="results-header__left">
          <p className="eyebrow">Analysis complete</p>
          <h2 className="screen-h1 screen-h1--results">
            {documentName} — {results.length} clause{results.length === 1 ? "" : "s"}
          </h2>
          <p className="results-header__orientation">{orientationSentence(counts)}</p>
        </div>
        <div className="results-header__right">
          <p className="eyebrow">Explanation language</p>
          <LanguageSwitch value={language} onChange={onLanguageChange} />
        </div>
      </div>

      <SummaryStrip high={counts.high} medium={counts.medium} low={counts.low} notAnalysed={counts.notAnalysed} />

      {ordered.length === 0 ? (
        <p className="results-screen__empty">No clauses were found in this document. Try a clearer image.</p>
      ) : (
        <div className="clause-grid">
          {ordered.map(({ clause, originalIndex }) => (
            <ClauseCard key={originalIndex} clause={clause} index={originalIndex} language={language} />
          ))}
        </div>
      )}

      <div className="results-footer">
        <p className="results-footer__note">
          If anything here worries you, take the original document to a solicitor or a free advice
          service before you sign. Lex can be wrong.
        </p>
        <button type="button" className="btn btn--secondary results-footer__action" onClick={onAnalyseAnother}>
          Analyse another document
        </button>
      </div>
    </div>
  );
}
