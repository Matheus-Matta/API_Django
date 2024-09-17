from .models import Pedido, Progresso, AvaliacaoMotorista, AvaliacaoMontador
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import random
import hashlib

class PedidoManager:
    def __init__(self, **kwargs):
        self.pedido = None
        codigo = kwargs.get("codigo")
        number = kwargs.get("number")
        if codigo and number:
            try:
                self.pedido = Pedido.objects.get(codigo=codigo, number=number)
            except Pedido.DoesNotExist:
                self.pedido = self.create_pedido(**kwargs)
        

    def create_pedido(self, **kwargs):
        """
        Cria um novo pedido e salva no banco de dados.
        """
        try:
            self.pedido = Pedido.objects.create(
                codigo=kwargs.get("codigo"),
                cliente=kwargs.get("nome"),
                desc=kwargs.get("desc"),
                email= kwargs.get("email", None),
                number=kwargs.get("number"),
                tracking=create_tracking(kwargs.get("number"), kwargs.get("codigo"), kwargs.get("desc"))
            )
            return self.pedido
        except Exception as e:
            raise ValueError(f"Erro ao criar pedido: {str(e)}")
    
    def update_status(self, status, mensagem, url):
        """
        Verifica se o status e a mensagem já foram adicionados ao pedido.
        Se não, adiciona-os ao progresso do pedido.
        """
        try:
            progresso = Progresso.objects.create(
                pedido=self.pedido,
                status=status,
                mensagem=mensagem,
                url=url
            )
            return progresso
        except Exception as e:
            raise ValueError(f"Erro ao adicionar status e mensagem: {str(e)}")
        
    def insert_avaliacao(self, **kwargs):
        """
            Função para registrar uma avaliação de motorista ou montador.
            
            kwargs:
            
            - motorista (string): nome do motorista avaliado.
            - montador (string): nome do montador avaliado.
            - comentario (str): Um comentário opcional.
            - avaliacao (int): avaliação do cliente de 1 a 5.
            - cliente (str); nome do cliente que avaliou
            
            Returns:
            - str: Uma mensagem de sucesso ou erro.
        """
        try:
            motorista = kwargs.get('motorista')
            montador = kwargs.get('montador')
        
            if motorista:
                avaliação = AvaliacaoMotorista.objects.create(
                    pedido = self.pedido,
                    motorista = kwargs.get('motorista'),
                    avaliacao = kwargs.get('avaliacao'),
                    comentario = kwargs.get('comentario') if kwargs.get('comentario') else "Sem comentario",
                    cliente = kwargs.get("nome")
                )
            
            elif montador:
                avaliação = AvaliacaoMontador.objects.create(
                    pedido = self.pedido,
                    montador= kwargs.get('montador'),
                    avaliacao = kwargs.get('avaliacao'),
                    comentario = kwargs.get('comentario') if kwargs.get('comentario') else "Sem comentario",
                    cliente = kwargs.get("nome")
                )
            else:
                raise ValueError("montador e nem motorista foram informados para a avaliação")
        
            return avaliação
        except Exception as e:
            raise ValueError(f"Erro ao adicionar avaliação: {str(e)}")
        
    def get_avaliacao(self, **kwargs):
        """
        Função para pegar uma avaliação caso exista.
        Retorna:
        - Avaliação encontrada ou None se não encontrada.
        """
        try:
            motorista = kwargs.get('motorista')
            montador = kwargs.get('montador')

            if motorista:
                try:
                    avaliacao = AvaliacaoMotorista.objects.get(
                        pedido=self.pedido,
                        motorista=motorista
                    )
                    return avaliacao
                except AvaliacaoMotorista.DoesNotExist:
                    return None

            elif montador:
                try:
                    avaliacao = AvaliacaoMontador.objects.get(
                        pedido=self.pedido,
                        montador=montador
                    )
                    return avaliacao
                except AvaliacaoMontador.DoesNotExist:
                    return None
            else:
                raise ValueError("Nem montador nem motorista foram informados para a avaliação.")
            
        except Exception as e:
            raise ValueError(f"Erro ao obter avaliação: {str(e)}")
        
    def get_tracking(self):
        try:
            # Verifica se o pedido existe com base no self.pedido
            pedido = Pedido.objects.filter(id=self.pedido.id).exists()
            if pedido:
                return self.pedido.tracking  # Retorna o código de rastreamento do pedido
            else:
                return False
        except Exception as e:
            raise ValueError(f"Houve um erro no get tracking: {str(e)}")

def create_tracking(number, codigo, desc):
    while True:
        # Combina os dados
        dados_combinados = f"{number}{codigo}{desc}"

        # Embaralha os caracteres
        dados_embaralhados = ''.join(random.sample(dados_combinados, len(dados_combinados)))

        # Gera um hash SHA256 para garantir a unicidade e uma boa aleatoriedade
        hash_rastreamento = hashlib.sha256(dados_embaralhados.encode()).hexdigest()[:15]  # Limita o hash a 10 caracteres

        # Verifica se o hash gerado já existe em algum pedido
        if not Pedido.objects.filter(tracking=hash_rastreamento).exists():
            # Se não existir, retorna o hash gerado como o código de rastreamento
            return hash_rastreamento
        