from numpy import true_divide
import os
import sys
import requests
import json
import base64
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()


def enconde_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ.get('AI_AGENT_KEY')}",
    "Content-Type": "application/json"
}

current_dir = Path(__file__).resolve().parent
static_dir = current_dir.parent.parent
image_path = static_dir / "media\\1.png"

base64_image = enconde_image_to_base64(image_path)
data_url = f"data:application/png;base64,{base64_image}"

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Describe que tipos de cable se muestran en la imagen asi como la composicion de cada una. Y dame la respuesta en español"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url
                }
            },
        ]
    }
]

# Optional: Configure PDF processing engine

payload = {
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "messages": messages
}

response = requests.post(url, headers=headers, json=payload)

print(response.json())

output = response.json()
save_dir = static_dir / "media\\output.txt"
text = output["choices"][0]["message"]["reasoning"]

with open(save_dir, 'w', encoding='utf-8') as file:
    file.write(text)
