import { useRef, useState } from "react";
import type { DragEvent } from "react";
import { FileUp } from "lucide-react";

interface DropZoneProps {
  onFile: (file: File) => void;
  onUseSample: () => void;
  onEmptyDrop: () => void;
  disabled: boolean;
}

export function DropZone({ onFile, onUseSample, onEmptyDrop, disabled }: DropZoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    if (!disabled) setDragging(true);
  }

  function handleDragLeave() {
    setDragging(false);
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    if (disabled) return;
    const file = event.dataTransfer.files?.[0];
    if (file) {
      onFile(file);
    } else {
      onEmptyDrop();
    }
  }

  return (
    <div
      className={`dropzone${dragging ? " dropzone--dragging" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <FileUp className="dropzone__icon" aria-hidden="true" size={40} strokeWidth={1.5} />
      <p className="dropzone__heading">Drag your document here</p>
      <p className="dropzone__hint">Photo or scan of a contract — JPG, PNG or PDF, up to 20 MB.</p>

      <div className="dropzone__actions">
        <button
          type="button"
          className="btn btn--primary"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          Choose file
        </button>
        <button type="button" className="btn btn--secondary" disabled={disabled} onClick={onUseSample}>
          Use the sample agreement
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        className="dropzone__input"
        aria-label="Choose a document file"
        accept="image/jpeg,image/png,application/pdf"
        disabled={disabled}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}
