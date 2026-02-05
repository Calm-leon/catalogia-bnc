export default function LoginPage() {
  return (
    <section className="card">
      <h2>Login basico</h2>
      <p>Sin autenticacion real. Solo flujo de UI.</p>
      <form>
        <label>
          Correo
          <input type="email" name="email" placeholder="usuario@bnc.gov" />
        </label>
        <label>
          Contrasena
          <input type="password" name="password" placeholder="********" />
        </label>
        <button type="button">Ingresar</button>
      </form>
      <p>
        Continuar: <a href="/select">Seleccionar tipo de objeto</a>
      </p>
    </section>
  );
}