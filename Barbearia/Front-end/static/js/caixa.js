document.addEventListener("DOMContentLoaded", () => {
  const totalElem = document.getElementById("total");
  const valorInput = document.getElementById("valor");
  const btnAdd = document.getElementById("btnAdicionar");
  const btnFechar = document.getElementById("btnFechar");
  const mensagem = document.getElementById("mensagem");

  async function atualizarTotal() {
    const res = await fetch("/api/caixa");
    const data = await res.json();
    totalElem.textContent = `Total no Caixa: R$ ${data.valor_total.toFixed(2)}`;
  }

  btnAdd.addEventListener("click", async () => {
    const valor = parseFloat(valorInput.value);
    if (isNaN(valor) || valor <= 0) {
      mensagem.textContent = "Digite um valor válido!";
      return;
    }

    await fetch("/api/caixa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ valor })
    });

    valorInput.value = "";
    mensagem.textContent = "Valor adicionado!";
    atualizarTotal();
  });

  btnFechar.addEventListener("click", async () => {
    await fetch("/api/caixa", { method: "DELETE" });
    mensagem.textContent = "Caixa fechado e zerado!";
    atualizarTotal();
  });

  atualizarTotal();
});
