export function Disclaimer() {
  return (
    <div className="disclaimer" role="note">
      <div className="disclaimer__bar" aria-hidden="true" />
      <div className="disclaimer__content">
        <p className="disclaimer__eyebrow">Please read</p>
        <p className="disclaimer__body">
          This is an AI-generated analysis and does not constitute legal advice.
          Please consult a qualified lawyer for important decisions.
        </p>
      </div>
    </div>
  );
}
