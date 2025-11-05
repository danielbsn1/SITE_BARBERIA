// static/js/login.js
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const usuario = document.getElementById('usuario').value.trim();
  const senha = document.getElementById('senha').value.trim();

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario, senha })
    });

    const data = await res.json();

    if (res.ok) {
      alert('Login realizado com sucesso!');
      window.location.href = '/caixa'; // 👉 redireciona direto pro caixa
    } else {
      alert(data.error || 'Usuário ou senha incorretos.');
    }
  } catch (err) {
    alert('Erro ao tentar fazer login: ' + err.message);
  }
});
