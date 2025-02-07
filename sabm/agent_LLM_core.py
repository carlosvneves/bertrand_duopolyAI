import time
import openai
import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from sabm.utils import BackendType,ModelType

load_dotenv()
# openai.api_key = ""

client = openai.OpenAI(

    api_key = os.environ["MARITACA_API_KEY"],
    base_url = "https://chat.maritaca.ai/api",

)

class Agent:
    # def __init__(self, temperature=0.8, model='gpt-4', max_tokens=100):
    def __init__(self, temperature=0.8, 
    backend=BackendType.OnlineMaritacaAI,
    model=ModelType.MaritacaAI, 
    max_tokens=100, max_retries = 3):
        self.temperature = temperature
        self.backend = backend
        self.model = model 
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        print(self.model)
    def communicate(self, context):
        prompt = context + "\n\n"
        message = ""

        if self.model.value == ModelType.MaritacaAI.value:
            retries = 3
            backoff_factor = 2
            current_retry = 0

            while current_retry < retries:
                try:
                    # response = openai.ChatCompletion.create(
                    #     model=self.model,
                    #     messages=[
                    #         {"role": "user", "content": prompt},
                    #         {"role": "user", "content": ""}
                    #     ],
                    #     max_tokens=self.max_tokens,
                    #     n=1,
                    #     temperature=self.temperature,
                    #     top_p=1
                    # )
                    response = client.chat.completions.create(
                        model=self.model.value,
                        messages=[
                            {"role": "user", "content": prompt},
                            {"role": "user", "content": ""}
                        ],
                        max_tokens=self.max_tokens,
                        n=1,
                        temperature=self.temperature,
                        top_p=1
                    )
                    message = response.choices[0].message.content
                    print(message)
                    if message is not None:
                        message = message.strip()
                    return message
                except openai.RateLimitError as e:
                    if current_retry < retries - 1:
                        wait_time = backoff_factor ** current_retry
                        print(f"RateLimitError: Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        current_retry += 1
                    else:
                        print(f"Error {e}")
                        raise e
                except openai.APIError as e:
                    if current_retry < retries - 1:
                        wait_time = backoff_factor ** current_retry
                        print(f"RateLimitError: Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        current_retry += 1
                    else:
                        raise e
                except Exception as e:
                    if current_retry < retries - 1:
                        wait_time = backoff_factor ** current_retry
                        print(f"RateLimitError: Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        current_retry += 1
                    else:
                        print(f"Error {e}")
                        raise e
    def generate_response(self, context):
        backend_option = self.backend
        model_option = self.model
        prompt = context + "\n\n"
        message = ""
        if backend_option == BackendType.OnlineMaritacaAI:
            model = ChatOpenAI(
                api_key=os.environ['MARITACA_API_KEY'], # type: ignore
                base_url="https://chat.maritaca.ai/api",
                model = str(ModelType.MaritacaAI.value),
                max_completion_tokens=self.max_tokens,
                max_retries=self.max_retries,
                temperature=self.temperature,
                n=1,
                top_p=1
            )
        elif backend_option == BackendType.LocalOllama:
            model = ChatOllama(
                base_url="http://localhost:11434/",
                model=str(ModelType[model_option.name].value),
                temperature=self.temperature,
                num_thread=8,
                top_p=1
            )
        elif backend_option == BackendType.OnlineGroq:
            model =ChatGroq(
                #api_key=os.environ['GROQ_API_KEY'],
                model = str(ModelType[model_option.name].value),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                max_retries=self.max_retries,
                n=1,
            )
        elif backend_option == BackendType.OnlineGoogle:
            model = ChatGoogleGenerativeAI(
                model = str(ModelType[model_option.name].value),
                max_retries=self.max_retries,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
                n=1
            )
        else:
            model = ChatMistralAI(
                model_name = str(ModelType[model_option.name].value),
                max_retries=self.max_retries,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
            )

        messages = [
            {"role": "user", "content": prompt},
            {"role": "user", "content": ""}
        ]
        message = model.invoke(messages).content
        print(message)
        if message is not None:
            message = str(message).strip()
        return message


if __name__ == "__main__":
    a = Agent(backend=BackendType.OnlineMistral, model=ModelType.Mistral_small)
    print(a.generate_response("Olá"))