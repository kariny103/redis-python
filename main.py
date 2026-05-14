import time
import redis
from fastapi import FastAPI, Response, Request, HTTPException

app = FastAPI()

# Conexão com o Redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# --- FASE 04: RATE LIMITING ---
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    key = f"rate_limit:{ip}"
    current_count = r.incr(key)
    if current_count == 1:
        r.expire(key, 60)
    if current_count > 10:
        raise HTTPException(status_code=429, detail="Muitas requisições.")
    return await call_next(request)

# --- FASE 02: CACHE ---
@app.get("/slow-data/{item_id}")
async def get_data(item_id: str, response: Response):
    cached_value = r.get(item_id)
    if cached_value:
        response.headers["X-Cache"] = "HIT"
        return {"data": cached_value, "source": "cache"}
    time.sleep(3) 
    data_final = f"Conteúdo do item {item_id}"
    r.setex(item_id, 30, data_final)
    response.headers["X-Cache"] = "MISS"
    return {"data": data_final, "source": "database"}

# --- FASE 03: FILA (PRODUTOR) ---
@app.post("/enviar-tarefa")
async def enqueue_task(mensagem: str):
    r.lpush("minha_fila", mensagem)
    return {"status": "Tarefa enviada!", "mensagem": mensagem}

@app.get("/")
def read_root():
    return {"message": "API de Redis rodando!"}