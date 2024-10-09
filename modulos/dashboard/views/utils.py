import requests
from django.contrib import messages
from django.utils import timezone
import calendar

def call_api(request, method, url, data=None):
    """
    Função genérica para realizar requisições à API, com tratamento de erros.
    """
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError("Método HTTP inválido")

        if response.status_code not in [200, 201]:
            print(f"Erro na resposta da API: {response.status_code} - {response.text}")
            messages.error(request, f"Erro: {response.status_code} - {response.text}")
            return None

        return response.json()

    except Exception as e:
        print(f"[call_api] Error: {e}")
        messages.error(request, f"Erro ao tentar acessar a API: {str(e)}")
        return None
    
def get_days_range_array(dataInicio, dataFim):
    delta = (dataFim - dataInicio).days + 1
    array = [0] * delta
    return array