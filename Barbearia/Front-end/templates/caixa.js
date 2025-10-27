// caixa.js
 
async function loadCaixa(){
  try{
    const res = await fetch('/api/caixa');
    const data = await res.json();
    document.getElementById('ganho_dia').textContent = 'R$ ' + Number(data.ganho_dia).toFixed(2);
    document.getElementById('ganho_mes').textContent = 'R$ ' + Number(data.ganho_mes).toFixed(2);
    document.getElementById('media_mensal').textContent = 'R$ ' + Number(data.media_mensal).toFixed(2);
  }catch(e){
    console.error(e);
  }
}
loadCaixa();