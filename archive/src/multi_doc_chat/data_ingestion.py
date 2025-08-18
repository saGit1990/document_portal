import uuid 
from pathlib import Path
import sys 
from datetime import datetime, timezone 

from langchain_community.document_loaders import TextLoader,PyPDFLoader, Docx2txtLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS 

from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomDocumentException 
from utils.model_loader import Model_Loader 

SUPPORTED_FILE_TYPES = {'.txt', '.pdf', '.docx', '.md', '.csv', '.json', '.html'}
class DocumentIngestor:
    def __init__(self, temp_dir: str = 'data/multi_doc_chat', 
                faiss_dir: str = 'faiss_index', session_id: str = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.SUPPORTED_FILE_TYPES = SUPPORTED_FILE_TYPES
            
            # base dir 
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            
            # sessioned path 
            self.session_id = session_id or f'session_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}'
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)
            
            # model loader 
            self.model_loader = Model_Loader()
            self.log.info(
                'Document Initialized',
                temp_path = str(self.session_temp_dir),
                faiss_base = str(self.session_faiss_dir),   
                session_id = self.session_id,
                faiss_path = str(self.session_faiss_dir)
            )
        except Exception as e:
            self.log.error('Failed to initialize DocumentIngestor', error=str(e))
            raise CustomDocumentException('Failed to initialize DocumentIngestor',sys )

    def ingest_files(self, uploaded_files):
        try:
            documents = []
            
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning('Unsupported file type', file_name=uploaded_file.name)
                    continue 
                
                unique_file_name = f'{uuid.uuid4().hex[:8]}{ext}'
                temp_path = self.session_temp_dir / unique_file_name
                
                with open(temp_path, 'wb') as f: 
                    f.write(uploaded_file.read())

                self.log.info(f"File saved for ingestion {unique_file_name}")
                if ext == '.pdf':
                    loader = PyPDFLoader(str(temp_path))
                elif ext == '.docx':
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == '.txt':
                    loader = TextLoader(str(temp_path), encoding='utf-8')
                else:
                    self.log.warning('Unsupported file type', file_name=uploaded_file.name)
                    continue 
                
                docs = loader.load()
                documents.extend(docs)
                
            if not documents:
                raise CustomDocumentException('No documents loaded from the files', sys)
                
            return self._create_retriever(documents)
                    
        except Exception as e:
            self.log.error('Failed to ingest files', error=str(e))
            raise CustomDocumentException('Failed to ingest files', sys)    
    
    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            
            embeddings = self.model_loader.load_embeddings() 
            vector_store = FAISS.from_documents(chunks,embeddings)
            self.log.info('FAISS index saved to disk', path=str(self.session_faiss_dir), session_id=self.session_id)
            retriever = vector_store.as_retriever(search_type='similarity', search_kwargs = {'k':5})
            return retriever 
        except Exception as e:
            self.log.error('Failed to create retriever', error=str(e))
            raise CustomDocumentException('Failed to create retriever', sys)
