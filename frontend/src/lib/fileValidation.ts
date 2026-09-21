export const ACCEPTED_TYPES = ["image/jpeg", "image/png", "application/pdf"];
export const MAX_SIZE_BYTES = 20 * 1024 * 1024;

const KIND_BY_EXTENSION: Record<string, string> = {
  csv: "spreadsheet",
  xls: "spreadsheet",
  xlsx: "spreadsheet",
  doc: "Word document",
  docx: "Word document",
  txt: "text file",
  zip: "zip archive",
  mp4: "video",
  mov: "video",
  avi: "video",
  mp3: "audio file",
  wav: "audio file",
  gif: "GIF image",
  heic: "HEIC photo",
  heif: "HEIC photo",
  webp: "WebP image",
};

// Friendly name for a rejected file so the error can say what it saw
export function describeFileKind(file: File): string | null {
  const extension = file.name.split(".").pop()?.toLowerCase();
  if (extension && KIND_BY_EXTENSION[extension]) {
    return KIND_BY_EXTENSION[extension];
  }
  return null;
}

export type FileProblem = { kind: "type"; description: string | null } | { kind: "too-large" };

// null = the file is fine to submit.
export function validateFile(file: File): FileProblem | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return { kind: "type", description: describeFileKind(file) };
  }
  if (file.size > MAX_SIZE_BYTES) {
    return { kind: "too-large" };
  }
  return null;
}
