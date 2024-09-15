import requests
from celery import shared_task
import time
from decouple import config
import random

@shared_task(rate_limit='1/m')
def send_message(instance, message, number):
    #sleep = random.randint(int(config('MESSAGE_TIMEOUT_START')), int(config('MESSAGE_TIMEOUT_END')))
    #time.sleep(sleep)
    """
    Envia uma mensagem usando uma API de mensagens.

    Args:
    - instance: Um dicionário contendo o 'name' e 'token' da instância.
    - message: A mensagem de texto a ser enviada.
    - number: O número de telefone para o qual a mensagem será enviada.

    Returns:
    - dict: Resposta da API ou um erro.
    """
    url = f"https://api.star.dev.br/message/sendText/{instance['name']}"
    headers = {
        'apikey': instance['token']
    }
    data = {
        'number': number,
        'options': {
            'delay': 2300,
            'presence': 'composing',
            'linkPreview': False
        },
        'textMessage': {
            'text': message
        }
    }

    try:
        # Faz a requisição POST para o endpoint da API
        response = requests.post(url, json=data, headers=headers)
        
        # Verifica se a resposta é bem-sucedida
        response.raise_for_status()  # Levanta uma exceção se o código de status for >= 400
        
        # Retorna os dados da resposta
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao enviar msg: {http_err}")
        return {'error': str(http_err)}
    except Exception as err:
        print(f"Erro ao enviar msg: {err}")
        return {'error': str(err)}
