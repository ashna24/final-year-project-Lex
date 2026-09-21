import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it.each([
    ["High", "risk-badge--high"],
    ["Medium", "risk-badge--medium"],
    ["Low", "risk-badge--low"],
    ["Error", "risk-badge--error"],
  ] as const)("applies the correct style class for %s", (level, expectedClass) => {
    render(<RiskBadge level={level} />);
    expect(screen.getByText(new RegExp(level, "i"))).toHaveClass(expectedClass);
  });
});
