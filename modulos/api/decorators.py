from functools import wraps
from django.http import JsonResponse
from decouple import config
def token_required(view_func):
    """
    Decorator para verificar o token de segurança em views de API.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.headers.get('token')
        if not token or token != config("TOKEN"):
            return JsonResponse({'error': 'Token de segurança inválido ou ausente.'}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view