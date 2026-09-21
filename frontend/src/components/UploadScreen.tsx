import { DropZone } from "./DropZone";
import { Sidebar } from "./Sidebar";
import { ErrorBlock } from "./ErrorBlock";
import type { ErrorKind } from "../types";
import type { FileProblem } from "../lib/fileValidation";

interface UploadScreenProps {
  onFile: (file: File) => void;
  onUseSample: () => void;
  onEmptyDrop: () => void;
  disabled: boolean;
  error: ErrorKind;
  fileProblem: FileProblem | null;
  onErrorPrimaryAction: () => void;
  onErrorDismiss: () => void;
}

export function UploadScreen({
  onFile,
  onUseSample,
  onEmptyDrop,
  disabled,
  error,
  fileProblem,
  onErrorPrimaryAction,
  onErrorDismiss,
}: UploadScreenProps) {
  return (
    <div className="upload-screen">
      <div className="upload-screen__main">
        <h2 className="screen-h1">Upload the document you were asked to sign.</h2>
        <p className="upload-screen__sub">
          A photo of the pages is fine. Lex reads it, and explains each one in plain English or Urdu.
        </p>
        <DropZone onFile={onFile} onUseSample={onUseSample} onEmptyDrop={onEmptyDrop} disabled={disabled} />
        {error && (
          <ErrorBlock
            kind={error}
            fileProblem={fileProblem}
            onPrimaryAction={onErrorPrimaryAction}
            onDismiss={onErrorDismiss}
          />
        )}
      </div>
      <Sidebar />
    </div>
  );
}
