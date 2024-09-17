import random
import re
import requests
from datetime import datetime
from .request import send_message
from .generator import MessageGenerator, MessageGenerator_unique
from .mail import send_mail
from .encrypt import cryp_encode
from decouple import config
from .db_manage import PedidoManager
from .encurtador import encurtar_url_tinyurl

class MessageProcessor:

    def __init__(self, instance):
        self.instance = instance
        self.message_generator = MessageGenerator()  # Classe para gerar mensagens
        self.status_handlers = {
            'l': self.message_generator.msg_roteiro,
            't': self.message_generator.msg_entrega,
            'n': self.message_generator.msg_chave_fiscal,
            'f': self.message_generator.msg_tentativa,
            'm': self.message_generator.msg_agendamento,
            'p': self.message_generator.msg_pedido,
            'am': self.message_generator.msg_avali_motorista,
            'at': self.message_generator.msg_avali_montagem,
            'a': self.message_generator.msg_vinculo,
        }
    
    def send(self, **kwargs):
        try:
            number = kwargs.get("number")
            nome = kwargs.get("nome")
            status = kwargs.get("status")
            email = kwargs.get("email")
            desc = kwargs.get("desc")
            codigo = kwargs.get("codigo")

            if not number or not nome or not status or not desc or not codigo:
                raise ValueError("Campos obrigatórios não foram fornecidos.( number, name, status, desc, codigo )")

            # Valida o número
            if not self.is_number_valid(number):
                raise ValueError("Número inválido. O formato correto é 5521912345678.")

            # Valida se o status é válido
            if status.lower() not in self.status_handlers:
                raise ValueError("Status inválido fornecido.")

            # Seleciona a função correta para o status
            msg_function = self.status_handlers[status.lower()]

            msg_unique = MessageGenerator_unique(**kwargs)  # Gera msg para tracking e email

            # Cria ou busca o pedido com base no código e número
            pedido = PedidoManager(**kwargs)

            # Gera a criptografia para a URL da avaliação e do rastreamento
            cryp = cryp_encode(**kwargs)

            tracking_link = f'{config("DOMAIN")}/api/tracking/{pedido.get_tracking()}' if pedido.get_tracking() else None
            avalicao_link = f'{config("DOMAIN")}/api/avaliacao/{cryp}' if status.lower() in ['at', 'am'] else None
           

            # Atualiza kwargs com os links
            kwargs['tracking_link'] = tracking_link
            if status.lower() in ['at', 'am']:
                kwargs['avalicao_link'] = encurtar_url_tinyurl(avalicao_link)

            pedido.update_status(status.lower(), msg_unique, avalicao_link) 

            # Gerar a mensagem
            if status.lower() == 'n':
                chave_fiscal = kwargs.get('chaveFiscal')
                if not chave_fiscal:
                    raise ValueError("Campo chaveFiscal inválido!")
                msg = random.choice(msg_function(nome, chave_fiscal))
            elif status.lower() == 'm' or status.lower() == 'a':
                montador = kwargs.get('montador')
                desc = kwargs.get('desc')
                data_previsao = kwargs.get('dataPrevisao')
                if not montador or not desc or not data_previsao:
                    raise ValueError("Campos obrigatórios para o status (m) não foram fornecidos.")
                data_previsao = self.formatar_data(data_previsao)
                msg = random.choice(msg_function(nome, desc, montador, data_previsao))
            elif status.lower() == 'p':
                desc = kwargs.get('desc')
                if not desc:
                    raise ValueError("Campos obrigatórios para o status (p) não foram fornecidos.")
                msg = random.choice(msg_function(nome, desc, kwargs['tracking_link']))
            elif status.lower() == 'am':
                desc = kwargs.get('desc')
                motorista = kwargs.get('motorista')
                if not desc or not motorista:
                    raise ValueError("Campos obrigatórios para o status (am) não foram fornecidos.")
                msg = random.choice(msg_function(nome, motorista, desc, kwargs['avalicao_link']))
            elif status.lower() == 'at':
                desc = kwargs.get('desc')
                montador = kwargs.get('montador')
                if not desc or not montador:
                    raise ValueError("Campos obrigatórios para o status (at) não foram fornecidos.")
                msg = random.choice(msg_function(nome, montador, desc, kwargs['avalicao_link']))
            else:
                # Para os outros status ('l', 't', 'f'), não há parâmetros extras
                msg = random.choice(msg_function(nome))

            # Atualiza o status com a nova mensagem

            # Envio de emails
            if email:
                if status.lower() in ['at', 'am']:
                    send_mail(nome, desc, email, msg_unique, codigo, kwargs['tracking_link'], kwargs['avalicao_link'])
                else:
                    send_mail(nome, desc, email, msg_unique, codigo, kwargs['tracking_link'])

            # Envio da mensagem usando a função send_message de forma assíncrona
            task = send_message.apply_async((self.instance, msg, number), queue='messages')

            return 'OK'
        except Exception as e:
            print(f"error interno no send function {str(e)}")
            raise ValueError(f"ops... houve um error interno {str(e)}")



    # Função para validar número
    @staticmethod
    def is_number_valid(number):
        return bool(re.match(r"^55\d{11}$", number))
    
    # função para formata data para dia/mes
    @staticmethod
    def formatar_data(data):
            date_obj = datetime.strptime(data, '%Y-%m-%d')
            return date_obj.strftime('%d/%m')