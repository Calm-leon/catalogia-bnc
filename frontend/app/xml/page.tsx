"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { loadPipelineResult, TOKEN_STORAGE_KEY } from "../lib/catalogia";

export default function XmlPage() {
  const router = useRouter();
  const [xmlContent, setXmlContent] = useState<string | null>(null);
  const [xmlPath, setXmlPath] = useState<string | null>(null);

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
  }, [router]);

  return (
    <section className="card">
      <h2>XML generado</h2>
      {xmlContent ? (
        <>
          <p>
            Ruta en storage: <code>{xmlPath}</code>
          </p>
          <pre>{xmlContent}</pre>
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
