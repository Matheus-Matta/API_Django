from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Pedido, Progresso
import random
import time
import requests
from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .send import MessageProcessor
from .decorators import token_required
from decouple import config
from .encrypt import cryp_decode
import json
from .db_manage import PedidoManager

def index_api(request):
    return  HttpResponse(f"Essa api está Online!")
    
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
            'name': config('INSTANCE_NAME'),
            'token': config("INSTANCE_TOKEN")
        }
        processor = MessageProcessor(instance)  # Agora você só passa a instância

        # Chamar o método send do MessageProcessor passando o data como **kwargs
        response = processor.send(**data)

        return JsonResponse({'success': 'Mensagem enviada com sucesso', 'response': response}, status=201)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Um erro interno aconteceu', 'details': str(e)}, status=500)    


def avaliacao(request, hash):

    if request.method == 'GET':

        try:
            # Descriptografa o hash
            dados_decodificados = cryp_decode(hash)
            data = {
                'number': dados_decodificados['number'],
                'codigo': dados_decodificados['codigo']
            }
            # Verifica se 'montador' e 'motorista' estão presentes antes de acessá-los
            if 'montador' in dados_decodificados:
                data['montador'] = dados_decodificados['montador']

            if 'motorista' in dados_decodificados:
                data['motorista'] = dados_decodificados['motorista']

            # Renderiza a página com os dados
            pedido = PedidoManager(**data)
            avaliacao = pedido.get_avaliacao(**data)
            if avaliacao:
                return render(request, 'avaliacao/avaliacao.html', {'data': data,'avaliacao': avaliacao})
            return render(request, 'avaliacao/avaliacao.html', {'data': data})
        
        except Exception as e:
            return HttpResponse(f"Erro ao descriptografar: {str(e)}", status=400)
        
    if request.method == 'POST':  
        try:
            data = json.loads(request.body)  # Pega os dados enviados no corpo da requisição

            # Tenta obter o pedido correspondente
            pedido = PedidoManager(**data)
            pedido.insert_avaliacao(**data)
           
            return JsonResponse({'sucesso': 'Avaliação do montador salva com sucesso'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Dados inválidos no corpo da requisição.'}, status=400)
        except Exception as e:
            return JsonResponse({'erro': f'Ocorreu um erro: {str(e)}'}, status=500)

    return HttpResponse("Método não permitido", status=405)
        
    
def tracking(request, hash):
    try:
        # Busca o pedido com base no código de rastreamento fornecido (hash)
        pedido = get_object_or_404(Pedido, tracking=hash)

        # Busca todos os progressos relacionados ao pedido
        progresso = Progresso.objects.filter(pedido=pedido).order_by('-id')

        # Retorna a timeline com os progressos do pedido
        context = {
            'pedido': pedido,
            'progresso': progresso,
        }
        return render(request, 'tracking/timeline.html', context)

    except Pedido.DoesNotExist:
        return HttpResponse("Pedido não encontrado", status=404)