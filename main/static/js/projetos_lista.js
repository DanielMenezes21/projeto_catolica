// Setup da página de listagem de projetos
document.addEventListener('DOMContentLoaded', function() {
  // preenche o dropdown de centro de custo a partir do JSON
  fetch('/static/data/centro_custo.json')
    .then(res => res.json())
    .then(list => {
      const sel = document.getElementById('centro_custo');
      if (sel) {
        list.forEach(item => {
          const opt = document.createElement('option');
          opt.value = item.code + ' - ' + item.name;
          opt.textContent = item.code + ' - ' + item.name;
          sel.appendChild(opt);
        });
      }
    })
    .catch(err => console.error('Erro carregando centros de custo:', err));

  // Quando clicar em exportar, pega os valores dos inputs e redireciona com query params
  const exportLink = document.getElementById('export-link');
  if (exportLink) {
    exportLink.addEventListener('click', function(e) {
      e.preventDefault();
      const gestor = encodeURIComponent(document.getElementById('nome_gestor').value || '');
      const setor = encodeURIComponent(document.getElementById('setor').value || '');
      const centro = encodeURIComponent(document.getElementById('centro_custo').value || '');
      
      // Tenta descobrir a URL de exportação a partir do atributo data ou da página
      let exportUrl = exportLink.getAttribute('data-export-url') || '/main/exportar-planilha/';
      
      // Se o navegador está em uma página que tem a URL no contexto, usa
      if (typeof EXPORT_URL !== 'undefined') {
        exportUrl = EXPORT_URL;
      }
      
      const sep = exportUrl.includes('?') ? '&' : '?';
      window.location.href = exportUrl + sep + 'nome_gestor=' + gestor + '&setor=' + setor + '&centro_custo=' + centro;
    });
  }
});

