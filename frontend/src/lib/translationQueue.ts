import { translateClauseText } from "../api/translate";

// Several cards can ask for Urdu at once but the backend may not handle parallel calls
// So this queues them and sends one at a time
let queue: Promise<unknown> = Promise.resolve();

export function queueTranslation(text: string): Promise<string> {
  const result = queue.then(() => translateClauseText(text));
  queue = result.catch(() => undefined);
  return result;
}
