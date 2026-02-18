"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getBackendUrl,
  loadPipelineResult,
  TOKEN_STORAGE_KEY,
} from "../lib/catalogia";

type DcFormState = {
  title: string;
  creator: string;
  date: string;
  format: string;
  description: string;
};

const EMPTY_FORM: DcFormState = {
  title: "",
  creator: "",
  date: "",
  format: "",
  description: "",
};

function parseTag(xml: string, tag: keyof DcFormState): string {
  const pattern = new RegExp(`<dc:${tag}>([\\s\\S]*?)</dc:${tag}>`, "i");
  const match = xml.match(pattern);
  return match?.[1]?.trim() ?? "";
}

function parseXmlToForm(xml: string): DcFormState {
  return {
    title: parseTag(xml, "title"),
    creator: parseTag(xml, "creator"),
    date: parseTag(xml, "date"),
    format: parseTag(xml, "format"),
    description: parseTag(xml, "description"),
  };
}

export default function XmlPage() {
  const router = useRouter();
  const [xmlContent, setXmlContent] = useState<string | null>(null);
  const [xmlPath, setXmlPath] = useState<string | null>(null);
  const [jobId, setJobId] = useState<number | null>(null);
  const [form, setForm] = useState<DcFormState>(EMPTY_FORM);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const hasMissingRequiredField = useMemo(
    () => Object.values(form).some((value) => !value.trim()),
    [form],
  );

  useEffect(() => {
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
      return;
    }

    const pipelineResult = loadPipelineResult();
    if (!pipelineResult) {
      setXmlContent(null);
      setXmlPath(null);
      return;
    }

    setXmlContent(pipelineResult.xml_content);
    setXmlPath(pipelineResult.xml_relative_path);
    setJobId(pipelineResult.job_id);
    setForm(parseXmlToForm(pipelineResult.xml_content));
  }, [router]);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!jobId || !xmlPath || !xmlContent) {
      setSaveError("No hay contexto de pipeline para guardar la revision.");
      return;
    }
    if (hasMissingRequiredField) {
      setSaveError("Debes completar title, creator, date, format y description.");
      return;
    }
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
      return;
    }

    setSaving(true);
    setSaveError(null);
    setSaveMessage(null);
    try {
      const response = await fetch(`${getBackendUrl()}/internal/pipeline/image/review`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_id: jobId,
          xml_relative_path: xmlPath,
          ...form,
        }),
      });
      const payload = (await response.json()) as
        | { detail?: string }
        | { xml_content: string; xml_relative_path: string };
      if (!response.ok) {
        const detail = "detail" in payload ? payload.detail : undefined;
        throw new Error(detail ?? `Error de backend (${response.status}).`);
      }

      const reviewed = payload as { xml_content: string; xml_relative_path: string };
      setXmlContent(reviewed.xml_content);
      setXmlPath(reviewed.xml_relative_path);
      setSaveMessage(`Revision guardada en ${reviewed.xml_relative_path}`);
    } catch (error) {
      setSaveError(
        error instanceof Error ? error.message : "No fue posible guardar la revision.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card">
      <h2>Revision XML Dublin Core</h2>
      {xmlContent ? (
        <>
          <p>
            Ruta en storage: <code>{xmlPath}</code>
          </p>
          <p>
            <code>job_id</code>: {jobId}
          </p>
          <pre>{xmlContent}</pre>
          <form className="formStack" onSubmit={onSave}>
            <label>
              title
              <input
                value={form.title}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, title: event.target.value }))
                }
              />
            </label>
            <label>
              creator
              <input
                value={form.creator}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, creator: event.target.value }))
                }
              />
            </label>
            <label>
              date
              <input
                value={form.date}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, date: event.target.value }))
                }
              />
            </label>
            <label>
              format
              <input
                value={form.format}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, format: event.target.value }))
                }
              />
            </label>
            <label>
              description
              <textarea
                value={form.description}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, description: event.target.value }))
                }
              />
            </label>
            <button type="submit" disabled={saving}>
              {saving ? "Guardando..." : "Guardar revision XML"}
            </button>
          </form>
          {saveError ? <p className="statusError">{saveError}</p> : null}
          {saveMessage ? <p className="statusSuccess">{saveMessage}</p> : null}
        </>
      ) : (
        <p className="statusError">
          No hay XML cargado en esta sesion. Vuelve a <a href="/upload">/upload</a>{" "}
          para ejecutar el pipeline.
        </p>
      )}
      <p>
        Volver al inicio: <a href="/">Home</a>
      </p>
    </section>
  );
}
