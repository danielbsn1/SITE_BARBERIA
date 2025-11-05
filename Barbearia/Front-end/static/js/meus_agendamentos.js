
ocument.getElementById('buscar').addEventListener('click', async () => {
      const tel = document.getElementById('telefone').value.trim();
      const ul = document.getElementById('lista-cliente');
      if (!tel) { ul.innerHTML = '<li>Digite o telefone.</li>'; return; }

      ul.innerHTML = '<li>Carregando...</li>';
      try {
        const res = await fetch('/api/agendamentos?telefone=' + encodeURIComponent(tel));
        if (!res.ok) throw new Error('Erro ao buscar');
        const data = await res.json();
        ul.innerHTML = '';
        if (!data.agendamentos || data.agendamentos.length === 0) {
          ul.innerHTML = '<li>Nenhum agendamento encontrado.</li>';
          return;
        }
        data.agendamentos.forEach(a => {
          const li = document.createElement('li');
          li.textContent = `${a.data_hora} — ${a.servico} — R$ ${Number(a.preco).toFixed(2)} — Pago: ${a.pago ? 'Sim' : 'Não'}`;
          ul.appendChild(li);
        });
      } catch (err) {
        ul.innerHTML = `<li>Erro: ${err.message}</li>`;
      }
    });