from enum import Enum

class ModelType(Enum):
    Sabia3_small = "sabiazinho-3"
    Sabia3_large = "sabia-3"
    Deepseek_r1_1dot5b_Distill_Qwen = "deepseek-r1:1.5b"
    Deepseek_r1_8b_Distill_Llama = "deepseek-r1:8b"
    Mistral_7b = "mistral:latest"
    Deepseek_r1_70b_Distill_Llama = "deepseek-r1-distill-llama-70b"
    Llama_3dot3_70b_versatile = "llama-3.3-70b-versatile"
    Gemini_2dot0_flash_lite = "gemini-2.0-flash-lite-preview-02-05"
    Gemini_2dot0_pro = "gemini-2.0-pro-exp-02-05"
    Gemini_2dot0_flash_thinking = "gemini-2.0-flash-thinking-exp-01-21"
    Mistral_small = "mistral-small-latest"
    Mistral_nemo = "open-mistral-nemo"
    Gemma2_9b = "gemma2"
    Phi4_14b = "phi4"
    TinyLlama_r1_limo = "hf.co/mradermacher/TinyLlama-R1-LIMO-GGUF:F16"

class BackendType(Enum):
    LocalOllama = "ollama"
    OnlineGroq = "groq"
    OnlineMaritacaAI = "maritaca"
    OnlineGoogle= "google"
    OnlineMistral = "mistral"