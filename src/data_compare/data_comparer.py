import sys 
from dotenv import load_env 
import pandas  as pd 
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomDocumentException
from model.models import * 
from prompt.prompt_library import PROMPT_REGISTRY 
from utils.model_loader import Model_Loader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentComparor:
    def __init__(self):
        pass 
    
    def compare_document(self):
        pass 
    
    def _format_response(self):
        pass 