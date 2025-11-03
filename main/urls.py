from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_projetos, name='listar_projetos'),
    path('novo/', views.criar_projeto, name='criar_projeto'),
    path('exportar/', views.exportar_planilha, name='exportar_planilha'),
]

