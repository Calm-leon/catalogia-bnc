import { render, screen, waitFor } from "@testing-library/react";
import XmlPage from "./page";
import {
  PIPELINE_RESULT_STORAGE_KEY,
  TOKEN_STORAGE_KEY,
} from "../lib/catalogia";

const replaceMock = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: replaceMock,
  }),
}));

describe("XmlPage", () => {
  beforeEach(() => {
    replaceMock.mockReset();
    window.sessionStorage.clear();
  });

  it("muestra fallback cuando no hay resultado en sesion", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");

    render(<XmlPage />);

    await waitFor(() => {
      expect(
        screen.getByText(/No hay XML cargado en esta sesion/i),
      ).toBeInTheDocument();
    });
  });

  it("renderiza xml y ruta cuando existe resultado en sesion", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    window.sessionStorage.setItem(
      PIPELINE_RESULT_STORAGE_KEY,
      JSON.stringify({
        job_id: 7,
        job_status: "completed",
        image_file_id: 1,
        xml_file_id: 2,
        xml_relative_path: "xml/2026/02/12/file.xml",
        xml_content: "<dc:title>portada.jpg</dc:title>",
      }),
    );

    render(<XmlPage />);

    await waitFor(() => {
      expect(screen.getByText("XML generado")).toBeInTheDocument();
      expect(
        screen.getByText("<dc:title>portada.jpg</dc:title>"),
      ).toBeInTheDocument();
      expect(screen.getByText("xml/2026/02/12/file.xml")).toBeInTheDocument();
    });
  });
});
