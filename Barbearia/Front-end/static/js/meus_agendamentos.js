document.addEventListener("DOMContentLoaded", () => {
  const btnBuscar = document.getElementById("btnBuscar");
  const telefoneInput = document.getElementById("telefone");
  const lista = document.getElementById("listaAgendamentos");

  // Buscar agendamentos do cliente
  if (btnBuscar) {
    btnBuscar.addEventListener("click", async () => {
      const telefone = telefoneInput.value.trim();
      if (!telefone) {
        alert("Digite seu telefone para buscar os agendamentos!");
        return;
      }

      try {
        const resp = await fetch(`/api/agendamentos?telefone=${telefone}`);
        const data = await resp.json();

        lista.innerHTML = ""; // limpa a lista

        if (!data.agendamentos || data.agendamentos.length === 0) {
          lista.innerHTML = "<p>Nenhum agendamento encontrado.</p>";
          return;
        }

        data.agendamentos.forEach(a => {
          const item = document.createElement("div");
          item.classList.add("agendamento");
          item.innerHTML = `
            <p><strong>Serviço:</strong> ${a.servico}</p>
            <p><strong>Data:</strong> ${a.data_hora}</p>
            <p><strong>Preço:</strong> R$ ${a.preco.toFixed(2)}</p>
            <button class="btnCancelar" data-id="${a.id}">❌ Cancelar</button>
          `;
          lista.appendChild(item);
        });

        // Botões de cancelamento
        document.querySelectorAll(".btnCancelar").forEach(btn => {
          btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");
            if (!confirm("Deseja cancelar este agendamento?")) return;

            try {
              const resp = await fetch(`/api/agendamentos/${id}`, {
                method: "DELETE"
              });

              const result = await resp.json();
              alert(result.message || "Agendamento cancelado!");
              btn.closest(".agendamento").remove();
            } catch (error) {
              alert("Erro ao cancelar o agendamento.");
              console.error(error);
            }
          });
        });

      } catch (error) {
        console.error("Erro ao buscar agendamentos:", error);
        alert("Erro ao buscar agendamentos. Tente novamente.");
      }
    });
  }
});
