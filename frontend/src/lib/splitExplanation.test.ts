import { describe, expect, it } from "vitest";
import { splitExplanation } from "./splitExplanation";

describe("splitExplanation", () => {
  it("splits off the first sentence as the title, leaving the rest as the body", () => {
    const result = splitExplanation(
      "Your deposit can be kept for reasons that are not defined. This means the landlord has a lot of freedom to decide what counts.",
    );
    expect(result.title).toBe("Your deposit can be kept for reasons that are not defined.");
    expect(result.body).toBe("This means the landlord has a lot of freedom to decide what counts.");
  });

  it("uses the whole explanation as the title with no body when there is no clean early sentence break", () => {
    const result = splitExplanation("This is one short sentence with no period at the end");
    expect(result.title).toBe("This is one short sentence with no period at the end");
    expect(result.body).toBeNull();
  });
});
