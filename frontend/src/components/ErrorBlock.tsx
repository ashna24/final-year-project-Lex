import { AlertCircle } from "lucide-react";
import type { ErrorKind } from "../types";
import type { FileProblem } from "../lib/fileValidation";

interface ErrorBlockProps {
  kind: Exclude<ErrorKind, null>;
  fileProblem?: FileProblem | null;
  onPrimaryAction: () => void;
  onDismiss: () => void;
}

function content(kind: Exclude<ErrorKind, null>, fileProblem: FileProblem | null | undefined) {
  switch (kind) {
    case "none":
      return {
        title: "No document chosen yet",
        body: "Nothing has been uploaded. Pick a photo or file of the contract and Lex will take it from there.",
        action: "Choose a file",
      };
    case "type": {
      if (fileProblem?.kind === "too-large") {
        return {
          title: "Lex can't read that kind of file",
          body: "That file is larger than the 20 MB limit. Lex works with photos, scans and PDFs of documents — JPG, PNG or PDF. A clear phone photo of each page works fine.",
          action: "Choose a different file",
        };
      }
      const named =
        fileProblem?.kind === "type" && fileProblem.description
          ? `That looks like a ${fileProblem.description}.`
          : "That doesn't look like a document Lex can read.";
      return {
        title: "Lex can't read that kind of file",
        body: `${named} Lex works with photos, scans and PDFs of documents — JPG, PNG or PDF. A clear phone photo of each page works fine.`,
        action: "Choose a different file",
      };
    }
    case "server":
      return {
        title: "Lex couldn't finish the analysis",
        body: "The connection dropped part-way through, so the results are incomplete. Your document is still on your device and nothing was lost. Trying again usually works.",
        action: "Try again",
      };
  }
}

export function ErrorBlock({ kind, fileProblem, onPrimaryAction, onDismiss }: ErrorBlockProps) {
  const { title, body, action } = content(kind, fileProblem);

  return (
    <div className="error-block" role="alert">
      <AlertCircle className="error-block__icon" aria-hidden="true" size={22} strokeWidth={1.8} />
      <div className="error-block__content">
        <p className="error-block__title">{title}</p>
        <p className="error-block__body">{body}</p>
        <div className="error-block__actions">
          <button type="button" className="btn btn--primary" onClick={onPrimaryAction}>
            {action}
          </button>
          <button type="button" className="btn btn--secondary" onClick={onDismiss}>
            Not now
          </button>
        </div>
      </div>
    </div>
  );
}
