import { useRef, useState } from "react";
import { Header } from "./components/Header";
import { Disclaimer } from "./components/Disclaimer";
import { UploadScreen } from "./components/UploadScreen";
import { LoadingScreen } from "./components/LoadingScreen";
import { ResultsScreen } from "./components/ResultsScreen";
import { analyzeDocument } from "./api/analyze";
import { validateFile } from "./lib/fileValidation";
import type { FileProblem } from "./lib/fileValidation";
import type { ClauseResult, ErrorKind, Language, Screen } from "./types";
import "./App.css";

const LANGUAGE_STORAGE_KEY = "lex-language";
const SAMPLE_URL = "/sample-tenancy-agreement.jpg";
const SAMPLE_FILE_NAME = "sample-tenancy-agreement.jpg";

function loadStoredLanguage(): Language {
  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored === "en" || stored === "both" || stored === "ur") return stored;
  } catch {
    // Storage can be blocked so fall back to English
  }
  return "en";
}

function App() {
  const [screen, setScreen] = useState<Screen>("upload");
  const [language, setLanguageState] = useState<Language>(loadStoredLanguage);
  const [error, setError] = useState<ErrorKind>(null);
  const [fileProblem, setFileProblem] = useState<FileProblem | null>(null);
  const [documentName, setDocumentName] = useState("");
  const [results, setResults] = useState<ClauseResult[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  function setLanguage(next: Language) {
    setLanguageState(next);
    try {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, next);
    } catch {
      // Saving the language is optional so ignore failures
    }
  }

  function resetToUpload() {
    abortRef.current?.abort();
    setScreen("upload");
    setError(null);
    setFileProblem(null);
    setResults([]);
  }

  async function submit(file: File) {
    setError(null);
    setFileProblem(null);
    setDocumentName(file.name);
    setScreen("loading");

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      // Urdu is fetched later from the language switch so never ask for it here
      const data = await analyzeDocument(file, false, controller.signal);
      setResults(data);
      setScreen("results");
    } catch {
      if (controller.signal.aborted) return; // Cancel already returned to "upload"
      setError("server");
      setScreen("upload");
    }
  }

  function handleFile(file: File) {
    const problem = validateFile(file);
    if (problem) {
      setError("type");
      setFileProblem(problem);
      return;
    }
    setError(null);
    setFileProblem(null);
    void submit(file);
  }

  async function handleUseSample() {
    try {
      const response = await fetch(SAMPLE_URL);
      const blob = await response.blob();
      const file = new File([blob], SAMPLE_FILE_NAME, { type: blob.type || "image/jpeg" });
      void submit(file);
    } catch {
      setError("server");
    }
  }

  function handleCancel() {
    abortRef.current?.abort();
    setScreen("upload");
  }

  return (
    <div className="app">
      <Header onNewDocument={resetToUpload} />
      <Disclaimer />
      <main className="app__main">
        {screen === "upload" && (
          <UploadScreen
            onFile={handleFile}
            onUseSample={handleUseSample}
            onEmptyDrop={() => setError("none")}
            disabled={false}
            error={error}
            fileProblem={fileProblem}
            onErrorPrimaryAction={() => setError(null)}
            onErrorDismiss={() => setError(null)}
          />
        )}
        {screen === "loading" && <LoadingScreen fileName={documentName} onCancel={handleCancel} />}
        {screen === "results" && (
          <ResultsScreen
            documentName={documentName}
            results={results}
            language={language}
            onLanguageChange={setLanguage}
            onAnalyseAnother={resetToUpload}
          />
        )}
      </main>
    </div>
  );
}

export default App;
