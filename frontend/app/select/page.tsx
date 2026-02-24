"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getBackendUrl, TOKEN_STORAGE_KEY } from "../lib/catalogia";

type QualityCheck = {
  key: string;
  passed: boolean;
  detail: string;
};

type QualitySummary = {
  passed: boolean;
  score: number;
  checks: QualityCheck[];
};

type JobItem = {
  id: number;
  status: string;
  source_filename: string | null;
  created_at: string;
  quality?: QualitySummary | null;
};

type JobsListResponse = {
  limit: number;
  offset: number;
  total: number;
  jobs: JobItem[];
};

type JobDetailResponse = {
  job: JobItem;
  logs: Array<{
    id: number;
    level: string;
    message: string;
    created_at: string;
  }>;
  files: Array<{
    id: number;
    storage_type: string;
    relative_path: string;
    size_bytes: number;
    created_at: string;
  }>;
};

export default function SelectPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [detail, setDetail] = useState<JobDetailResponse | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
      return;
    }

    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(
          `${getBackendUrl()}/internal/jobs?limit=20&offset=0&include_quality=true`,
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );
        const payload = (await response.json()) as JobsListResponse | { detail?: string };
        if (!response.ok) {
          const detailText = "detail" in payload ? payload.detail : undefined;
          throw new Error(detailText ?? `Error de backend (${response.status}).`);
        }
        setJobs((payload as JobsListResponse).jobs);
      } catch (fetchError) {
        setError(fetchError instanceof Error ? fetchError.message : "No se pudo cargar historial.");
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, [router]);

  async function loadDetail(jobId: number) {
    const token = window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
      return;
    }

    setSelectedJobId(jobId);
    setDetail(null);
    setLoadingDetail(true);
    setError(null);

    try {
      const response = await fetch(
        `${getBackendUrl()}/internal/jobs/${jobId}?include_quality=true`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      const payload = (await response.json()) as JobDetailResponse | { detail?: string };
      if (!response.ok) {
        const detailText = "detail" in payload ? payload.detail : undefined;
        throw new Error(detailText ?? `Error de backend (${response.status}).`);
      }
      setDetail(payload as JobDetailResponse);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "No se pudo cargar detalle.");
    } finally {
      setLoadingDetail(false);
    }
  }

  return (
    <section className="card">
      <h2>Historial operativo de jobs</h2>
      <p>
        Consulta ejecuciones recientes, calidad minima de metadatos y detalle con logs/archivos.
      </p>

      {loading ? <p>Cargando historial...</p> : null}
      {error ? <p className="statusError">{error}</p> : null}

      {!loading && jobs.length === 0 ? (
        <p className="statusError">No hay jobs recientes para mostrar.</p>
      ) : null}

      {jobs.length > 0 ? (
        <div className="resultBox">
          {jobs.map((job) => (
            <div key={job.id} style={{ marginBottom: "0.75rem" }}>
              <p>
                <code>job_id</code>: {job.id} | <code>status</code>: {job.status} |{" "}
                <code>quality</code>: {job.quality ? `${job.quality.score}%` : "N/A"}
              </p>
              <p>
                <code>source</code>: {job.source_filename ?? "-"} | <code>created_at</code>:{" "}
                {new Date(job.created_at).toLocaleString()}
              </p>
              <button type="button" onClick={() => void loadDetail(job.id)}>
                Ver detalle
              </button>
            </div>
          ))}
        </div>
      ) : null}

      {loadingDetail ? <p>Cargando detalle...</p> : null}

      {detail && selectedJobId === detail.job.id ? (
        <div className="resultBox">
          <h3>Detalle job {detail.job.id}</h3>
          <p>
            <code>status</code>: {detail.job.status} | <code>quality</code>:{" "}
            {detail.job.quality ? `${detail.job.quality.score}%` : "N/A"}
          </p>
          {detail.job.quality ? (
            <div>
              <p>Checklist calidad:</p>
              {detail.job.quality.checks.map((check) => (
                <p key={check.key}>
                  <code>{check.key}</code>: {check.passed ? "OK" : "FALLO"} - {check.detail}
                </p>
              ))}
            </div>
          ) : null}
          <p>Archivos asociados:</p>
          {detail.files.map((file) => (
            <p key={file.id}>
              <code>{file.storage_type}</code> - {file.relative_path}
            </p>
          ))}
          <p>Logs asociados:</p>
          {detail.logs.map((log) => (
            <p key={log.id}>
              [{log.level}] {log.message}
            </p>
          ))}
        </div>
      ) : null}

      <p>
        Continuar: <a href="/upload">Carga de archivo</a>
      </p>
    </section>
  );
}
