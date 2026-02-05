export default function Home() {
  return (
    <section className="card">
      <h2>Flujo CatalogIA</h2>
      <p>UI base para recorrido de carga y revision sin autenticacion real.</p>
      <ol>
        <li><a href="/login">Login basico</a></li>
        <li><a href="/select">Seleccion de tipo de objeto</a></li>
        <li><a href="/upload">Carga de archivo</a></li>
        <li><a href="/xml">Visualizacion de XML</a></li>
      </ol>
    </section>
  );
}