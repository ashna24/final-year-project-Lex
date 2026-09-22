import { describe, expect, it } from "vitest";
import { confidencePipCount } from "./confidence";

describe("confidencePipCount", () => {
  it.each([
    [50, 1],
    [60, 1],
    [68, 1],
    [69, 2],
    [75, 2],
    [81, 2],
    [82, 3],
    [90, 3],
    [93, 3],
    [94, 4],
    [100, 4],
  ])("maps confidence %i to %i pips", (confidence, expected) => {
    expect(confidencePipCount(confidence)).toBe(expected);
  });

  it("clamps scores at or below 50 to 1 pip", () => {
    expect(confidencePipCount(50)).toBe(1);
    expect(confidencePipCount(10)).toBe(1);
    expect(confidencePipCount(0)).toBe(1);
  });
});
