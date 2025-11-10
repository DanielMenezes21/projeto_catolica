from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

# Ordem dos meses (mantém consistência)
MESES_ORDEM = [
    'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
]


def create_projetos_excel_response(projetos, filename='projetos.xlsx'):
    """Cria um arquivo Excel estilizado a partir de uma queryset de Projetos.

    Args:
        projetos: iterable de objetos Projeto (model instances) com atributos
                  id, nome_projeto, codigo_produto e valores_mensais (dict).
        filename: nome do arquivo gerado.

    Retorna:
        HttpResponse pronto para download contendo o arquivo .xlsx.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'Projetos'

    # Estilos reutilizáveis
    title_font = Font(size=14, bold=True)
    header_font = Font(bold=True)
    center_align = Alignment(horizontal='center', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')
    thin = Side(border_style='thin', color='000000')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_fill = PatternFill(start_color='FFEEEEEE', end_color='FFEEEEEE', fill_type='solid')

    # Cabeçalho/título mesclado
    total_cols = 3 + len(MESES_ORDEM)  # ID, Nome, Código + meses
    last_col = get_column_letter(total_cols)
    ws.merge_cells(f'A1:{last_col}1')
    ws['A1'] = 'Relatório de Projetos'
    ws['A1'].font = title_font
    ws['A1'].alignment = center_align

    # Cabeçalhos das colunas (linha 2)
    headers = ['ID', 'Nome do Projeto', 'Código do Produto'] + [m.title() for m in MESES_ORDEM]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = border

    # Linhas de dados (a partir da linha 3)
    row = 3
    for p in projetos:
        # tenta obter valores_mensais; suporta tanto dict quanto None
        valores = getattr(p, 'valores_mensais', None) or {}

        ws.cell(row=row, column=1, value=getattr(p, 'id', ''))
        ws.cell(row=row, column=2, value=getattr(p, 'nome_projeto', ''))
        ws.cell(row=row, column=3, value=getattr(p, 'codigo_produto', ''))

        # Aplica borda e alinhamento básicos nas 3 primeiras colunas
        for c in range(1, 4):
            cell = ws.cell(row=row, column=c)
            cell.border = border
            cell.alignment = Alignment(vertical='center')

        # Valores por mês
        for m_idx, mes in enumerate(MESES_ORDEM, start=4):
            val = valores.get(mes)
            cell = ws.cell(row=row, column=m_idx)
            if val is not None:
                try:
                    cell.value = float(val)
                    # Formato de número com R$ (pt-br style)
                    cell.number_format = 'R$ #,##0.00'
                    cell.alignment = right_align
                except Exception:
                    cell.value = val
            cell.border = border

        row += 1

    # Ajustar larguras de coluna para ficar legível
    col_widths = {
        1: 8,   # ID
        2: 30,  # Nome do Projeto
        3: 18,  # Código
    }
    for i in range(4, total_cols + 1):
        col_widths[i] = 15

    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Gerar arquivo na memória
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    response = HttpResponse(
        stream.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
