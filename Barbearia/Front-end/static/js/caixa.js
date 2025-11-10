document.addEventListener("DOMContentLoaded", () => {
    const totalElem = document.getElementById("total");
    const valorInput = document.getElementById("valor");
    const btnAdd = document.getElementById("btnAdicionar");
    const btnFechar = document.getElementById("btnFechar");
    const mensagem = document.getElementById("msg"); // Alterado para 'msg' para manter consistência

    function mostrarMensagem(texto, tipo = 'erro') {
        if (!mensagem) return;
        
        mensagem.textContent = texto;
        mensagem.className = `mensagem ${tipo}`;
        mensagem.style.display = 'block';
        
        if (tipo === 'sucesso') {
            setTimeout(() => {
                mensagem.style.display = 'none';
            }, 3000);
        }
    }

    async function carregarSaldo() {
        try {
            const res = await fetch('/api/caixa/saldo');
            if (!res.ok) throw new Error('Erro ao carregar saldo');
            
            const data = await res.json();
            document.getElementById('saldoAtual').textContent = 
                `R$ ${Number(data.saldo).toFixed(2)}`;
        } catch (err) {
            console.error(err);
            mostrarMensagem('Erro ao carregar saldo');
        }
    }

    async function adicionarValor() {
        const valor = Number(valorInput.value);
        
        if (!valor || valor <= 0) {
            mostrarMensagem('Digite um valor válido');
            return;
        }

        try {
            const res = await fetch('/api/caixa/adicionar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ valor })
            });

            if (!res.ok) throw new Error('Erro ao adicionar valor');
            
            const data = await res.json();
            document.getElementById('saldoAtual').textContent = 
                `R$ ${Number(data.saldo).toFixed(2)}`;
            
            valorInput.value = '';
            mostrarMensagem('Valor adicionado com sucesso!', 'sucesso');
        } catch (err) {
            console.error(err);
            mostrarMensagem('Erro ao adicionar valor');
        }
    }

    async function fecharCaixa() {
        if (!confirm('Tem certeza que deseja fechar o caixa? O saldo será zerado.')) {
            return;
        }

        try {
            const res = await fetch('/api/caixa/fechar', {
                method: 'POST'
            });

            if (!res.ok) throw new Error('Erro ao fechar caixa');
            
            const data = await res.json();
            document.getElementById('saldoAtual').textContent = 'R$ 0,00';
            mostrarMensagem(`Caixa fechado! Total: R$ ${Number(data.total).toFixed(2)}`, 'sucesso');
        } catch (err) {
            console.error(err);
            mostrarMensagem('Erro ao fechar caixa');
        }
    }

    // Anexa eventos aos botões
    if (btnAdd) btnAdd.addEventListener('click', adicionarValor);
    if (btnFechar) btnFechar.addEventListener('click', fecharCaixa);

    // Expõe funções globalmente para uso em onclick
    window.adicionarValor = adicionarValor;
    window.fecharCaixa = fecharCaixa;

    // Carrega saldo inicial
    carregarSaldo();
});
