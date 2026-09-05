from langchain_ollama import ChatOllama


def create_llm():
    return ChatOllama(
        model="qwen3:8b",  # Specifies the target local model name or tag to pull and run via Ollama
        temperature=0,  # Sets sampling randomness to zero for deterministic, factual outputs
        validate_model_on_init=True,  # Checks Ollama service connectivity and confirms the model is pulled during initialization
    )