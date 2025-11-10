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
    console.log('loadServicos: iniciando fetch');
    const res = await fetch('/api/servicos');
    console.log('loadServicos: status', res.status);
    if(!res.ok){
      const txt = await res.text();
      throw new Error(`Status ${res.status}: ${txt}`);
    }
    const data = await res.json();
    console.log('loadServicos: data', data);
    const sel = document.getElementById('servico');
    if(!sel) { console.error('select #servico não encontrado'); return; }
    sel.innerHTML = '';
    if(!data.servicos || data.servicos.length===0){
      sel.innerHTML = '<option value="">Nenhum serviço</option>';
      return;
    }
    data.servicos.forEach(s=>{
      const opt = document.createElement('option');
      opt.value = String(s.id);
      opt.textContent = `${s.nome} — R$ ${Number(s.preco).toFixed(2)}`;
      sel.appendChild(opt);
    });
    console.log('loadServicos: preenchido');
  } catch (err) {
    console.error('Erro loadServicos:', err);
    const sel = document.getElementById('servico');
    if(sel) sel.innerHTML = `<option>Erro ao carregar</option>`;
    const msg = document.getElementById('msg');
    if(msg){ msg.style.display='block'; msg.textContent = 'Erro loadServicos: '+err.message; }
  }
}

// Carrega agendamentos de uma data
async function loadAgendamentos(data) {
  try {
    const res = await fetch('/api/agendamentos?data=' + data);
    const dados = await res.json();

    const lista = document.getElementById('lista-agendamentos');
    if (!lista) return console.error('Elemento lista-agendamentos não encontrado');
    lista.innerHTML = '<li>Carregando...</li>';

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
document.addEventListener('DOMContentLoaded', function() {
    const hoje = new Date().toISOString().slice(0,10);
    
    // Função auxiliar para mostrar mensagens
    function mostrarMensagem(texto, tipo = 'erro') {
        const msg = document.getElementById('msg');
        if (!msg) return;
        
        msg.textContent = texto;
        msg.className = `mensagem ${tipo}`;
        msg.style.display = 'block';
        
        if (tipo === 'sucesso') {
            setTimeout(() => msg.style.display = 'none', 3000);
        }
    }

    // Gera opções de horário
    function gerarHoras() {
        const selectHora = document.getElementById('hora');
        if (!selectHora) return;
        
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
            if (!res.ok) throw new Error(`Erro ao carregar serviços (${res.status})`);
            
            const data = await res.json();
            const select = document.getElementById('servico');
            if (!select) return;
            
            select.innerHTML = '';
            if (!data.servicos?.length) {
                select.innerHTML = '<option value="">Nenhum serviço disponível</option>';
                return;
            }
            
            data.servicos.forEach(s => {
                const opt = document.createElement('option');
                opt.value = String(s.id);
                opt.textContent = `${s.nome} — R$ ${Number(s.preco).toFixed(2)}`;
                select.appendChild(opt);
            });
        } catch (err) {
            console.error('Erro:', err);
            mostrarMensagem('Erro ao carregar serviços. Tente novamente.');
        }
    }

    // Handler do formulário
    const form = document.getElementById('agendamentoForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            mostrarMensagem('', ''); // limpa mensagens anteriores

            // Coleta dados do formulário
            const nome = document.getElementById('nome').value.trim();
            const telefone = document.getElementById('telefone').value.trim();
            const servico_id = document.getElementById('servico').value;
            const data = document.getElementById('data').value;
            const hora = document.getElementById('hora').value;

            // Validação básica
            if (!nome || !telefone || !servico_id || !data || !hora) {
                mostrarMensagem('Por favor, preencha todos os campos.');
                return;
            }

            try {
                const res = await fetch('/api/agendamentos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome, telefone, servico_id, data, hora })
                });

                const result = await res.json();
                
                if (res.ok && result.success) {
                    mostrarMensagem('Agendamento realizado com sucesso! ✅', 'sucesso');
                    form.reset();
                    document.getElementById('data').value = hoje;
                    gerarHoras();
                } else if (res.status === 409) {
                    mostrarMensagem('Este horário já está agendado. Por favor, escolha outro horário.');
                } else {
                    throw new Error(result.error || 'Erro ao criar agendamento');
                }
            } catch (err) {
                mostrarMensagem(err.message);
            }
        });
    }

    // Inicialização
    const dataInput = document.getElementById('data');
    if (dataInput) {
        dataInput.value = hoje;
        dataInput.min = hoje; // Impede datas passadas
    }
    
    gerarHoras();
    loadServicos();
});