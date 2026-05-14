import redis
import time

# Conecta ao Redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

print("Worker iniciado. Aguardando tarefas...")

while True:
    # BRPOP remove e retorna o item da lista (Fase 03)
    tarefa = r.brpop("minha_fila", timeout=0)
    if tarefa:
        print(f"Processando tarefa recebida: {tarefa[1]}")
        time.sleep(2) # Simula processamento