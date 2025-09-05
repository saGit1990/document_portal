import os
import sys
import json
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

class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("API_KEYS")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("Missing required API keys", missing_keys=missing)
            raise CustomDocumentException("Missing API keys", sys)

        log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val

class Model_Loader:
    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))
    
    # def _validate_env(self):
    #     required_vars= ['GOOGLE_API_KEY','GROQ_API_KEY'] 
    #     self.api_key_mgr =  {key: os.getenv(key) for key in required_vars}
    #     log.info(self.api_keys.keys())
    #     missing = [k for k,v in self.api_key_mgr.items() if not v]

    #     if missing:
    #         log.error('Missing Env Variables ',missing_vars = missing)
    #         raise CustomDocumentException("Missing Env Key",sys)
        
    #     log.info('Env variables validated', available_keys = [k for k in self.api_key_mgr if self.api_key_mgr[k]])        

    def load_embeddings(self):
        try:
            log.info('Loading Embedding Model...')
            if self.config['embedding_model']['provider'] =='ollama':
                model_name = self.config['embedding_model']['model_name']
                return OllamaEmbeddings(model = model_name,verbose=False)
            elif self.config['embedding_model']['provider'] == 'google':
                model_name = self.config['embedding_model']['model_name']
                return GoogleGenerativeAIEmbeddings(model = model_name,
                                                    google_api_key= self.api_key_mgr.get('GOOGLE_API_KEY') )
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise CustomDocumentException('Failed to load embedding model', sys)
    
    def load_llm(self):
        """Load LLM dynamically based on provider in config."""
        
        llm_block = self.config["llm"]
        log.info("Loading LLM...")
        provider_key = "google"#os.getenv("LLM_PROVIDER")
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
                max_output_tokens=max_tokens,
                google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
            )
            return llm

        elif provider == "groq":
            llm=ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
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
