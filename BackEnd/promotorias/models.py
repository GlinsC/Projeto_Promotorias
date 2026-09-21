from django.db import models

# Create your models here.
class Promotoria(models.Model):
    nome_promotoria = models.CharField(max_length=100)
    entrancia = models.CharField(max_length=50, blank=True)

class Resolucao(models.Model):
    nome_resolucao = models.CharField(max_length=100)
    descricao_resolucao = models.TextField(blank=True)
    prazo_resolucao = models.CharField(max_length=100, blank=True)
    numero_resolucao = models.CharField(max_length=50, blank=True)
    ano_resolucao = models.CharField(max_length=4, blank=True)

class PromotoriaResolucao(models.Model):
    promotoria = models.ForeignKey(Promotoria, on_delete=models.CASCADE)
    resolucao = models.ForeignKey(Resolucao, on_delete=models.CASCADE)
    Unidade = models.CharField(max_length=100, blank=True)

class usuario(models.Model):
    nome_usuario = models.CharField(max_length=100)
    email_usuario = models.EmailField(unique=True)
    senha_usuario = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)


    

