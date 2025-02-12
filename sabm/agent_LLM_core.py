import time
from groq import RateLimitError
import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from sabm.utils import BackendType,ModelType
#from langchain_core.rate_limiters import InMemoryRateLimiter

# rate_limiter = InMemoryRateLimiter(
#     requests_per_second=0.1,  # <-- Super slow! We can only make a request once every 10 seconds!!
#     check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
#     max_bucket_size=10,  # Controls the maximum burst size.
# )
class Agent:

    def __init__(self, temperature=0.8,
    backend=BackendType.OnlineMaritacaAI,
    model=ModelType.Sabia3_small,
    max_tokens=128, max_retries = 3):
        self.temperature = temperature
        self.backend = backend
        self.model = model 
        self.max_tokens = max_tokens
        self.max_retries = max_retries


    def generate_response(self, context):
        backend_option = self.backend
        model_option = self.model
        prompt = context + "\n\n"
        message = ""

        retries = 3
        backoff_factor = 2
        current_retry = 0

        while current_retry < retries:
            try:
                if backend_option == BackendType.OnlineMaritacaAI:
                    model = ChatOpenAI(
                        api_key=os.environ['MARITACA_API_KEY'], # type: ignore
                        base_url="https://chat.maritaca.ai/api",
                        model = str(ModelType[model_option.name].value),
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
                        n=1,
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
                # print(message)
                if message is not None:
                    message = str(message).strip()

                return message
            except RateLimitError as e:
                if current_retry < retries - 1:
                    wait_time = backoff_factor ** current_retry
                    print(f"RateLimitError: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    current_retry += 1
                else:
                    print(f"Error {e}")
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
    

