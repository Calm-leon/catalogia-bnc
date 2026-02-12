import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import UploadPage from "./page";
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

function createDeferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

describe("UploadPage", () => {
  beforeEach(() => {
    replaceMock.mockReset();
    window.sessionStorage.clear();
    global.fetch = jest.fn();
  });

  it("muestra error si no hay archivo al enviar", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    const user = userEvent.setup();

    render(<UploadPage />);

    await user.click(
      screen.getByRole("button", { name: "Subir y generar XML" }),
    );

    expect(
      screen.getByText("Selecciona un archivo para continuar."),
    ).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("procesa upload exitoso, muestra loading y guarda resultado en sesion", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    const user = userEvent.setup();
    const deferred = createDeferred<{
      ok: boolean;
      status: number;
      json: () => Promise<unknown>;
    }>();

    (global.fetch as jest.Mock).mockReturnValueOnce(deferred.promise);

    render(<UploadPage />);

    const file = new File(["img"], "portada.jpg", { type: "image/jpeg" });
    await user.upload(screen.getByLabelText("Archivo"), file);
    await user.click(
      screen.getByRole("button", { name: "Subir y generar XML" }),
    );

    expect(
      screen.getByRole("button", { name: "Procesando..." }),
    ).toBeDisabled();

    deferred.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        image_file_id: 1,
        xml_file_id: 2,
        xml_relative_path: "xml/2026/02/12/file.xml",
        xml_content: "<dc:title>portada.jpg</dc:title>",
      }),
    });

    await waitFor(() => {
      expect(
        screen.getByText(
          "Archivo procesado correctamente. Ya puedes revisar el XML.",
        ),
      ).toBeInTheDocument();
    });

    const storedResult = window.sessionStorage.getItem(
      PIPELINE_RESULT_STORAGE_KEY,
    );
    expect(storedResult).toContain("xml/2026/02/12/file.xml");
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("muestra mensaje de error cuando backend responde con detalle", async () => {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, "cataloger-token");
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Unauthorized" }),
    });

    render(<UploadPage />);

    const file = new File(["img"], "portada.jpg", { type: "image/jpeg" });
    await user.upload(screen.getByLabelText("Archivo"), file);
    await user.click(
      screen.getByRole("button", { name: "Subir y generar XML" }),
    );

    await waitFor(() => {
      expect(screen.getByText("Unauthorized")).toBeInTheDocument();
    });
  });
});
