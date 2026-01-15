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
    return {
            "Welcome": "to sunsete-api",
            "Query": "any Japanese word, in both English and Japanese!",
            "Example": "https://sunsete-api.vercel.app/v1/define/Japan",
            "Developer": "Ajmain Ahmed",
            "Github": "https://github.com/ajmain-ahmed/sunsete-api"
            }

@app.get("/v1/define/{word}")
@app.get("/v1/define/{word}/")
@app.get("/v1/define/{word}/?page={page}")
def define(word: str, request: Request, page: int = 0):

    page = max(page, 0)
    
    cache_key = f"{word}:{page}"
    client_host = request.client.host or 'unknown'
    response = ratelimit.limit(client_host)

    # if they've been rate limited
    if not response.allowed:
        return {
            'source': f'{client_host}', 
            'query': word, 
            'page': page,
            'data': 'rate limited', 
            'error': True,
        }
    
    # if data is in cache, respond with it
    cached_data = redis.get(cache_key)
    if cached_data:
        return {
            'source': 'cache', 
            'query': word, 
            'page': page,
            'data': json.loads(cached_data), 
            'error': False
        }
    
    # if data isn't in cache, send query to db
    data = supabase.rpc('def', params={'word': word, 'page': page}).execute()

    # if we get a valid response with data present
    if data.data is not None and len(data.data) > 0:
       
        redis.setex(cache_key, 21600, data.data)
        return {
            'source': 'api', 
            'query': word, 
            'page': page,
            'data': data.data, 
            'error': False,
            'count': len(data.data)
        }
    
    # if there's a response but no data
    elif data.data is not None and len(data.data) == 0:
      
        return {
            'source': 'api', 
            'query': word, 
            'page': page,
            'data': [], 
            'error': False,
            'message': 'No results found',
            'count': 0
        }
    
    # if there's no response at all
    else:
       
        return {
            'source': 'api', 
            'query': word, 
            'page': page,
            'data': None, 
            'error': True,
            'message': 'Database query failed'
        }