# Sunsete API

A Japanese-English dictionary REST API built with FastAPI and PostgreSQL, serving vocabulary entries from the JMdict project.
Japanese: exact match | English: partial match within definitions.

## Features

- **Pagination**: Efficiently browse large result sets
- **Full-Text Search**: Search in both Japanese and English
- **Rate Limiting**: 100 requests per minute per IP
- **CORS Enabled**: Ready for web applications
- **JSON Responses**: Clean, structured data format

## Stack

- **Python** with FastAPI framework
- **PostgreSQL** with advanced JSON aggregation functions
- **Redis/Upstash** for caching
- **Vercel** for serverless deployment
- **Supabase** for managed PostgreSQL

## API Usage

GET /v1/define/{word}
Returns first 20 entries for queried word

GET v1/define/{word}/?page={page}
page=0: first 20 results
page=1: results 21-40

## Example

curl https://sunsete-api.vercel.app/v1/define/日本

Response:

{
  "source":"api",
  "query":"日本",
  "page":0,
  "data":[
    {
      "wid":1582710,"kanji":[{"j_id":737042,"j_info":null,"japanese":"日本"}],
      "senses":[{"ant":null,"pos":"noun (common) (futsuumeishi)","ref":null,"dial":null,"misc":null,"s_id":71623,"gloss":"Japan","s_info":null,"k_restrict":null,"r_restrict":null}],
      "readings":[{"kana":"にほん","r_id":846994,"r_info":null,"restricted":null},{"kana":"にっぽん","r_id":846995,"r_info":null,"restricted":null}]}],
      "error":false,
      "count":1
      }
