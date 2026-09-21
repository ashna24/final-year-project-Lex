import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { LanguageSwitch } from "./LanguageSwitch";

describe("LanguageSwitch", () => {
  it("marks the current value as the checked radio", () => {
    render(<LanguageSwitch value="both" onChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "Both" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "English" })).toHaveAttribute("aria-checked", "false");
  });

  it("calls onChange with the clicked option's value", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<LanguageSwitch value="en" onChange={onChange} />);

    await user.click(screen.getByRole("radio", { name: "اردو" }));
    expect(onChange).toHaveBeenCalledWith("ur");
  });
});
