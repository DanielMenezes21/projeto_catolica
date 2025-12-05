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
            instance = form.save()
            # processar contas e valores enviados via POST
            processar_contas_post(request.POST, instance)
            return redirect('listar_projetos')
    else:
        form = ProjetoForm()
    
    return render(request, 'page/projetos_form.html', {
        'form': form,
        'campos_excluir': CAMPOS_EXCLUIR_MESES,
        'contas_data': []
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
    return create_projetos_excel_response(projetos, filename='PLANEJAMENTO ORÇAMENTÁRIO.xlsx', gestor=gestor, setor=setor, centro_custo=centro_custo)


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
            instance = form.save()
            # remover contas antigas e recriar
            projeto.contas_valores.all().delete()
            processar_contas_post(request.POST, instance)
            return redirect('listar_projetos')
    else:
        form = ProjetoForm(instance=projeto)
    
    # preparar dados das contas para pré-popular o JS
    contas = []
    for pcv in projeto.contas_valores.all():
        contas.append({
            'conta': pcv.conta_contabil,
            'valores': pcv.valores_mensais,
            'total': float(pcv.valor_total),
        })

    return render(request, 'page/projetos_form.html', {
         'form': form,
         'edit': True,
         'projeto': projeto,
         'campos_excluir': CAMPOS_EXCLUIR_MESES,
         'contas_data': contas,
     })


def processar_contas_post(post, projeto_instance):
    """Processa campos do POST com prefixo conta__<idx>__<field> e salva ProjetoContaValor."""
    from .models import ProjetoContaValor
    contas = {}
    for key, val in post.items():
        if not key.startswith('conta__'):
            continue
        parts = key.split('__')
        # espera formato: conta__<idx>__<field>
        if len(parts) < 3:
            continue
        _, idx, field = parts[:3]
        entry = contas.setdefault(idx, {'conta_label': None, 'valores': {}})
        if field == 'label':
            entry['conta_label'] = val
        elif field == 'total':
            # total será calculado a partir dos meses; ignorar ou usar como fallback
            entry['total'] = float(val) if val else 0
        else:
            # campo de mês
            try:
                entry['valores'][field] = float(val) if val else 0
            except Exception:
                entry['valores'][field] = 0

    soma_projeto = 0
    for idx, data in contas.items():
        conta_label = data.get('conta_label') or ''
        valores = data.get('valores', {})
        total = sum([float(v) for v in valores.values()]) if valores else data.get('total', 0)
        ProjetoContaValor.objects.create(
            projeto=projeto_instance,
            conta_contabil=conta_label,
            valores_mensais=valores,
            valor_total=total
        )
        soma_projeto += total

    # atualizar total do projeto
    projeto_instance.valor_total = soma_projeto
    projeto_instance.save()