import json
from database import supabase
from fastapi import FastAPI, Request
from upstash_redis import Redis
from fastapi.middleware.cors import CORSMiddleware
from upstash_ratelimit import Ratelimit, FixedWindow

app = FastAPI()
redis = Redis.from_env()

origins = [
    "*",
]

ratelimit = Ratelimit(
    redis=Redis.from_env(),
    limiter=FixedWindow(max_requests=100, window=60),
    prefix="@upstash/ratelimit",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Welcome": "to sunsete-api"}

@app.get("/v1/define/{word}")
def define(word: str, request: Request):

    cache_key = word
    client_host = request.client.host or 'unknown'
    response = ratelimit.limit(client_host)

    if not response.allowed:
        return {'source':f'{client_host}', 'query': word, 'data':'rate limited', 'error': True}

    cached_data =  redis.get(cache_key)
    if cached_data:
        return {'source': 'cache', 'query': word, 'data': json.loads(cached_data), 'error': False}

    data = supabase.rpc('def', params={'word': word}).execute()
    if data.data is not None:
        redis.setex(cache_key, 21600, data.data)
        return {'source':'api', 'query': word, 'data':data.data, 'error': False}
    else:
        return {'source':'api', 'query': word, 'data':None, 'error': True}