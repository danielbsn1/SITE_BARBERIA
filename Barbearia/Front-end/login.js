
// login.js
gerarloginForm();


document.getElementById('loginForm').addEventListener('submit', async function(e){
  e.preventDefault();
  const usuario = document.getElementById('usuario').value;
  const senha = document.getElementById('senha').value;
  const msg = document.getElementById('messages');

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin, 1234  })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      window.location = data.redirect || '/';
    } else {
      msg.style.display = 'block';
      msg.textContent = data.error || 'Erro no login';
    }
  } catch (err) {
    msg.style.display = 'block';
    msg.textContent = 'Erro de conexão';
  }
});