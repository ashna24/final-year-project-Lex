import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Disclaimer } from "./Disclaimer";

describe("Disclaimer", () => {
  it("always renders the legal-advice disclaimer text with no way to dismiss it", () => {
    render(<Disclaimer />);
    expect(screen.getByText(/does not constitute legal advice/i)).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
