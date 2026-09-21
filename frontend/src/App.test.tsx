import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import { AnalyzeError } from "./api/analyze";

vi.mock("./api/analyze", async () => {
  const actual = await vi.importActual<typeof import("./api/analyze")>("./api/analyze");
  return { ...actual, analyzeDocument: vi.fn() };
});

import { analyzeDocument } from "./api/analyze";

async function uploadFile(file: File) {
  const user = userEvent.setup();
  await user.upload(screen.getByLabelText(/choose a document file/i), file);
}

describe("App", () => {
  it("always shows the legal disclaimer, even before any analysis", () => {
    render(<App />);
    expect(screen.getByText(/does not constitute legal advice/i)).toBeInTheDocument();
  });

  it("uploading a valid file immediately enters the loading state, then shows results on success", async () => {
    let resolveAnalyze: (value: Awaited<ReturnType<typeof analyzeDocument>>) => void;
    vi.mocked(analyzeDocument).mockReturnValue(
      new Promise((resolve) => {
        resolveAnalyze = resolve;
      }),
    );
    render(<App />);

    const file = new File(["dummy"], "contract.png", { type: "image/png" });
    await uploadFile(file);

    expect(screen.getByRole("status")).toBeInTheDocument();

    resolveAnalyze!([
      {
        clause_text: "Clause one.",
        risk_level: "High",
        confidence_score: 81,
        explanation: "This is risky.",
      },
    ]);

    await waitFor(() => expect(screen.getByText(/analysis complete/i)).toBeInTheDocument());
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("rejects an unsupported file type dropped in, without calling the API", async () => {
    render(<App />);
    const file = new File(["dummy"], "contract.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    // Uses a drop because the file input would filter this file out first
    // A drop skips that filter so DropZone has to catch it
    const dropzone = screen.getByText(/drag your document here/i).closest(".dropzone")!;
    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });

    expect(await screen.findByText(/can't read that kind of file/i)).toBeInTheDocument();
    expect(screen.getByText(/word document/i)).toBeInTheDocument();
    expect(analyzeDocument).not.toHaveBeenCalled();
  });

  it("returns to the upload screen with a fixed, non-leaky error message when the API call fails", async () => {
    vi.mocked(analyzeDocument).mockRejectedValue(new AnalyzeError("boom — some internal detail"));
    render(<App />);

    const file = new File(["dummy"], "contract.png", { type: "image/png" });
    await uploadFile(file);

    expect(await screen.findByText(/couldn't finish the analysis/i)).toBeInTheDocument();
    expect(screen.queryByText(/boom/i)).not.toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("New document resets from a results screen back to upload", async () => {
    vi.mocked(analyzeDocument).mockResolvedValue([
      {
        clause_text: "Clause one.",
        risk_level: "Low",
        confidence_score: 90,
        explanation: "Fine.",
      },
    ]);
    render(<App />);

    const file = new File(["dummy"], "contract.png", { type: "image/png" });
    await uploadFile(file);
    await screen.findByText(/analysis complete/i);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /new document/i }));

    expect(screen.getByText(/upload the document you were asked to sign/i)).toBeInTheDocument();
  });
});
