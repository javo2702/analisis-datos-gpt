import openai as gpt
import os
from dotenv import load_dotenv
from util.functions import loading

load_dotenv()


def ask_gpt(question, data):
    gpt.api_key = os.getenv('OPENAI_API_KEY')
    text_data = data.to_string(index=False)
    request = question + "\n" + text_data[0:2500]
    print(request)
    response = gpt.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a data analyze"},
            {"role": "user", "content": text_data[0:1500]}
        ],
    )
    print(response)
    return response


def analyse_gpt(question):
    gpt.api_key = os.getenv('OPENAI_API_KEY')
    print(question)
    response = gpt.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "Eres un analista de datos"},
            {"role": "user", "content": question}
        ],
    )
    print(response)
    return response
