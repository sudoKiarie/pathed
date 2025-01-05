import os
from openai import OpenAI

client = OpenAI(
    api_key="de1cd11f90b84bef979a279a8fd8a8eb",
    base_url="https://api.aimlapi.com",
)

response = client.chat.completions.create(
    model="o1-preview",
    messages=[
        {
            "role": "user",
            "content": "The patient has reported a stomachache. Please generate the most relevant question to help narrow down the possible causes."
        },
    ],
    max_tokens=100,
)

message = response.choices[0].message.content
print(f"Assistant: {message}")