import type { ClauseResult } from "../types";

const API_BASE_URL = "http://127.0.0.1:8000";

// Set high on purpose since real runs took up to 34 minutes when memory was low
// A short timeout would fail a request that was still working
const REQUEST_TIMEOUT_MS = 45 * 60 * 1000;

export class AnalyzeError extends Error {}

export async function analyzeDocument(
  file: File,
  translate: boolean,
  signal?: AbortSignal,
): Promise<ClauseResult[]> {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE_URL}/analyze?translate=${translate}`;

  const combinedSignal = signal
    ? AbortSignal.any([signal, AbortSignal.timeout(REQUEST_TIMEOUT_MS)])
    : AbortSignal.timeout(REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      body: formData,
      signal: combinedSignal,
    });
  } catch (err) {
    if (signal?.aborted) {
      throw err; // The user pressed Cancel so pass the error on unchanged
    }
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new AnalyzeError(
        "The request timed out after 45 minutes. This document may be unusually " +
          "large, or the server may be under heavy memory pressure. Try again, or " +
          "with a smaller document.",
      );
    }
    throw new AnalyzeError(
      "Could not reach the Lex server. Make sure the backend is running at " +
        API_BASE_URL +
        " and try again.",
    );
  }

  if (!response.ok) {
    let detail = `Server returned an error (status ${response.status}).`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
    }
    throw new AnalyzeError(detail);
  }

  return (await response.json()) as ClauseResult[];
}
