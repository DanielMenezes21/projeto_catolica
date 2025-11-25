import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from openpyxl import load_workbook

MESES_ORDEM = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def create_projetos_excel_response(projetos, filename="projetos.xlsx"):

    template_path = os.path.join(
        settings.BASE_DIR,
        "main",
        "excel_file",
        "modelo_projetos.xlsx"
    )

    wb = load_workbook(template_path)

    ws_proj = wb["Projetos"]
    ws_orc = wb["Orçamento"]

    # ======================================================================
    # ABA PROJETOS
    # ======================================================================
    LINHA_PROJ = 5  # onde começam os projetos

    # ⚠️ Ajuste se desejar: valores fixos no cabeçalho
    # ws_proj["B2"] = "GESTOR EXEMPLO"
    # ws_proj["D2"] = "SETOR EXEMPLO"

    linha_p = LINHA_PROJ

    for p in projetos:

        valores = p.valores_mensais or {}

        # Nome do projeto
        ws_proj[f"A{linha_p}"] = p.nome_projeto

        # Objetivo / Justificativa → supondo que está em "objetivo" no model
        try:
            ws_proj[f"B{linha_p}"] = p.objetivo
        except:
            ws_proj[f"B{linha_p}"] = ""

        # Recorrência
        ws_proj[f"C{linha_p}"] = "Sim" if p.e_recorrente else "Não"

        # Obrigação Legal
        ws_proj[f"D{linha_p}"] = "Sim" if p.obrigacao_legal else "Não"

        # Valor total
        ws_proj[f"E{linha_p}"] = p.valor_total

        linha_p += 1

    # ======================================================================
    # ABA ORÇAMENTO
    # ======================================================================
    LINHA_ORC = 4

    linha_o = LINHA_ORC

    for p in projetos:

        valores = p.valores_mensais or {}

        # Nome do Projeto
        ws_orc[f"A{linha_o}"] = p.nome_projeto

        # Tipo de despesa
        ws_orc[f"B{linha_o}"] = p.tipo_conta

        # Conta contábil (código do produto)
        ws_orc[f"C{linha_o}"] = p.codigo_produto

        # Meses (D → O)
        col_base = 4  # coluna D = 4
        for i, mes in enumerate(MESES_ORDEM):
            col = col_base + i
            val = valores.get(mes)
            ws_orc.cell(row=linha_o, column=col).value = float(val) if val else 0

        # Total na coluna P
        ws_orc[f"P{linha_o}"] = p.valor_total

        linha_o += 1

    # ======================================================================
    # RETORNO DO ARQUIVO GERADO
    # ======================================================================
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    response = HttpResponse(
        stream.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response
