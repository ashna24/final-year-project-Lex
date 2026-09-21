import { describe, expect, it } from "vitest";
import { confidencePipCount } from "./confidence";

describe("confidencePipCount", () => {
  it.each([
    [75, 1],
    [80, 1],
    [81, 1],
    [82, 2],
    [87, 2],
    [88, 3],
    [90, 3],
    [94, 4],
    [95, 4],
    [100, 4],
  ])("maps confidence %i to %i pips", (confidence, expected) => {
    expect(confidencePipCount(confidence)).toBe(expected);
  });

  it("clamps low scores to at least 1 pip rather than 0", () => {
    expect(confidencePipCount(10)).toBe(1);
    expect(confidencePipCount(0)).toBe(1);
  });
});
