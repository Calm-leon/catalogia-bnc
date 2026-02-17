"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getBackendUrl,
  PipelineImageResponse,
  savePipelineResult,
  TOKEN_STORAGE_KEY,
} from "../lib/catalogia";

type RequestStatus = "idle" | "loading" | "success" | "error";

const STORAGE_OPTIONS = [
  { value: "images", label: "Imagen" },
  { value: "pdf", label: "PDF" },
  { value: "audio", label: "Audio" },
  { value: "video", label: "Video" },
];

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [storageType, setStorageType] = useState("images");
  const [creator, setCreator] = useState("");
  const [status, setStatus] = useState<RequestStatus>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineImageResponse | null>(null);

  useEffect(() => {
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
    }
  }, [router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);

    if (!token) {
      setStatus("error");
      setMessage("No hay token de sesion. Inicia sesion nuevamente.");
      router.replace("/login");
      return;
    }

    if (!file) {
      setStatus("error");
      setMessage("Selecciona un archivo para continuar.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("storage_type", storageType);
    if (creator.trim()) {
      formData.append("creator", creator.trim());
    }

    setStatus("loading");
    setMessage(null);
    setResult(null);

    try {
      const response = await fetch(`${getBackendUrl()}/internal/pipeline/image`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const payload = (await response.json()) as
        | PipelineImageResponse
        | { detail?: string };

      if (!response.ok) {
        const detail = "detail" in payload ? payload.detail : undefined;
        throw new Error(detail ?? `Error de backend (${response.status}).`);
      }

      savePipelineResult(payload as PipelineImageResponse);
      setResult(payload as PipelineImageResponse);
      setStatus("success");
      setMessage("Archivo procesado correctamente. Ya puedes revisar el XML.");
    } catch (error) {
      setStatus("error");
      setMessage(
        error instanceof Error
          ? error.message
          : "No fue posible procesar la solicitud.",
      );
    }
  }

  return (
    <section className="card">
      <h2>Carga de archivo</h2>
      <form onSubmit={onSubmit} className="formStack">
        <label>
          Archivo
          <input
            type="file"
            name="file"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
            }}
          />
        </label>
        <label>
          Tipo de almacenamiento
          <select
            name="storage_type"
            value={storageType}
            onChange={(event) => setStorageType(event.target.value)}
          >
            {STORAGE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Creador (opcional)
          <input
            type="text"
            name="creator"
            placeholder="Nombre del creador"
            value={creator}
            onChange={(event) => setCreator(event.target.value)}
          />
        </label>
        <button type="submit" disabled={status === "loading"}>
          {status === "loading" ? "Procesando..." : "Subir y generar XML"}
        </button>
      </form>

      {status === "success" && message ? (
        <p className="statusSuccess">{message}</p>
      ) : null}
      {status === "error" && message ? <p className="statusError">{message}</p> : null}

      {result ? (
        <div className="resultBox">
          <p>
            <code>job_id</code>: {result.job_id} | <code>job_status</code>:{" "}
            {result.job_status}
          </p>
          <p>
            <code>image_file_id</code>: {result.image_file_id} |{" "}
            <code>xml_file_id</code>:{" "}
            {result.xml_file_id}
          </p>
          <p>
            <code>xml_relative_path</code>: {result.xml_relative_path}
          </p>
        </div>
      ) : null}

      <p>
        Continuar: <a href="/xml">Ver XML</a>
      </p>
    </section>
  );
}
