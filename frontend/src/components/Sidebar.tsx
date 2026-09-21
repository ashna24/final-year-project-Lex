const STEPS = [
  "You upload a photo or file of the contract.",
  "Lex splits it into clauses and reads each one. This takes about a minute and a half.",
  "You get a plain-English or Urdu explanation of every clause, with a note on which ones need care.",
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <p className="eyebrow">How it works</p>
      <ol className="sidebar__steps">
        {STEPS.map((step, index) => (
          <li key={step} className="sidebar__step">
            <span className="sidebar__step-number" aria-hidden="true">
              {String(index + 1).padStart(2, "0")}
            </span>
            <span className="sidebar__step-text">{step}</span>
          </li>
        ))}
      </ol>
      <hr className="sidebar__rule" />
      <p className="sidebar__privacy">
        Your document is analysed and then deleted. It is not shared with anyone and is not used to
        train models.
      </p>
    </aside>
  );
}
