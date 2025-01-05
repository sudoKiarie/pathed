import requests
import json
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()


api_key = os.getenv('API_KEY')
def get_gemini_ai_response(prompt):
    context = "The interaction is with people who have low but daily earnings in Nairobi, Kenya. They cannot afford financial advisor. If they give you a number, please respond with some helpful math. The expectation is the responses will be relevant to them. The points should be brief and should not produce the 'read more' prompt on WhatsApp.\n\n"
    prompt_with_context = context + prompt

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_with_context
                    }
                ]
            }
        ]
    }
    try:
        response = requests.post(url, json=data, headers=headers, params={'key': api_key})
        response_data = response.json()
        #debug
        print(response_data)

        if response.status_code == 200:
            if response_data.get('candidates'):
                return response_data['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Error: Empty response from Gemini AI API"
        else:
            return f"Error: HTTP status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test.py 'How can I save money effectively?'")
        return
    
    prompt = sys.argv[1]

    #DEBUG
    print(f"Prompt: {prompt}")

    response_text = get_gemini_ai_response(prompt)
    print(response_text)

if __name__ == "__main__":
    main()