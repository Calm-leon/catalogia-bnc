import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import SelectPage from "./page";
import { TOKEN_STORAGE_KEY } from "../lib/catalogia";

const replaceMock = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: replaceMock,
  }),
}));

describe("SelectPage", () => {
  beforeEach(() => {
    replaceMock.mockReset();
    window.sessionStorage.clear();
    global.fetch = jest.fn();
  });

  it("redirige a login cuando no hay token", async () => {
    render(<SelectPage />);
    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login");
    });
  });

  it("muestra historial y detalle de job", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockImplementation((input: string) => {
      if (input.includes("/internal/jobs?")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            limit: 20,
            offset: 0,
            total: 1,
            jobs: [
              {
                id: 77,
                status: "completed",
                source_filename: "input.jpg",
                created_at: "2026-02-26T00:00:00+00:00",
                quality: {
                  passed: false,
                  score: 85.71,
                  checks: [],
                },
              },
            ],
          }),
        });
      }
      if (input.includes("/internal/jobs/77")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            job: {
              id: 77,
              status: "completed",
              source_filename: "input.jpg",
              created_at: "2026-02-26T00:00:00+00:00",
              quality: {
                passed: false,
                score: 85.71,
                checks: [
                  {
                    key: "required_type",
                    passed: false,
                    detail: "Falta contenido en dc:type",
                  },
                ],
              },
            },
            logs: [
              {
                id: 1,
                level: "info",
                message: "pipeline_image_completed",
                created_at: "2026-02-26T00:00:01+00:00",
              },
            ],
            files: [
              {
                id: 1,
                storage_type: "xml",
                relative_path: "xml/2026/02/26/out.xml",
                size_bytes: 100,
                created_at: "2026-02-26T00:00:01+00:00",
              },
            ],
          }),
        });
      }
      return Promise.resolve({
        ok: false,
        json: async () => ({ detail: "Not found" }),
      });
    });

    render(<SelectPage />);

    await waitFor(() => {
      expect(screen.getByText(/job_id/i)).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Ver detalle" }));

    await waitFor(() => {
      expect(screen.getByText("Detalle job 77")).toBeInTheDocument();
      expect(screen.getByText(/required_type/i)).toBeInTheDocument();
      expect(screen.getByText(/pipeline_image_completed/i)).toBeInTheDocument();
      expect(screen.getByText(/xml\/2026\/02\/26\/out\.xml/i)).toBeInTheDocument();
    });
  });
});
