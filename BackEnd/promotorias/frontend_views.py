import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def _is_staff(user):
    return user.is_authenticated and user.is_staff


def _api_base_url():
    base_url = os.getenv('BI_API_URL', 'http://127.0.0.1:8000/api').rstrip('/')
    if base_url.endswith('/promotorias'):
        return base_url[:-len('/promotorias')]
    return base_url


def _api_request(request, endpoint, method='GET', payload=None, retry=True):
    access_token = request.session.get('jwt_access')
    headers = {'Content-Type': 'application/json'}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    api_request = Request(
        f'{_api_base_url()}/{endpoint.lstrip("/")}',
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(api_request, timeout=10) as response:
            content = response.read()
            return json.loads(content) if content else {}
    except HTTPError as error:
        if error.code == 401 and retry and request.session.get('jwt_refresh'):
            try:
                with urlopen(Request(
                    f'{_api_base_url().rsplit("/api", 1)[0]}/api/token/refresh/',
                    data=json.dumps({
                        'refresh': request.session['jwt_refresh'],
                    }).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST',
                ), timeout=10) as refresh_response:
                    refresh_data = json.loads(refresh_response.read())
                request.session['jwt_access'] = refresh_data['access']
                return _api_request(request, endpoint, method, payload, retry=False)
            except (HTTPError, KeyError, URLError, json.JSONDecodeError):
                logout(request)
                raise

        detail = error.read().decode('utf-8', errors='replace')
        raise RuntimeError(detail or f'API retornou HTTP {error.code}') from error
    except (URLError, json.JSONDecodeError) as error:
        raise RuntimeError('Não foi possível acessar a API Django.') from error


def _painel_data(request):
    promotorias = _api_request(request, 'promotorias/')['promotorias']
    resolucoes = _api_request(request, 'resolucoes/')['resolucoes']
    relacoes = _api_request(request, 'relacoes/')['relacoes']
    promotoria_by_id = {item['id']: item for item in promotorias}
    resolucao_by_id = {item['id']: item for item in resolucoes}
    rows = []

    for relacao in relacoes:
        promotoria = promotoria_by_id.get(relacao['promotoria_id'], {})
        resolucao = resolucao_by_id.get(relacao['resolucao_id'], {})
        rows.append({
            'id': promotoria.get('id'),
            'nome_promotoria': promotoria.get('nome_promotoria', ''),
            'entrancia': promotoria.get('entrancia', ''),
            'relacao_id': relacao['id'],
            'resolucao': resolucao.get('nome_resolucao', ''),
            'unidade': relacao.get('Unidade', ''),
        })

    relation_promotoria_ids = {row['id'] for row in rows}
    rows.extend({
        'id': item['id'],
        'nome_promotoria': item['nome_promotoria'],
        'entrancia': item['entrancia'],
        'relacao_id': None,
        'resolucao': 'Nenhuma resolução vinculada',
        'unidade': '',
    } for item in promotorias if item['id'] not in relation_promotoria_ids)
    return promotorias, resolucoes, rows


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('painel')
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Usuário ou senha inválidos.')
        elif not user.is_staff:
            messages.error(request, 'Este usuário não tem permissão para acessar o painel.')
        else:
            token_serializer = TokenObtainPairSerializer(
                data={'username': username, 'password': password}
            )
            token_serializer.is_valid(raise_exception=True)

            login(request, user)
            request.session['jwt_access'] = str(token_serializer.validated_data['access'])
            request.session['jwt_refresh'] = str(token_serializer.validated_data['refresh'])
            request.session['usuario'] = {
                'id': user.id,
                'username': user.get_username(),
                'email': user.email,
                'is_staff': user.is_staff,
            }
            request.session.set_expiry(1800)
            return redirect('painel')

    return render(request, 'promotorias/login.html')


@user_passes_test(_is_staff, login_url='login')
def painel_view(request):
    try:
        promotorias, resolucoes, rows = _painel_data(request)
    except RuntimeError as error:
        messages.error(request, str(error))
        promotorias, resolucoes, rows = [], [], []

    query = request.GET.get('q', '').strip().lower()
    if query:
        rows = [row for row in rows if query in row['nome_promotoria'].lower()]

    page_obj = Paginator(rows, 20).get_page(request.GET.get('page'))
    entrancias = sorted({
        promotoria['entrancia'].strip()
        for promotoria in promotorias
        if promotoria.get('entrancia', '').strip()
    })

    return render(request, 'promotorias/painel.html', {
        'usuario': request.session.get('usuario', {}),
        'page_obj': page_obj,
        'promotorias': promotorias,
        'resolucoes': resolucoes,
        'entrancias': entrancias,
        'query': request.GET.get('q', ''),
    })


@user_passes_test(_is_staff, login_url='login')
@require_http_methods(['POST'])
def salvar_promotoria_view(request):
    data = {
        'nome_promotoria': request.POST.get('nome_promotoria', '').strip(),
        'entrancia': request.POST.get('entrancia', '').strip(),
    }
    promotoria_id = request.POST.get('promotoria_id')
    try:
        if promotoria_id:
            _api_request(request, 'promotorias/', 'PUT', {**data, 'id': int(promotoria_id)})
            message = 'Promotoria atualizada com sucesso.'
        else:
            result = _api_request(request, 'promotorias/', 'POST', data)
            promotoria_id = result['promotoria_id']
            message = 'Promotoria criada com sucesso.'

        resolucao_id = request.POST.get('resolucao_id')
        if resolucao_id:
            _api_request(request, 'relacoes/', 'POST', {
                'promotoria_id': int(promotoria_id),
                'resolucao_id': int(resolucao_id),
                'Unidade': request.POST.get('unidade', '').strip(),
            })
            message += ' Resolução vinculada.'
        messages.success(request, message)
    except (RuntimeError, KeyError, ValueError) as error:
        messages.error(request, f'Não foi possível salvar: {error}')
    return redirect('painel')


@user_passes_test(_is_staff, login_url='login')
@require_http_methods(['POST'])
def excluir_promotoria_view(request, promotoria_id):
    try:
        _api_request(request, 'promotorias/', 'DELETE', {'id': promotoria_id})
        messages.success(request, 'Promotoria excluída com sucesso.')
    except RuntimeError as error:
        messages.error(request, f'Não foi possível excluir: {error}')
    return redirect('painel')


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('login')
