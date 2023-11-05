import requests
import sys

# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/generate'

async def print_response_stream(prompt):
    async for response in run(prompt):
        print(response, end='')
        sys.stdout.flush()  # If we don't flush, we won't see tokens in realtime.

def run(prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 2000,
        'mode': 'instruct',
        'preset': 'simple-1',
    }

    response = requests.post(URI, json=request)
    if response.status_code == 200:
        return response.json()['results'][0]['text']