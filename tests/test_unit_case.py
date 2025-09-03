import pytest 
import unittest
from pathlib import Path

from fastapi.testclient import TestClient 
from api.main import app
from src.document_ingestion.data_ingestion import DocumentHandler, ChatIngestor
from src.document_analyzer.data_analysis import DocumentAnalyzer    
from exception.custom_exception import CustomDocumentException 

client = TestClient(app) 

class TestApplicationStatus(unittest.TestCase):
    def test_home(self):
        response = client.get("/") 
        self.assertEqual(response.status_code, 200)  
        self.assertIn("Document Portal", response.text)

    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),  {'status': 'ok', 'service': 'document-portal'})

class TestDocumentHandler(unittest.TestCase):
    def setUp(self):
        self.handler = DocumentHandler(data_dir='test_data',session_id='test_session')

    def test_save_pdf_invalid_extension(self):
        class DummyFile:
            name = 'file.txt'
            def read(self): return b'dummy'

        with self.assertRaises(CustomDocumentException) :
            self.handler.save_pdf(DummyFile())

    def test_save_pdf_valid(self):

        ref_path = Path("tests/test_data/Long_Report_V1.pdf")

        class FakeUpload:
            def __init__(self,file_path:Path):
                self.name = file_path.name
                self._buffer =  file_path.read_bytes()

            def getbuffer(self):
                return self._buffer

        ref_upload = FakeUpload(ref_path)

        path = self.handler.save_pdf(ref_upload)
        self.assertTrue(path.endswith("Long_Report_V1.pdf"))

class TestChatIngestor(unittest.TestCase):
    def setUp(self):
        self.ingestor = ChatIngestor(temp_base='test_data', session_id='test_session')

    def test_resolve_dir(self):
        resolved_path = self.ingestor._resolve_dir(self.ingestor.temp_base)
        self.assertTrue(str(resolved_path).endswith('test_session'))

class TestDocumentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DocumentAnalyzer()

    def test_analyze_empty_document(self):
        result = self.analyzer.analyze_document("")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid document text")

    def test_analyze_valid_document(self):
        result = self.analyzer.analyze_document("This is a test document.")
        self.assertIsNotNone(result)

class TestAPIEndpoints(unittest.TestCase):
    def test_post_chat_index_no_files(self):
        response = client.post("/chat/index", data={})
        self.assertIn(response.status_code, [code for code in range(400,450)])

    def test_post_chat_query_no_question(self):
        response = client.post("/chat/query", data={})
        self.assertIn(response.status_code, [code for code in range(400,450)])

    def test_post_chat_query_valid(self):
        response = client.post("/chat/query", data={"question": "What is AI?", 
                        "session_id": "test_session", "use_session_dirs": False})
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.json())

    def test_post_chat_query_nonexistent_index(self):
        response = client.post("/chat/query", data={"question": "What is AI?", 
                                                    "session_id": "nonexistent_session"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("FAISS index not found", response.text)

if __name__ == "__main__":
    unittest.main()