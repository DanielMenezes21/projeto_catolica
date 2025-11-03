from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProjetoForm
from .models import Projeto
import pandas as pd

def criar_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_projetos')
    else:
        form = ProjetoForm()
    return render(request, 'projetos_form.html', {'form': form})


def listar_projetos(request):
    projetos = Projeto.objects.all()
    return render(request, 'projetos_lista.html', {'projetos': projetos})


def exportar_planilha(request):
    projetos = Projeto.objects.all().values()
    df = pd.DataFrame(list(projetos))

    # Expandir os valores mensais (coluna JSON)
    if 'valores_mensais' in df.columns:
        valores_df = df['valores_mensais'].apply(pd.Series)
        df = pd.concat([df.drop('valores_mensais', axis=1), valores_df], axis=1)

    # Criar o arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="projetos.xlsx"'
    df.to_excel(response, index=False)
    return response

