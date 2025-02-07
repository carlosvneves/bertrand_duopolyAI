from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import os
from sabm.utils import BackendType, ModelType, SYSTEM_TEMPLATE_BR, SYSTEM_TEMPLATE


load_dotenv()


def generate_response(input_text, model_option, backend_option):
    
    if backend_option == BackendType.OnlineMaritacaAI.value:
        system_template = SYSTEM_TEMPLATE_BR
    else:
        system_template = SYSTEM_TEMPLATE

    # Define the system and human message templates
    human_template = "{input_text}"
    
    # Create the chat prompt template
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    # Format the messages with the input text
    messages = chat_prompt.format_messages(input_text=input_text)

    if backend_option == BackendType.OnlineMaritacaAI.name:
        model = ChatOpenAI(
            api_key=os.environ['MARITACA_API_KEY'], # type: ignore
            base_url="https://chat.maritaca.ai/api",
            model = str(ModelType.MaritacaAI.value)
        )    
    elif backend_option == BackendType.LocalOllama.name:
        model = ChatOpenAI(
            model=str(ModelType[model_option].value)
        )        
    elif backend_option == BackendType.OnlineGroq.name:
        model =ChatGroq(
            #api_key=os.environ['GROQ_API_KEY'],
            model = str(ModelType[model_option].value)
        ) 
    elif backend_option == BackendType.OnlineGoogle.name:
        model = ChatGoogleGenerativeAI(
            model = str(ModelType[model_option].value)
        )
    else:
        model = ChatMistralAI(
            model_name = str(ModelType[model_option].value)
        )
            
    # don´t need to be stream....
    response = model.stream(messages)

    return response
def parse_stream(stream):
    for chunk in stream:
        yield (chunk.content.
                replace('$', '\\$').
                replace('<think>', '\n:brain:\n\n:green[\\<pensando\\>]\n').
                replace('</think>', '\n\n:green[\\</pensando\\>]\n\n---')
                )