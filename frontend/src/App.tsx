import { Link, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink-700/60">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-accent-500 to-good" />
            <div className="leading-tight">
              <div className="font-semibold tracking-tight">Frontal Harmony</div>
              <div className="text-xs text-ink-300">facial proportion analysis</div>
            </div>
          </Link>
          <a
            href="https://github.com/"
            className="text-xs text-ink-300 hover:text-ink-100"
            target="_blank"
            rel="noreferrer"
          >
            stateless &middot; ephemeral &middot; no auth
          </a>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </main>

      <footer className="border-t border-ink-700/60">
        <div className="max-w-6xl mx-auto px-6 py-4 text-xs text-ink-300">
          Image bytes are processed in-memory and discarded after the response is built. No
          database, no logging of pixel data.
        </div>
      </footer>
    </div>
  );
}
