class MessageGenerator:
    def msg_pedido(self,nome, desc, link):
        return [
                f"Olá {nome}, Obrigado pela compra do produto {desc}. Acompanhe o status do seu pedido pelo link >> {link} ",
            ]
    
    def msg_roteiro(self, nome):
        return [
            f"Olá {nome}, seu pedido está atualmente em processo de roteirização e sairá amanhã.",
            f"Oi {nome}, estamos trabalhando na roteirização do seu pedido, que está previsto para sair amanhã.",
            f"Prezado {nome}, seu pedido está sendo roteirizado neste momento e sairá amanhã.",
            f"Olá {nome}, a roteirização do seu pedido está em andamento e a previsão é que ele saia amanhã.",
            f"Caro {nome}, seu pedido está passando pelo processo de roteirização e sairá amanhã.",
            f"Oi {nome}, seu pedido entrou na fase de roteirização e deverá sair amanhã.",
            f"Prezado {nome}, estamos cuidando da roteirização do seu pedido, que está previsto para sair amanhã.",
            f"Olá {nome}, seu pedido está na etapa de roteirização e será enviado amanhã.",
            f"Oi {nome}, estamos organizando a roteirização do seu pedido, que sairá amanhã.",
            f"Caro {nome}, seu pedido está sendo preparado para a roteirização e sairá amanhã."
        ]
    
    def msg_entrega(self, nome):
        return [
            f"Olá {nome}, seu pedido está a caminho para entrega.",
            f"Oi {nome}, seu pedido está atualmente em trânsito para entrega.",
            f"Prezado {nome}, seu pedido está em rota de entrega.",
            f"Olá {nome}, seu pedido está sendo saindo para ser entregue.",
            f"Caro {nome}, seu pedido já saiu para entrega.",
            f"Oi {nome}, a entrega do seu pedido está em andamento.",
            f"Prezado {nome}, seu pedido está em trânsito e será entregue em breve.",
            f"Olá {nome}, estamos a caminho com seu pedido.",
            f"Oi {nome}, seu pedido está em fase de entrega final.",
            f"Caro {nome}, seu pedido será entregue em breve."
        ]
    
    def msg_avali_motorista(self, nome, motorista, desc, link):
        return [
                f"Olá {nome}, a entrega do seu produto {desc} foi concluida. avalie a entrega do motorista: {motorista}. link > {link}",
        ]

    def msg_chave_fiscal(self, nome, chave_fiscal):
        return [
            f"Olá {nome}, sua nota fiscal foi emitida com sucesso. A chave fiscal é {chave_fiscal}.",
            f"Oi {nome}, sua nota fiscal foi gerada com sucesso. Veja a chave fiscal: {chave_fiscal}.",
            f"Prezado {nome}, sua nota fiscal foi emitida corretamente. Chave fiscal: {chave_fiscal}.",
            f"Olá {nome}, a nota fiscal do seu pedido foi gerada. Chave fiscal: {chave_fiscal}.",
            f"Caro {nome}, sua nota fiscal foi criada. Chave fiscal: {chave_fiscal}.",
            f"Oi {nome}, a emissão da sua nota fiscal foi concluída. Chave fiscal: {chave_fiscal}.",
            f"Prezado {nome}, sua nota fiscal foi devidamente gerada. Chave fiscal: {chave_fiscal}.",
            f"Olá {nome}, sua nota fiscal foi emitida com a chave: {chave_fiscal}.",
            f"Caro {nome}, sua nota fiscal foi emitida com sucesso. Chave fiscal: {chave_fiscal}.",
            f"Oi {nome}, sua nota fiscal está pronta. A chave fiscal é {chave_fiscal}."
        ]

    def msg_tentativa(self, nome):
        return [
            f"Olá {nome}, tentamos entregar seu pedido, mas não tivemos sucesso.",
            f"Oi {nome}, houve uma tentativa de entrega que não foi bem-sucedida.",
            f"Prezado {nome}, infelizmente, não conseguimos realizar a entrega do seu pedido.",
            f"Olá {nome}, tentamos entregar seu pedido, mas não obtivemos sucesso.",
            f"Caro {nome}, houve uma tentativa de entrega que não foi bem-sucedida.",
            f"Oi {nome}, não conseguimos completar a entrega do seu pedido.",
            f"Prezado {nome}, nossa tentativa de entrega não foi bem-sucedida.",
            f"Olá {nome}, a tentativa de entrega do seu pedido não teve sucesso.",
            f"Caro {nome}, a entrega do seu pedido falhou na tentativa realizada.",
            f"Oi {nome}, infelizmente, a tentativa de entrega do seu pedido não foi concluída."
        ]

    def msg_agendamento(self, nome, desc, montador, data_previsao):
        return [
            f"Olá {nome}, a montagem do seu produto {desc} está agendada. Montador: {montador}, previsão: {data_previsao}.",
            f"Oi {nome}, sua montagem está marcada. Montador: {montador}, previsão para {data_previsao}, produto: {desc}.",
            f"Prezado {nome}, a montagem do {desc} está programada. Montador: {montador}, previsão: {data_previsao}.",
            f"Olá {nome}, seu produto {desc} está com a montagem agendada. Montador: {montador}, previsão: {data_previsao}.",
            f"Caro {nome}, a montagem do seu {desc} está agendada. Montador: {montador}, data prevista: {data_previsao}.",
            f"Oi {nome}, a montagem do produto {desc} está agendada para {data_previsao}. Montador: {montador}.",
            f"Prezado {nome}, a montagem do seu {desc} foi marcada. Montador: {montador}, data: {data_previsao}.",
            f"Olá {nome}, o montador {montador} está agendado para montar seu {desc} na data: {data_previsao}.",
            f"Caro {nome}, a montagem do {desc} está programada para {data_previsao}. Montador: {montador}.",
            f"Oi {nome}, seu {desc} será montado pelo {montador} na data de {data_previsao}."
        ]
    
    
    def msg_vinculo(self, nome, desc, montador , data_previsao):
        return [
                f"Olá {nome}, a montagem do seu produto {desc} está agendada para {data_previsao} com o montador {montador}",
            ]
   
    def msg_avali_montagem(self, nome, montador, desc, link):
        return [
                f"Olá {nome}, a montagem do seu produto {desc} foi concluida. avalie o montador: {montador}. link > {link}",
            ]
    
    

