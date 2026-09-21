import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Promotoria, Resolucao


class PromotoriaApiTests(TestCase):
	url = '/promotorias/'

	def setUp(self):
		self.client = APIClient()
		self.admin = get_user_model().objects.create_user(
			username='admin',
			password='senha-segura',
			is_staff=True,
		)
		self.client.force_authenticate(user=self.admin)

	def test_post_requires_authentication(self):
		response = APIClient().post(
			self.url,
			data=json.dumps({'nome_promotoria': 'Promotoria sem CSRF'}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 401)

	def test_post_creates_promotoria(self):
		response = self.client.post(
			self.url,
			data=json.dumps({
				'nome_promotoria': 'Promotoria Central',
				'descricao_promotoria': 'Descricao',
				'entrancia': 'Final',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Promotoria.objects.count(), 1)
		self.assertEqual(response.json()['promotoria_id'], Promotoria.objects.get().id)

	def test_get_returns_promotorias(self):
		promotoria = Promotoria.objects.create(nome_promotoria='Promotoria Central')

		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['promotorias'][0]['id'], promotoria.id)

	def test_put_updates_promotoria(self):
		promotoria = Promotoria.objects.create(nome_promotoria='Nome antigo')

		response = self.client.put(
			self.url,
			data=json.dumps({
				'id': promotoria.id,
				'nome_promotoria': 'Nome atualizado',
				'descricao_promotoria': 'Nova descricao',
				'entrancia': 'Inicial',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		promotoria.refresh_from_db()
		self.assertEqual(promotoria.nome_promotoria, 'Nome atualizado')

	def test_delete_removes_promotoria(self):
		promotoria = Promotoria.objects.create(nome_promotoria='Para remover')

		response = self.client.delete(
			self.url,
			data=json.dumps({'id': promotoria.id}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Promotoria.objects.filter(id=promotoria.id).exists())


class ResolucaoApiTests(TestCase):
	url = '/promotorias/resolucoes/'

	def setUp(self):
		self.client = APIClient()
		self.admin = get_user_model().objects.create_user(
			username='admin-resolucoes',
			password='senha-segura',
			is_staff=True,
		)
		self.client.force_authenticate(user=self.admin)

	def test_post_requires_authentication(self):
		response = APIClient().post(
			self.url,
			data=json.dumps({
				'nome_resolucao': 'Resolucao 001',
				'descricao_resolucao': 'Descricao',
				'prazo_resolucao': '30 dias',
				'numero_resolucao': '001',
				'ano_resolucao': '2026',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 401)

	def test_get_returns_resolucoes(self):
		resolucao = Resolucao.objects.create(nome_resolucao='Resolucao 001')

		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['resolucoes'][0]['id'], resolucao.id)

	def test_put_updates_resolucao(self):
		resolucao = Resolucao.objects.create(nome_resolucao='Nome antigo')

		response = self.client.put(
			self.url,
			data=json.dumps({
				'id': resolucao.id,
				'nome_resolucao': 'Nome atualizado',
				'descricao_resolucao': 'Nova descricao',
				'prazo_resolucao': '60 dias',
				'numero_resolucao': '002',
				'ano_resolucao': '2026',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		resolucao.refresh_from_db()
		self.assertEqual(resolucao.nome_resolucao, 'Nome atualizado')

	def test_delete_removes_resolucao(self):
		resolucao = Resolucao.objects.create(nome_resolucao='Para remover')

		response = self.client.delete(
			self.url,
			data=json.dumps({'id': resolucao.id}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Resolucao.objects.filter(id=resolucao.id).exists())

# Create your tests here.
