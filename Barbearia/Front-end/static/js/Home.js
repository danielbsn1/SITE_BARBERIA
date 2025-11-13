
function gerarHome() {
  const main = document.querySelector('main');
  if (!main) {
    console.error('Elemento <main> não encontrado!');
    return;
  }

  if (main.querySelector('.home')) return;

  main.innerHTML = `
    <section class="home">
      <h1>💈 Barbearia Style</h1>
      <img src="/static/img/Barberia.jpeg" alt="Logo da barbearia" class="logo">
      <p>Bem-vindo! Escolha uma opção para continuar:</p>
      <a href="/agenda" class="btn">Ir para Agenda</a>
      <br>
      <a href="/meus-agendamentos" class="btn">Meus Agendamentos</a>
      <footer>© 2025 Barbearia Style</footer>
    </section>
  `;
}

window.addEventListener('DOMContentLoaded', gerarHome);