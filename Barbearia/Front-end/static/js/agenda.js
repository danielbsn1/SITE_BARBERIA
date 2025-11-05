// ==============================
// agenda.js
// ==============================

// Carrega as horas disponíveis
function gerarHoras() {
  const selectHora = document.getElementById('hora');
  selectHora.innerHTML = '';
  for (let h = 7; h <= 20; h++) {
    const hora = h.toString().padStart(2, '0') + ':00';
    const opt = document.createElement('option');
    opt.value = hora;
    opt.textContent = hora;
    selectHora.appendChild(opt);
  }
}

// Carrega serviços do backend
async function loadServicos() {
  try {
    const res = await fetch('/api/servicos');
    const data = await res.json();

    const select = document.getElementById('servico');
    select.innerHTML = '';

    data.servicos.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.nome} - R$ ${s.preco.toFixed(2)}`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Erro ao carregar serviços:', err);
  }
}

// Carrega agendamentos de uma data
async function loadAgendamentos(data) {
  try {
    const res = await fetch('/api/agendamentos?data=' + data);
    const dados = await res.json();

    const lista = document.getElementById('lista-agendamentos');
    lista.innerHTML = '';

    if (!dados.agendamentos || dados.agendamentos.length === 0) {
      lista.innerHTML = '<li>Nenhum agendamento nesta data.</li>';
      return;
    }

    dados.agendamentos.forEach(a => {
      const li = document.createElement('li');
      li.textContent = `${a.hora || a.data_hora.slice(11,16)} - ${a.cliente} - ${a.servico}`;
      lista.appendChild(li);
    });
  } catch (err) {
    console.error('Erro ao carregar agendamentos:', err);
  }
}

// Quando o formulário for enviado
document.getElementById('agendamentoForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const nome = document.getElementById('nome').value.trim();
  const telefone = document.getElementById('telefone').value.trim();
  const servico_id = document.getElementById('servico').value;
  const data = document.getElementById('data').value;
  const hora = document.getElementById('hora').value;

  if (!nome || !servico_id || !data || !hora) {
    alert('Preencha todos os campos obrigatórios!');
    return;
  }

  try {
    const res = await fetch('/api/agendamentos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, telefone, servico_id, data, hora })
    });

    const result = await res.json();

    if (!res.ok) throw new Error(result.error || 'Erro ao salvar agendamento');

    alert('✅ Agendamento realizado com sucesso!');
    loadAgendamentos(data);
  } catch (err) {
    alert('Erro: ' + err.message);
  }
});

// Atualiza lista quando a data muda
document.getElementById('data').addEventListener('change', (e) => {
  loadAgendamentos(e.target.value);
});

// Inicializa a página
window.addEventListener('DOMContentLoaded', () => {
  gerarHoras();
  loadServicos();

  const hoje = new Date().toISOString().slice(0, 10);
  document.getElementById('data').value = hoje;
  loadAgendamentos(hoje);
});