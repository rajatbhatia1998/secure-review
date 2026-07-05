import os
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from backend.app.config.config import load_config

def get_llm() -> Any:
    config = load_config()
    provider = config.provider.lower()
    api_key = config.api_key or "no-key-required"
    
    if provider == "anthropic":
        # Anthropic standard Claude models
        return ChatAnthropic(
            api_key=api_key,
            model=config.model,
            temperature=config.temperature,
        )
    else:
        # ChatOpenAI supports OpenAI, Ollama, LM Studio, and Gemini
        base_url = config.base_url
        
        if provider == "openai" and (not base_url or "localhost" in base_url):
            base_url = "https://api.openai.com/v1"
        elif provider == "groq" and (not base_url or "localhost" in base_url):
            base_url = "https://api.groq.com/openai/v1"
        elif provider == "gemini" and (not base_url or "localhost" in base_url):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            
        return ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=config.model,
            temperature=config.temperature,
        )
