async function carregarCaixa() {
    const data = document.getElementById('data').value;
    const res = await fetch('/api/agendamentos?data=' + data);
    const dados = await res.json();
    const lista = document.getElementById('lista');
    lista.innerHTML = '';

    let total = 0;
    dados.agendamentos.forEach(a => {
      total += a.preco;
      const li = document.createElement('li');
      li.textContent = `${a.data_hora.slice(11,16)} - ${a.cliente} - ${a.servico} - R$ ${a.preco.toFixed(2)}`;
      lista.appendChild(li);
    });

    const liTotal = document.createElement('li');
    liTotal.innerHTML = `<strong>Total do dia: R$ ${total.toFixed(2)}</strong>`;
    lista.appendChild(liTotal);
  }

  document.getElementById('data').addEventListener('change', carregarCaixa);

  window.addEventListener('DOMContentLoaded', () => {
    const hoje = new Date().toISOString().slice(0, 10);
    document.getElementById('data').value = hoje;
    carregarCaixa();
  });