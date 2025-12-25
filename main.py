import json
from typing import Union
from database import supabase
from fastapi import FastAPI
from upstash_redis import Redis

app = FastAPI()
redis = Redis.from_env()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/v1/define/{word}")
def define(word: str):
    cache_key = word
    
    cached_data =  redis.get(cache_key)
    if cached_data:
        return {'source': 'cache', 'data': json.loads(cached_data)}

    data = supabase.rpc('def', params={'word': word}).execute()
    redis.setex(cache_key, 21600, data.data)
    return {'source':'api', 'data':data}