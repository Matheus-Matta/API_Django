from django.shortcuts import render
from django.http import HttpResponse
import random
import time
import requests
from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .send import MessageProcessor
from .decorators import token_required
from decouple import config
def index(request):
    #return  HttpResponse(f"<h1 style='color: green'> Essa api está Online! </h1>")
    """
    View que simula o envio de uma mensagem para a API `send_msg` usando a biblioteca requests.
    """
    try:
        # URL da API para onde vamos enviar os dados
        api_url = 'http://127.0.0.1:8000/api/sendMsg'  # Substitua pelo endpoint correto, se necessário

        # Dados simulados para o envio de mensagem
        data = {
            "number": "5521981345727",
            "nome": "João",
            "status": "p",  # Pode ser 'l', 't', 'n', etc.
            "chaveFiscal": "12345678901234",
            "motorista": "Carlos",
            "desc": "Mesa",
            "dataPrevisao": "2024-09-15",
            'email': 'matheuseduardo3004@gmail.com',
            'codigo': 112233
        }

        headers = {
            'token': config("TOKEN") # Substitua pelo token correto
        }
        # Fazendo a requisição POST para a API send_msg
        response = requests.post(api_url, json=data,headers=headers)

        # Processa a resposta da API
        if response.status_code == 201:
            return HttpResponse(f"Simulação de envio bem-sucedida! Resposta: {response.json()}")
        else:
            return HttpResponse(f"Falha ao enviar mensagem. Status: {response.status_code}, Resposta: {response.text}")

    except Exception as e:
        return HttpResponse(f"Erro durante a simulação: {str(e)}")

def doc(request):
    return render(request, 'doc/doc.html') 

@api_view(['POST'])
@token_required
def send_msg(request):
    try:
        # Obter os dados do corpo da requisição diretamente como kwargs
        data = request.data

        # Instanciar o MessageProcessor
        instance = {
            'name': 'Maxxx-dp1',
            'token': 'xq2yrgebvounsyyrukq6'
        }
        processor = MessageProcessor(instance)  # Agora você só passa a instância

        # Chamar o método send do MessageProcessor passando o data como **kwargs
        response = processor.send(**data)

        return JsonResponse({'success': 'Mensagem enviada com sucesso', 'response': response}, status=201)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Um erro interno aconteceu', 'details': str(e)}, status=500)    
