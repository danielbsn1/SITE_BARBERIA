document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('formLogin');
  const msg = document.getElementById('mensagem');

  if (!form) return; 

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const usuario = document.getElementById('usuario').value.trim();
    const senha = document.getElementById('senha').value.trim();

    if (!usuario || !senha) {
      msg.textContent = 'Preencha todos os campos.';
      msg.style.color = 'red';
      return;
    }

    
    if (usuario === 'admin' && senha === '1234') {
      msg.textContent = 'Login bem-sucedido! Redirecionando...';
      msg.style.color = 'green';
      setTimeout(() => {
        window.location.href = '/caixa'; 
      }, 1000);
    } else {
      msg.textContent = 'Usuário ou senha incorretos.';
      msg.style.color = 'red';
    }
  });
});
