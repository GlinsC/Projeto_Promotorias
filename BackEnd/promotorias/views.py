from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Promotoria, PromotoriaResolucao, Resolucao
from .permissions import ReadOnlyOrAdminWrite
import json

# Criando View para promotorias
class PromotoriaView(APIView):
    permission_classes = [ReadOnlyOrAdminWrite]

    #Metodo GET para retornar todas as promotorias
    def get(self, request):
        promotoria_data = list(Promotoria.objects.values(
            "id", "nome_promotoria", "entrancia"
        ))
        return JsonResponse({'promotorias': promotoria_data})

    #Metodo POST para criar uma nova promotoria
    def post(self, request):
        data = json.loads(request.body)
        nome_promotoria = data.get('nome_promotoria') or ''
        entrancia = data.get('entrancia') or ''

        promotoria = Promotoria.objects.create(
            nome_promotoria=nome_promotoria,
            entrancia=entrancia
        )
        return JsonResponse({
            'message': 'Requisição POST recebida com sucesso!',
            'promotoria_id': promotoria.id
        })

    #Metodo PUT para atualizar uma promotoria existente
    def put(self, request):
        data = json.loads(request.body)
        promotoria_id = data.get('id')
        nome_promotoria = data.get('nome_promotoria') or ''
        entrancia = data.get('entrancia') or ''

        try:
            promotoria = Promotoria.objects.get(id=promotoria_id)
            promotoria.nome_promotoria = nome_promotoria
            promotoria.entrancia = entrancia
            promotoria.save()
            return JsonResponse({
                'message': 'Requisição PUT recebida com sucesso!',
                'promotoria_id': promotoria.id
            })
        except Promotoria.DoesNotExist:
            return JsonResponse({
                'message': 'Promotoria não encontrada.'
            }, status=404)

    #Metodo DELETE para deletar uma promotoria existente
    def delete(self, request):
        data = json.loads(request.body)
        promotoria_id = data.get('id')

        try:
            promotoria = Promotoria.objects.get(id=promotoria_id)
            promotoria.delete()
            return JsonResponse({
                'message': 'Requisição DELETE recebida com sucesso!'
            })
        except Promotoria.DoesNotExist:
            return JsonResponse({
                'message': 'Promotoria não encontrada.'
            }, status=404)

    def patch(self, request):
        data = json.loads(request.body)
        promotoria_id = data.get('id')
        nome_promotoria = data.get('nome_promotoria')
        entrancia = data.get('entrancia')

        try:
            promotoria = Promotoria.objects.get(id=promotoria_id)
            if nome_promotoria is not None:
                promotoria.nome_promotoria = nome_promotoria
            if entrancia is not None:
                promotoria.entrancia = entrancia
            promotoria.save()
            return JsonResponse({
                'message': 'Requisição PATCH recebida com sucesso!',
                'promotoria_id': promotoria.id
            })
        except Promotoria.DoesNotExist:
            return JsonResponse({
                'message': 'Promotoria não encontrada.'
            }, status=404)

