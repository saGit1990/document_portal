import pytest 
from pathlib import Path
from fastapi.testclient import TestClient 
from api.main import app
from src.document_ingestion.data_ingestion import DocumentHandler, ChatIngestor
from src.document_analyzer.data_analysis import DocumentAnalyzer    
from exception.custom_exception import CustomDocumentException 

client = TestClient(app)

# -------------------- Application Status --------------------

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Document Portal" in response.text

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'service': 'document-portal'}

# -------------------- DocumentHandler --------------------

@pytest.fixture
def document_handler():
    return DocumentHandler(data_dir='test_data', session_id='test_session')

def test_save_pdf_invalid_extension(document_handler):
    class DummyFile:
        name = 'file.txt'
        def read(self): return b'dummy'

    with pytest.raises(CustomDocumentException):
        document_handler.save_pdf(DummyFile())

def test_save_pdf_valid(document_handler):
    ref_path = Path("test_data/test_session/Long_Report_V1.pdf")

    class FakeUpload:
        def __init__(self, file_path: Path):
            self.name = file_path.name
            self._buffer = file_path.read_bytes()

        def getbuffer(self):
            return self._buffer

    ref_upload = FakeUpload(ref_path)
    path = document_handler.save_pdf(ref_upload)
    assert path.endswith("Long_Report_V1.pdf")

# -------------------- ChatIngestor --------------------

@pytest.fixture
def chat_ingestor():
    return ChatIngestor(temp_base='test_data', session_id='test_session')

def test_resolve_dir(chat_ingestor):
    resolved_path = chat_ingestor._resolve_dir(chat_ingestor.temp_base)
    assert str(resolved_path).endswith('test_session')

# -------------------- DocumentAnalyzer --------------------

@pytest.fixture
def analyzer():
    return DocumentAnalyzer()

def test_analyze_empty_document(analyzer):
    result = analyzer.analyze_document("")
    assert "error" in result
    assert result["error"] == "Invalid document text"

def test_analyze_valid_document(analyzer):
    result = analyzer.analyze_document("This is a test document.")
    assert result is not None

# -------------------- API Endpoints --------------------

def test_post_chat_index_no_files():
    response = client.post("/chat/index", data={})
    assert response.status_code in range(400, 450)

def test_post_chat_query_no_question():
    response = client.post("/chat/query", data={})
    assert response.status_code in range(400, 450)

def test_post_chat_query_valid():
    response = client.post("/chat/query", data={
        "question": "What is AI?",
        "session_id": "test_session",
        "use_session_dirs": False
    })
    assert response.status_code == 200
    assert "answer" in response.json()

def test_post_chat_query_nonexistent_index():
    response = client.post("/chat/query", data={
        "question": "What is AI?",
        "session_id": "nonexistent_session"
    })
    assert response.status_code == 404
    assert "FAISS index not found" in response.text

if __name__ == "__main__":
    pytest.main()