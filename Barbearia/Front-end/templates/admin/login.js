
function fazerLogin() {
  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;

  if (usuario === "admin" && senha === "1234") {
    localStorage.setItem("userLoggedIn", "true");
    window.location.href = "caixa.html";
  } else {
    alert("Usuário ou senha incorretos!");
  }
}
