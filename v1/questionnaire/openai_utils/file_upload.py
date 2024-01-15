import requests
from django.conf import settings

url = "https://api.openai.com/v1/files"

def upload_file(file_obj):
    payload = {'purpose': 'assistants'}
    files=[
      ('file',('_'.join(file_obj.name.split('/')[-1].split('_')[1:]), file_obj))
    ]
    headers = {
      'Authorization': f'Bearer {settings.OPEN_AI_API_KEY}',
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response.json()['id']
