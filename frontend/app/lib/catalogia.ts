export const TOKEN_STORAGE_KEY = "catalogia_token";
export const PIPELINE_RESULT_STORAGE_KEY = "catalogia_pipeline_result";

export type PipelineImageResponse = {
  job_id: number;
  job_status: "queued" | "running" | "completed" | "failed";
  image_file_id: number;
  xml_file_id: number;
  xml_relative_path: string;
  xml_content: string;
};

export function getBackendUrl(): string {
  const candidate =
    process.env.NEXT_PUBLIC_BACKEND_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000";
  return candidate.replace(/\/+$/, "");
}

export function savePipelineResult(result: PipelineImageResponse): void {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.setItem(
    PIPELINE_RESULT_STORAGE_KEY,
    JSON.stringify(result),
  );
}

export function loadPipelineResult(): PipelineImageResponse | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.sessionStorage.getItem(PIPELINE_RESULT_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as PipelineImageResponse;
  } catch {
    return null;
  }
}
