// agenda.js
gerarHoras();
loadServicos();
loadAgendamentos(new Date().toISOString().slice(0,10));
const hoje = new Date().toISOString().slice(0,10);
document.getElementById('data').value = hoje;


function gerarHoras(){
  const sel = document.getElementById('hora');
  sel.innerHTML = '';
  for(let h=8; h<=19; h++){ // 08:00 até 19:00
    const hh = String(h).padStart(2,'0') + ':00';
    const opt = document.createElement('option');
    opt.value = hh; opt.textContent = hh;
    sel.appendChild(opt);
  }
}

async function loadServicos(){
  try{
    const res = await fetch('/api/servicos');
    const data = await res.json();
    const sel = document.getElementById('servico');
    sel.innerHTML = '';
    if(!data.servicos || data.servicos.length===0){
      sel.innerHTML = '<option value="">Nenhum serviço</option>';
      return;
    }
    data.servicos.forEach(s=>{
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.nome} — R$ ${Number(s.preco).toFixed(2)}`;
      sel.appendChild(opt);
    });
  }catch(err){
    console.error(err);
  }
}

async function loadAgendamentos(date){
  const ul = document.getElementById('lista-agendamentos');
  ul.innerHTML = '<li>Carregando...</li>';
  try{
    const res = await fetch('/api/agendamentos?data=' + date);
    if(!res.ok) throw new Error('Falha ao carregar');
    const data = await res.json();
    ul.innerHTML = '';
    if(!data.agendamentos || data.agendamentos.length===0){
      ul.innerHTML = '<li>Nenhum agendamento nesta data.</li>';
      return;
    }
    data.agendamentos.forEach(a=>{
      const li = document.createElement('li');
      const hora = a.data_hora ? a.data_hora.split(' ')[1] : '';
      li.textContent = `${hora} — ${a.cliente || a.nome || '---'} — ${a.servico || ''} — R$ ${Number(a.preco||0).toFixed(2)}`;
      ul.appendChild(li);
    });
  }catch(err){
    ul.innerHTML = `<li>Erro: ${err.message}</li>`;
  }
}

document.getElementById('data').addEventListener('change', (e)=> {
  loadAgendamentos(e.target);
});