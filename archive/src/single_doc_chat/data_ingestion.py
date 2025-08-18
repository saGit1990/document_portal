from logging import log
import uuid 
from pathlib import Path 
import sys 
import os
import chardet

from datetime import datetime, timezone
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS 
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomDocumentException 
from utils.model_loader import Model_Loader
from utils.config_loader import load_config

class SingleDocumentLoader:
    def __init__(self, data_dir:str = 'data/single_doc_chat', faiss_dir:str = 'faiss_index'):
        try:
            self.log = CustomLogger().get_logger(__name__ + ".SingleDocumentLoader")
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = Model_Loader()
            self.log.info("Single Document Ingestor initialized successfully.")
            
            self.config = load_config()
        except Exception as e:
            self.log.error(f"Error initializing Single Document Ingestor: {e}")
            raise CustomDocumentException("Error initializing Single Document Ingestor", sys)
    
    def _detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read(100000)  # Read a portion to detect encoding
            result = chardet.detect(raw_data)
            return result['encoding']
        
    def ingest_files(self, uploaded_files, pdf_path):
        try:
            documents = []
            self.log.info(f"Processing file named {uploaded_files}")
            
            for uploaded_file in uploaded_files:
                unique_name = f'session_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}.pdf'
                temp_path = self.data_dir / unique_name
                
                #--------------------------------------
                self.log.info(f"Processing file at {temp_path}")
                # with open(temp_path, 'wb') as f_out:
                #     f_out.write(uploaded_file.read())
                #--------------------------------------
                self.log.info("PDF saved for ingestion", filename=uploaded_file.name)
                loader = PyPDFLoader(Path(pdf_path))
                docs = loader.load()
                documents.extend(docs)
                
            self.log.info('PDF files loaded', count = len(documents))
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Failed to Ingest file: {e}")
            raise CustomDocumentException("Failed to Ingest file", sys)
        
    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            self.log.info(f"Document chunks created: {len(chunks)}")
            embeddings = self.model_loader.load_embeddings() # Load embeddings for the document chunks
            vectorstore = FAISS.from_documents(chunks,embeddings)
            vectorstore.save_local(str(self.faiss_dir))
            self.log.info(f"FAISS index saved locally at: {self.faiss_dir}")
            retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={'k': self.config['retriever']['top_k']})
            self.log.info(f"Retriever created successfully of {str(type(retriever))}")
            return retriever
        except Exception as e:
            self.log.error(f"Retrieval Creation Failed: {e}")
            raise CustomDocumentException("Retrieval Creation Failed", sys) 