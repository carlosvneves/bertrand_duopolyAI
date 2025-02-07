import pytest
from unittest.mock import Mock, patch
from sabm.agent_LLM_core import Agent
from utils import BackendType, ModelType

@pytest.fixture
def mock_response():
    return "This is a test response"

@pytest.fixture
def base_agent():
    return Agent(temperature=0.7, max_tokens=100, max_retries=1)

def test_maritaca_generate_response(base_agent, mock_response):
    base_agent.backend = BackendType.OnlineMaritacaAI
    base_agent.model = ModelType.MaritacaAI
    
    with patch('langchain_openai.ChatOpenAI') as mock_chat:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = mock_response
        mock_chat.return_value = mock_instance
        
        response = base_agent.generate_response("Test prompt")
        
        assert response == mock_response
        mock_chat.assert_called_once_with(
            api_key=pytest.any_string(),
            base_url="https://chat.maritaca.ai/api",
            model=ModelType.MaritacaAI.value,
            max_completion_tokens=100,
            max_retries=1,
            temperature=0.7,
            n=1,
            top_p=1
        )

def test_ollama_generate_response(base_agent, mock_response):
    base_agent.backend = BackendType.LocalOllama
    base_agent.model = ModelType.Llama2
    
    with patch('langchain_ollama.ChatOllama') as mock_chat:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = mock_response
        mock_chat.return_value = mock_instance
        
        response = base_agent.generate_response("Test prompt")
        
        assert response == mock_response
        mock_chat.assert_called_once_with(
            base_url="http://localhost:11434/",
            model=ModelType.Llama2.value,
            temperature=0.7,
            num_thread=8,
            top_p=1
        )

def test_groq_generate_response(base_agent, mock_response):
    base_agent.backend = BackendType.OnlineGroq
    base_agent.model = ModelType.Mixtral
    
    with patch('langchain_groq.ChatGroq') as mock_chat:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = mock_response
        mock_chat.return_value = mock_instance
        
        response = base_agent.generate_response("Test prompt")
        
        assert response == mock_response
        mock_chat.assert_called_once_with(
            model=ModelType.Mixtral.value,
            max_tokens=100,
            temperature=0.7,
            max_retries=1,
            n=1
        )

def test_google_generate_response(base_agent, mock_response):
    base_agent.backend = BackendType.OnlineGoogle
    base_agent.model = ModelType.Gemini_pro
    
    with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_chat:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = mock_response
        mock_chat.return_value = mock_instance
        
        response = base_agent.generate_response("Test prompt")
        
        assert response == mock_response
        mock_chat.assert_called_once_with(
            model=ModelType.Gemini_pro.value,
            max_retries=1,
            max_tokens=100,
            temperature=0.7,
            top_p=1,
            n=1
        )

def test_mistral_generate_response(base_agent, mock_response):
    base_agent.backend = BackendType.OnlineMistral
    base_agent.model = ModelType.Mistral_small
    
    with patch('langchain_mistralai.ChatMistralAI') as mock_chat:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = mock_response
        mock_chat.return_value = mock_instance
        
        response = base_agent.generate_response("Test prompt")
        
        assert response == mock_response
        mock_chat.assert_called_once_with(
            model_name=ModelType.Mistral_small.value,
            max_retries=1,
            max_tokens=100,
            temperature=0.7,
            top_p=1
        ) 