import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import XmlPage from "./page";
import {
  PIPELINE_RESULT_STORAGE_KEY,
  TOKEN_STORAGE_KEY,
} from "../lib/catalogia";

const replaceMock = jest.fn();
const routerMock = { replace: replaceMock };

jest.mock("next/navigation", () => ({
  useRouter: () => routerMock,
}));

describe("XmlPage", () => {
  beforeEach(() => {
    replaceMock.mockReset();
    window.sessionStorage.clear();
    global.fetch = jest.fn();
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
      expect(screen.getByText("Revision XML Dublin Core")).toBeInTheDocument();
      expect(
        screen.getByText("<dc:title>portada.jpg</dc:title>"),
      ).toBeInTheDocument();
      expect(screen.getByText("xml/2026/02/12/file.xml")).toBeInTheDocument();
    });
  });

  it("bloquea guardado cuando falta un campo obligatorio", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    window.sessionStorage.setItem(
      PIPELINE_RESULT_STORAGE_KEY,
      JSON.stringify({
        job_id: 7,
        job_status: "completed",
        image_file_id: 1,
        xml_file_id: 2,
        xml_relative_path: "xml/2026/02/12/file.xml",
        xml_content:
          "<dc:title>portada.jpg</dc:title>\n<dc:creator>Ana</dc:creator>\n<dc:date>2026-02-12</dc:date>\n<dc:format>image/jpeg</dc:format>",
      }),
    );
    const user = userEvent.setup();

    render(<XmlPage />);

    await user.click(screen.getByRole("button", { name: "Guardar revision XML" }));

    expect(
      await screen.findByText(
        "Debes completar title, creator, date, format y description.",
      ),
    ).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
