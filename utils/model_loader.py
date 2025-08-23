import os
import sys
from dotenv import load_dotenv
from utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

#from langchain_openai import ChatOpenAI
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomDocumentException
log = CustomLogger().get_logger(__name__)

class Model_Loader:
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configuration loaded successfully", config_keys=list(self.config.keys()))
    
    def _validate_env(self):
        required_vars= ['GOOGLE_API_KEY','GROQ_API_KEY'] 
        self.api_keys =  {key: os.getenv(key) for key in required_vars}
        missing = [k for k,v in self.api_keys.items() if not v]
        if missing:
            log.error('Missing Env Variables ',missing_vars = missing)
            raise CustomDocumentException("Missing Env Key",sys)
        
        log.info('Env variables validated', available_keys = [k for k in self.api_keys if self.api_keys[k]])        

    def load_embeddings(self):
        try:
            log.info('Loading Embedding Model...')
            if self.config['embedding_model']['provider'] =='ollama':
                model_name = self.config['embedding_model']['model_name']
                return OllamaEmbeddings(model = model_name)
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise CustomDocumentException('Failed to load embedding model', sys)
    
    def load_llm(self):
        """
        Load and return the LLM model.
        """
        """Load LLM dynamically based on provider in config."""
        
        llm_block = self.config["llm"]
        log.info("Loading LLM...")
        provider_key = os.getenv("LLM_PROVIDER", "ollama")  # Default to 'ollama' if not set
        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider_key=provider_key)
            raise ValueError(f"Provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature")
        max_tokens = llm_config.get("max_output_tokens")
        
        log.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

        if provider == "google":
            llm=ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            return llm

        elif provider == "groq":
            llm=ChatGroq(
                model=model_name,
                api_key=self.api_keys["GROQ_API_KEY"],
                temperature=temperature,
            )
            return llm
            
        elif provider == "ollama":
            llm = ChatOllama(model=model_name)
            return llm
        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")

if __name__ == "__main__":
    loader = Model_Loader()
    
    # Test embedding model loading
    embeddings = loader.load_embeddings()
    # print(f"Embedding Model Loaded: {embeddings}")
    
    # Test the ModelLoader
    result=embeddings.embed_query("Hello, how are you?")
    # print(f"Embedding Result: {result}")
    
    # Test LLM loading based on YAML config
    llm = loader.load_llm()
    # print(f"LLM Loaded: {llm}")
    
    # Test the ModelLoader
    result=llm.invoke("Hello, what is the current status on GDP of india?")
    print(f"LLM Result: {result.content}")