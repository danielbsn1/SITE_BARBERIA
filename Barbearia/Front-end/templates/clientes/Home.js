//home.js//
import { gerarHome } from '../Front-end/templates/Home.js';
gerarHome();
 document.title = "Barbearia - Home";
import '../Front-end/styles/home.css';
// pagina inicial da barbearia
   function gerarHome() {
    const main = document.querySelector('main');
    main.innerHTML = `
    <section class="home">
        <h1>Bem-vindo à Barbearia</h1>
        <p>Seu estilo, nossa paixão.</p>
        <img src="../Front-end/assets/barbearia.jpg" alt="Imagem da Barbearia">
    </section>
    `;
}


