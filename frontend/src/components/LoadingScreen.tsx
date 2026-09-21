import { useSimulatedProgress } from "../lib/useSimulatedProgress";

const STAGE_HEADLINES = [
  "Reading your document…",
  "Finding the clauses…",
  "Analysing clauses…",
  "Almost done…",
];

const STEPS = [
  "Reading your document",
  "Finding the clauses",
  "Analysing clauses",
  "Writing plain-English explanations",
];

interface LoadingScreenProps {
  fileName: string;
  onCancel: () => void;
}

export function LoadingScreen({ fileName, onCancel }: LoadingScreenProps) {
  const { pct, stage, elapsed, stalled } = useSimulatedProgress();
  const remaining = Math.max(75 - elapsed, 5);

  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <p className="eyebrow">Analysing</p>
      <h2 className="screen-h1 screen-h1--loading">{STAGE_HEADLINES[stage]}</h2>
      <p className="loading-screen__meta">
        {fileName} · {stalled ? "still working — this one is taking longer than usual." : "this usually takes 60 to 90 seconds. You can leave this tab open."}
      </p>

      <div
        className="progress-bar"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="progress-bar__fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="loading-screen__progress-meta">
        <span>{pct}% complete</span>
        <span>
          {elapsed}s elapsed{!stalled && ` · about ${remaining}s to go`}
        </span>
      </div>

      <ol className="step-checklist">
        {STEPS.map((label, index) => {
          const isDone = index < stage;
          const isActive = index === stage;
          return (
            <li
              key={label}
              className={`step-checklist__row${!isDone && !isActive ? " step-checklist__row--pending" : ""}`}
            >
              <span className={`step-checklist__marker${isActive ? " step-checklist__marker--active" : ""}`} aria-hidden="true">
                {isDone ? "✓" : isActive ? "●" : "·"}
              </span>
              <span className={`step-checklist__label${isActive ? " step-checklist__label--active" : ""}`}>
                {label}
              </span>
              <span className="step-checklist__note">{isDone ? "done" : ""}</span>
            </li>
          );
        })}
      </ol>

      <div className="loading-screen__footer">
        <button type="button" className="btn btn--secondary" onClick={onCancel}>
          Cancel
        </button>
        <p className="loading-screen__reassurance">
          Nothing has been sent anywhere else. You can stop at any point.
        </p>
      </div>
    </div>
  );
}
