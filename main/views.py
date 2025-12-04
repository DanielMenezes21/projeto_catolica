from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProjetoForm, CAMPOS_EXCLUIR_MESES
from .models import Projeto
from .excel_file.excel_constructor import create_projetos_excel_response
import pandas as pd

def criar_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_projetos')
    else:
        form = ProjetoForm()
    
    return render(request, 'page/projetos_form.html', {
        'form': form,
        'campos_excluir': CAMPOS_EXCLUIR_MESES
    })


def listar_projetos(request):
    projetos = Projeto.objects.all()
    return render(request, 'page/projetos_lista.html', {'projetos': projetos})


def exportar_planilha(request):
    # Usamos o helper que cria um arquivo Excel estilizado com openpyxl
    projetos = Projeto.objects.all()
    # ler nome do gestor e setor via query params (se fornecidos)
    gestor = request.GET.get('nome_gestor') or request.GET.get('gestor')
    setor = request.GET.get('setor')
    centro_custo = request.GET.get('centro_custo')
    return create_projetos_excel_response(projetos, filename='projetos.xlsx', gestor=gestor, setor=setor, centro_custo=centro_custo)


def deletar_projeto(request, projeto_id):
    try:
        projeto = Projeto.objects.get(id=projeto_id)
        projeto.delete()
    except Projeto.DoesNotExist:
        pass
    return redirect('listar_projetos')

def editar_projeto(request, projeto_id):
    try:
        projeto = Projeto.objects.get(id=projeto_id)
    except Projeto.DoesNotExist:
        return redirect('listar_projetos')
    
    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            return redirect('listar_projetos')
    else:
        form = ProjetoForm(instance=projeto)
    
    return render(request, 'page/projetos_form.html', {
         'form': form,
         'edit': True,
         'projeto': projeto,
         'campos_excluir': CAMPOS_EXCLUIR_MESES
     })