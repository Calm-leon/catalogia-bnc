export default function UploadPage() {
  return (
    <section className="card">
      <h2>Carga de archivo</h2>
      <form>
        <label>
          Archivo
          <input type="file" name="file" />
        </label>
        <label>
          Tipo
          <select name="type">
            <option value="image">Imagen</option>
            <option value="pdf">PDF</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
          </select>
        </label>
        <button type="button">Subir</button>
      </form>
      <p>
        Continuar: <a href="/xml">Ver XML</a>
      </p>
    </section>
  );
}