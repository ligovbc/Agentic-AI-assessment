import logo from './ago_downloaded.png';

export function Header() {
  return (
    <header className="bc-header">
      <div className="header-content">
        <img src={logo} alt="BC Government Logo" className="header-logo" />
        <div className="header-text">
          <h1>Agentic AI Assessment</h1>
        </div>
      </div>
    </header>
  );
}
