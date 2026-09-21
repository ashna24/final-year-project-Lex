const API_BASE_URL = "http://127.0.0.1:8000";

// this only runs one NLLB call
// A cold model load takes about 15 to 20 seconds so 3 minutes leaves plenty of room
const REQUEST_TIMEOUT_MS = 3 * 60 * 1000;

export class TranslateError extends Error {}

export async function translateClauseText(text: string): Promise<string> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new TranslateError("Translation timed out. Please try again.");
    }
    throw new TranslateError(
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
    throw new TranslateError(detail);
  }

  const body = (await response.json()) as { translation: string };
  return body.translation;
}
