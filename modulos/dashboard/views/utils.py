import requests
from django.contrib import messages

def call_api(request, method, url, data=None):
    """
    Função genérica para realizar requisições à API.
    """
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError("Método HTTP inválido")

        if response.status_code not in [200, 201]:
            messages.error(request, f"Erro: {response.status_code} - {response.text}")
            return None

        return response.json()

    except Exception as e:
        print(f"[call_api] Error: {e}")
        messages.error(request, f"Erro ao tentar acessar a API: {str(e)}")
        return None