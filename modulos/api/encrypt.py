import json
import hashlib
import base64
from cryptography.fernet import Fernet
from django.conf import settings

# Derivar uma chave de encriptação a partir da SECRET_KEY do Django
def get_fernet_key():
    secret_key = settings.SECRET_KEY.encode()
    digest = hashlib.sha256(secret_key).digest()
    return Fernet(base64.urlsafe_b64encode(digest))

cipher_suite = get_fernet_key()

def cryp_encode(**kwargs):

    # Converte o dicionário para uma string JSON
    json_data = json.dumps(kwargs)

    # Criptografa os dados
    encrypted_data = cipher_suite.encrypt(json_data.encode())

    return encrypted_data.decode()  # Retorna o texto criptografado como string

def cryp_decode(encrypted_data):

    # Descriptografa os dados
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    
    # Converte de volta para o dicionário
    return json.loads(decrypted_data.decode())


