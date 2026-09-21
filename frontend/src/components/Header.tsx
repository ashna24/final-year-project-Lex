interface HeaderProps {
  onNewDocument: () => void;
}

export function Header({ onNewDocument }: HeaderProps) {
  return (
    <header className="header">
      <div className="header__inner">
        <div className="header__logo-group">
          <h1 className="header__logo">Lex</h1>
          <span className="header__logo-dot" aria-hidden="true" />
        </div>
        <p className="header__tagline">Understand your contract before you sign it.</p>
        <button type="button" className="btn btn--secondary header__new-doc" onClick={onNewDocument}>
          New document
        </button>
      </div>
    </header>
  );
}