# Criando View para resoluções
class ResolucaoView(APIView):
    permission_classes = [ReadOnlyOrAdminWrite]

    #Metodo GET para retornar todas as resoluções
    def get(self, request):
        resolucao_data = list(Resolucao.objects.values(
            "id", "nome_resolucao", "descricao_resolucao", "prazo_resolucao", "numero_resolucao", "ano_resolucao"
        ))
        return JsonResponse({'resolucoes': resolucao_data})

    #Metodo POST para criar uma nova resolução
    def post(self, request):
        data = json.loads(request.body)
        nome_resolucao = data.get('nome_resolucao')
        descricao_resolucao = data.get('descricao_resolucao') or ''
        prazo_resolucao = data.get('prazo_resolucao') or ''
        numero_resolucao = data.get('numero_resolucao') or ''
        ano_resolucao = data.get('ano_resolucao') or ''

        resolucao = Resolucao.objects.create(
            nome_resolucao=nome_resolucao,
            descricao_resolucao=descricao_resolucao,
            prazo_resolucao=prazo_resolucao,
            numero_resolucao=numero_resolucao,
            ano_resolucao=ano_resolucao
        )
        return JsonResponse({
            'message': 'Requisição POST recebida com sucesso!',
            'resolucao_id': resolucao.id
        })

    #Metodo PUT para atualizar uma resolução existente
    def put(self, request):
        data = json.loads(request.body)
        resolucao_id = data.get('id')
        nome_resolucao = data.get('nome_resolucao')
        descricao_resolucao = data.get('descricao_resolucao') or ''
        prazo_resolucao = data.get('prazo_resolucao') or ''
        numero_resolucao = data.get('numero_resolucao') or ''
        ano_resolucao = data.get('ano_resolucao') or ''

        try:
            resolucao = Resolucao.objects.get(id=resolucao_id)
            resolucao.nome_resolucao = nome_resolucao
            resolucao.descricao_resolucao = descricao_resolucao
            resolucao.prazo_resolucao = prazo_resolucao
            resolucao.numero_resolucao = numero_resolucao
            resolucao.ano_resolucao = ano_resolucao
            resolucao.save()
            return JsonResponse({
                'message': 'Requisição PUT recebida com sucesso!',
                'resolucao_id': resolucao.id
            })
        except Resolucao.DoesNotExist:
            return JsonResponse({
                'message': 'Resolução não encontrada.'
            }, status=404)

    #Metodo DELETE para deletar uma resolução existente
    def delete(self, request):
        data = json.loads(request.body)
        resolucao_id = data.get('id')

        try:
            resolucao = Resolucao.objects.get(id=resolucao_id)
            resolucao.delete()
            return JsonResponse({
                'message': 'Requisição DELETE recebida com sucesso!'
            })
        except Resolucao.DoesNotExist:
            return JsonResponse({
                'message': 'Resolução não encontrada.'
            }, status=404)  

class PromotoriaResolucaoView(APIView):
    permission_classes = [ReadOnlyOrAdminWrite]

    def get(self, request):
        # Retorna todas as relações entre promotorias e resoluções
        relacoes_data = list(PromotoriaResolucao.objects.values(
            "id", "promotoria_id", "resolucao_id", "Unidade"
        ))
        return JsonResponse({'relacoes': relacoes_data})

    def post(self, request):
        # Cria uma nova relação entre promotoria e resolução
        data = json.loads(request.body)
        promotoria_id = data.get('promotoria_id')
        resolucao_id = data.get('resolucao_id')
        unidade = data.get('Unidade') or ''

        try:
            promotoria = Promotoria.objects.get(id=promotoria_id)
            resolucao = Resolucao.objects.get(id=resolucao_id)

            relacao = PromotoriaResolucao.objects.create(
                promotoria=promotoria,
                resolucao=resolucao,
                Unidade=unidade
            )
            return JsonResponse({
                'message': 'Relação criada com sucesso!',
                'relacao_id': relacao.id
            })
        except (Promotoria.DoesNotExist, Resolucao.DoesNotExist):
            return JsonResponse({
                'message': 'Promotoria ou Resolução não encontrada.'
            }, status=404)

    def put(self, request):
         # Atualiza uma relação existente entre promotoria e resolução
        data = json.loads(request.body)
        relacao_id = data.get('id')
        promotoria_id = data.get('promotoria_id')
        resolucao_id = data.get('resolucao_id')
        unidade = data.get('Unidade') or ''

        try:
            relacao = PromotoriaResolucao.objects.get(id=relacao_id)
            promotoria = Promotoria.objects.get(id=promotoria_id)
            resolucao = Resolucao.objects.get(id=resolucao_id)

            relacao.promotoria = promotoria
            relacao.resolucao = resolucao
            relacao.Unidade = unidade
            relacao.save()
            return JsonResponse({
                'message': 'Relação atualizada com sucesso!',
                'relacao_id': relacao.id
            })
        except (PromotoriaResolucao.DoesNotExist, Promotoria.DoesNotExist, Resolucao.DoesNotExist):
            return JsonResponse({
                'message': 'Relação, Promotoria ou Resolução não encontrada.'
            }, status=404)

    def delete(self, request):
        # Deleta uma relação existente entre promotoria e resolução
        data = json.loads(request.body)
        relacao_id = data.get('id')

        try:
            relacao = PromotoriaResolucao.objects.get(id=relacao_id)
            relacao.delete()
            return JsonResponse({
                'message': 'Relação deletada com sucesso!'
                })
        except PromotoriaResolucao.DoesNotExist:
            return JsonResponse({
                'message': 'Relação não encontrada.'
            }, status=404)


