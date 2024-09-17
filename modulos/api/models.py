from django.db import models

# Modelo do Pedido
class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20)
    cliente = models.CharField(max_length=100)
    desc = models.TextField()
    email = models.EmailField(blank=True, null=True)  # Email opcional
    number = models.CharField(max_length=15)  # Número do telefone
    tracking = models.TextField(max_length=50,default=None,null=True)

    def __str__(self):
        return f'{self.cliente} - {self.codigo}'


# Modelo de Progresso
class Progresso(models.Model):
    id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='progresso')
    status = models.CharField(max_length=100)
    mensagem = models.TextField()
    url = models.TextField(default=None, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)  # Data e hora adicionadas automaticamente

    def __str__(self):
        return f'Progresso {self.status} - Pedido {self.pedido.codigo}'


# Modelo de Avaliação do Motorista
class AvaliacaoMotorista(models.Model):
    motorista = models.TextField(blank=True, null=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='avaliacao_motorista')
    avaliacao = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)  # Avaliação de 1 a 5
    comentario = models.TextField(blank=True, null=True)
    cliente = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Avaliação Motorista - Pedido {self.pedido.codigo}: {self.avaliacao} estrelas'


# Modelo de Avaliação do Montador
class AvaliacaoMontador(models.Model):
    montador = models.TextField(blank=True, null=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='avaliacao_montador')
    avaliacao = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)  # Avaliação de 1 a 5
    comentario = models.TextField(blank=True, null=True)
    cliente = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Avaliação Montador - Pedido {self.pedido.codigo}: {self.avaliacao} estrelas'
