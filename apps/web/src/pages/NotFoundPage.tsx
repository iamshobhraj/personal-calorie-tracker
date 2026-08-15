import { Link } from "react-router-dom";

export function NotFoundPage(): React.JSX.Element {
  return (
    <main className="page-shell" aria-labelledby="not-found-title">
      <section className="setup-card">
        <p className="eyebrow">404</p>
        <h1 id="not-found-title">Page not found</h1>
        <p>The requested page is not available in this application shell.</p>
        <Link to="/">Return to setup</Link>
      </section>
    </main>
  );
}
