from django.urls import path
from . import views

urlpatterns = [
    path('promotorias/', views.PromotoriaView.as_view(), name='promotoria'),
    path('resolucoes/', views.ResolucaoView.as_view(), name='resolucao'),
    path('relacoes/', views.PromotoriaResolucaoView.as_view(), name='promotoria_resolucao'),
    path('promotorias/<int:id>/', views.PromotoriaView.as_view(), name='promotoria_detail'),
]   