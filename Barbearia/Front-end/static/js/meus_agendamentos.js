document.addEventListener('DOMContentLoaded', function() {
    const btnBuscar = document.getElementById('btnBuscar');
    const telefoneInput = document.getElementById('telefone');
    const listaDiv = document.getElementById('listaAgendamentos');

    async function buscarAgendamentos() {
        const telefone = telefoneInput.value.trim();
        if (!telefone) {
            alert('Digite um telefone para buscar');
            return;
        }

        try {
            const response = await fetch(`/api/agendamentos/cliente/${telefone}`);
            const data = await response.json();

            listaDiv.innerHTML = '';  

            if (!data.agendamentos || data.agendamentos.length === 0) {
                listaDiv.innerHTML = '<p class="msg">Nenhum agendamento encontrado.</p>';
                return;
            }

            data.agendamentos.forEach(ag => {
                const div = document.createElement('div');
                div.className = 'agendamento-item';
                div.setAttribute('data-agendamento-id', ag.id);
                
                const dataFormatada = new Date(ag.data_hora).toLocaleString('pt-BR');
                
                div.innerHTML = `
                    <p><strong>Data:</strong> ${dataFormatada}</p>
                    <p><strong>Serviço:</strong> ${ag.servico}</p>
                    <p><strong>Valor:</strong> R$ ${Number(ag.preco).toFixed(2)}</p>
                    <button onclick="cancelarAgendamento(${ag.id})">Cancelar</button>
                `;
                
                listaDiv.appendChild(div);
            });
        } catch (error) {
            console.error('Erro:', error);
            listaDiv.innerHTML = '<p class="erro">Erro ao buscar agendamentos.</p>';
        }
    }

    async function cancelarAgendamento(id) {
        if (!confirm('Tem certeza que deseja cancelar este agendamento?')) return;

        try {
            const response = await fetch(`/api/agendamentos/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                
                const elemento = document.querySelector(`[data-agendamento-id="${id}"]`);
                if (elemento) {
                    elemento.remove();
                    
                    // Se não houver mais agendamentos, mostra mensagem
                    if (listaDiv.children.length === 0) {
                        listaDiv.innerHTML = '<p class="msg">Nenhum agendamento encontrado.</p>';
                    }
                }
                alert('Agendamento cancelado com sucesso!');
            } else {
                throw new Error('Erro ao cancelar agendamento');
            }
        } catch (error) {
            alert('Erro ao cancelar agendamento: ' + error.message);
        }
    }

    // Evento de clique no botão buscar
    btnBuscar.addEventListener('click', buscarAgendamentos);

    // Evento de pressionar Enter no input
    telefoneInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            buscarAgendamentos();
        }
    });

    // Expõe função para o onclick do botão
    window.cancelarAgendamento = cancelarAgendamento;
});
