// Formatação de valores em BRL
function formatBRL(v) {
  try {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
  } catch (e) {
    return 'R$ ' + Number(v).toFixed(2);
  }
}

// Cria bloco de inputs mensais para uma conta
function criarBlocoConta(idx, contaLabel, valoresExistentes) {
  const container = document.createElement('div');
  container.className = 'conta-box';
  container.dataset.idx = idx;

  const header = document.createElement('h4');
  header.textContent = contaLabel;
  container.appendChild(header);

  const meses = [
    'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
  ];

  const grid = document.createElement('div');
  grid.className = 'mes-grid';
  // criar células (6 colunas x 2 linhas visualmente) — grid cuidará do fluxo
  meses.forEach(mes => {
    const cell = document.createElement('div');
    cell.className = 'mes-item';
    const label = document.createElement('label');
    label.style.marginBottom = '4px';
    label.textContent = mes.charAt(0).toUpperCase() + mes.slice(1);
    const inp = document.createElement('input');
    inp.type = 'number';
    inp.step = '0.01';
    inp.min = '0';
    inp.name = `conta__${idx}__${mes}`;
    inp.setAttribute('inputmode', 'decimal');
    inp.style.marginTop = '4px';
    inp.style.padding = '6px';
    inp.style.border = '1px solid #ccc';
    inp.style.borderRadius = '4px';
    cell.appendChild(label);
    cell.appendChild(inp);
    grid.appendChild(cell);
    // prefill
    if (valoresExistentes && valoresExistentes[mes] !== undefined) {
      inp.value = valoresExistentes[mes];
    }
  });

  // total field
  const totalWrapper = document.createElement('p');
  // hidden input for submission, visible span for formatted currency
  const hiddenTotal = document.createElement('input');
  hiddenTotal.type = 'hidden';
  hiddenTotal.name = `conta__${idx}__total`;
  hiddenTotal.value = '0.00';
  const displayTotal = document.createElement('span');
  displayTotal.className = 'subtotal-display';
  displayTotal.style.marginLeft = '6px';
  displayTotal.textContent = 'R$ 0,00';
  totalWrapper.textContent = 'Subtotal:';
  totalWrapper.appendChild(hiddenTotal);
  totalWrapper.appendChild(displayTotal);
  container.appendChild(grid);
  container.appendChild(totalWrapper);

  // hidden field to carry the label (conta identificador)
  const hidden = document.createElement('input');
  hidden.type = 'hidden';
  hidden.name = `conta__${idx}__label`;
  hidden.value = contaLabel;
  container.appendChild(hidden);

  // attach event listeners to compute subtotal
  container.querySelectorAll('input[type="number"]').forEach(inp => {
    inp.addEventListener('input', function() {
      let s = 0;
      container.querySelectorAll('input[type="number"]').forEach(i => { s += parseFloat(i.value) || 0; });
      hiddenTotal.value = s.toFixed(2);
      displayTotal.textContent = formatBRL(s);
      // update project total
      atualizarTotalProjeto();
    });
  });

  return container;
}

function atualizarTotalProjeto() {
  let soma = 0;
  document.querySelectorAll('input[name$="__total"]').forEach(i => { soma += parseFloat(i.value) || 0; });
  const totalField = document.getElementById('id_valor_total');
  if (totalField) totalField.value = soma.toFixed(2);
}

// Setup inicial do formulário
document.addEventListener('DOMContentLoaded', function() {
  // Inicializa Select2 para código do produto
  $('#id_codigo_produto').select2({
    placeholder: 'Selecione as contas...',
    allowClear: true
  });

  // quando a seleção de contas muda, gera blocos
  $('#id_codigo_produto').on('change', function() {
    const sel = $(this).val() || [];
    const container = document.getElementById('contas-container');
    container.innerHTML = '';
    sel.forEach((val, idx) => {
      // tenta achar valores existentes em contas_data
      let existentes = null;
      if (typeof CONTAS_INITIAL !== 'undefined' && CONTAS_INITIAL) {
        for (const c of CONTAS_INITIAL) {
          if (c.conta === val) { existentes = c.valores; break; }
        }
      }
      const bloco = criarBlocoConta(idx, val, existentes);
      container.appendChild(bloco);
      // if existentes, set total (hidden) and display formatted
      if (existentes) {
        let s = 0; for (const m in existentes) s += parseFloat(existentes[m]) || 0;
        const hiddenTotalInput = bloco.querySelector('input[name$="__total"]');
        const displaySpan = bloco.querySelector('.subtotal-display');
        if (hiddenTotalInput) hiddenTotalInput.value = s.toFixed(2);
        if (displaySpan) displaySpan.textContent = formatBRL(s);
      }
    });
    atualizarTotalProjeto();
  });

  // pre-popular se estivermos editando
  if (typeof CONTAS_INITIAL !== 'undefined' && CONTAS_INITIAL && CONTAS_INITIAL.length > 0) {
    // set selected options in select2
    const codes = CONTAS_INITIAL.map(c => c.conta);
    $('#id_codigo_produto').val(codes).trigger('change');
  }

  // Setup do display do total do projeto em formato moeda
  setupTotalDisplay();
});

function setupTotalDisplay() {
  const rawTotal = document.getElementById('id_valor_total');
  if (rawTotal) {
    // manter valor para submissão, esconder input visível
    try { rawTotal.type = 'hidden'; } catch (e) { }
    const span = document.createElement('span');
    span.id = 'valor_total_display';
    span.style.marginLeft = '8px';
    span.textContent = formatBRL(parseFloat(rawTotal.value) || 0);
    rawTotal.parentNode.appendChild(span);
  }

  // atualizarTotalProjeto já soma os inputs hidden __total; aqui só reforçamos a display
  const originalAtualizar = window.atualizarTotalProjeto;
  if (typeof originalAtualizar === 'function') {
    window.atualizarTotalProjeto = function() {
      originalAtualizar();
      const raw = document.getElementById('id_valor_total');
      const disp = document.getElementById('valor_total_display');
      if (raw && disp) disp.textContent = formatBRL(parseFloat(raw.value) || 0);
    };
  }
}
