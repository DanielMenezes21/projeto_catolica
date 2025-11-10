from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProjetoForm
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
    return render(request, 'page/projetos_form.html', {'form': form})


def listar_projetos(request):
    projetos = Projeto.objects.all()
    return render(request, 'page/projetos_lista.html', {'projetos': projetos})


def exportar_planilha(request):
    # Usamos o helper que cria um arquivo Excel estilizado com openpyxl
    projetos = Projeto.objects.all()
    return create_projetos_excel_response(projetos, filename='projetos.xlsx')

