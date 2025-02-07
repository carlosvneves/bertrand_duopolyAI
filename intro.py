# import openai
# import os 
# from dotenv import load_dotenv

# load_dotenv()

# client = openai.OpenAI(

#     api_key=os.getenv("MARITACA_API_KEY_AG2"),
#     base_url="https://chat.maritaca.ai/api",
# )

# response = client.chat.completions.create(
#     model = "sabiazinho-3",
#     messages=[
#         {
#             "role": "user",
#             "content": "O que é um Large Language Model? Responda com 50 tokens."
#         }
#     ],
#     max_tokens=100
# )

# print(f"Resposta:\n {response.choices[0].message.content}")
from sabm.utils import ModelType, BackendType

back = "OnlineMaritacaAI"
model = "MaritacaAI"

[print(k) for k in ModelType]

[print(k) for k in BackendType]

print(ModelType[model].value)
print(BackendType[back].value)