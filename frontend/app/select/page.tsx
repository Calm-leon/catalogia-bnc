export default function SelectPage() {
  return (
    <section className="card">
      <h2>Seleccion de tipo de objeto</h2>
      <form>
        <label>
          <input type="radio" name="type" value="image" /> Imagen
        </label>
        <label>
          <input type="radio" name="type" value="pdf" /> PDF
        </label>
        <label>
          <input type="radio" name="type" value="audio" /> Audio
        </label>
        <label>
          <input type="radio" name="type" value="video" /> Video
        </label>
        <button type="button">Continuar</button>
      </form>
      <p>
        Continuar: <a href="/upload">Carga de archivo</a>
      </p>
    </section>
  );
}