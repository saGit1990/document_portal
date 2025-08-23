from ast import Dict
import sys 
import os 
import streamlit as st

from dotenv import load_dotenv
from operator import itemgetter 
from typing  import Any, List, Optional, Dict

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS 


from utils.model_loader import Model_Loader
from logger.custom_logger   import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from exception.custom_exception import CustomDocumentException 
from model.models import PromptType

class ConversationRAG:
    def __init__(self, session_id:str, retriever=None):
        """
            LCEL-based Conversational RAG with lazy retriever initialization.

            Usage:
                rag = ConversationalRAG(session_id="abc")
                rag.load_retriever_from_faiss(index_path="faiss_index/abc", k=5, index_name="index")
                answer = rag.invoke("What is ...?", chat_history=[])
        """
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            self.llm = Model_Loader().load_llm()
            self.contextualized_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.retriever = retriever
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()
            self.log.info('ConversationalRAG Initialized', session_id=self.session_id)
            
        except Exception as e:
            self.log.error('Failed to initialize ConversationRAG', error=str(e))
            raise CustomDocumentException('Failed to initialize ConversationRAG', sys)

    def load_retriever_from_faiss(self,index_path: str,k: int = 5,index_name: str = "index",search_type: str = "similarity",search_kwargs: Optional[Dict[str, Any]] = None,):
            """Load FAISS vectorstore from disk and build retriever + LCEL chain."""
            try:
                if not os.path.isdir(index_path):
                    raise FileNotFoundError(f"FAISS index directory not found: {index_path}")

                embeddings = Model_Loader().load_embeddings()
                vectorstore = FAISS.load_local(
                    index_path,
                    embeddings,
                    index_name=index_name,
                    allow_dangerous_deserialization=True,  # ok if you trust the index
                )

                if search_kwargs is None:
                    search_kwargs = {"k": k}

                self.retriever = vectorstore.as_retriever(
                    search_type=search_type, search_kwargs=search_kwargs
                )
                self._build_lcel_chain()

                self.log.info(
                    "FAISS retriever loaded successfully",
                    index_path=index_path,
                    index_name=index_name,
                    k=k,
                    session_id=self.session_id,
                )
                return self.retriever

            except Exception as e:
                self.log.error("Failed to load retriever from FAISS", error=str(e))
                raise CustomDocumentException("Loading error in ConversationalRAG", sys)

    def invoke(self, user_input:str, chat_history:Optional[List[BaseMessage]]=None)->str:
        '''
        Args: 
            user_input (str): Description, 
            chat_history (Optional[List[BaseMessage]], optional): History of chat messages _description_. Defaults to None 
        '''
        try:
            chat_history = chat_history or []
            payload={'input': user_input, 'chat_history': chat_history or []}
            answer = self.chain.invoke(payload)
            if not answer: 
                self.log.warning('No answer generated', session_id=self.session_id)
                return 'No answers generated'
            self.log.info('Answer generated successfully'
                ,session_id=self.session_id
                ,user_input=user_input
                ,answer_preview=answer[:150])
            return answer
        except Exception as e:
            self.log.error('Failed to invoke ConversationRAG', error=str(e))
            raise CustomDocumentException('Failed to invoke ConversationRAG', sys)

    def _load_llm(self):
        try:
            llm = Model_Loader().load_llm() 
            if not llm:
                raise ValueError('LLM could not be loaded')
            self.log.info('LLM loaded successfully', session_id=self.session_id)
            return llm
        except Exception as e:
            self.log.error('Failed to load LLM', error=str(e))
            raise CustomDocumentException('Failed to load LLM', sys)

    @staticmethod
    def _format_docs(docs):
        return '\n\n'.join(d.page_content for d in docs)
    
    def _build_lcel_chain(self):
        try:
            question_rewriter = (
                {'input': itemgetter('input'), 'chat_history': itemgetter('chat_history')}
                | self.contextualized_prompt
                | self.llm
                | StrOutputParser()
            )
            retrieve_docs = question_rewriter | self.retriever | self._format_docs
            self.chain=({
                    'context':retrieve_docs,
                    'input': itemgetter('input'),
                    'chat_history': itemgetter('chat_history'), 
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            self.log.info('LCEL graph built successfully', session_id=self.session_id)
        except Exception as e:
            self.log.error('Failed to build LCEL chain', error=str(e))
            raise CustomDocumentException('Failed to build LCEL chain', sys)