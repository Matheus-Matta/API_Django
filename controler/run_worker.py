# run_worker.py
from celery import Celery
from celery.bin import worker

# Carregue o app Celery do seu projeto
app = Celery('controler')

# Certifique-se de que a configuração das filas esteja correta
app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'webhook': {
        'exchange': 'webhook',
        'routing_key': 'webhook',
    },
    'messages': {
        'exchange': 'messages',
        'routing_key': 'messages',
    }
}

def start_worker():
    argv = [
        'worker',
        '--loglevel=info',
        '--queues=messages',  # Define para trabalhar na fila 'messages'
        '--concurrency=1'     # Define para processar uma tarefa por vez
    ]
    worker_instance = worker.worker(app=app)
    worker_instance.run(argv)

if __name__ == "__main__":
    start_worker()