from __future__ import annotations
from utils.config_loader import load_config_extensions
from pathlib import Path
from typing import Iterable, List
from fastapi import UploadFile
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredPowerPointLoader,
    CSVLoader, UnstructuredMarkdownLoader, UnstructuredXMLLoader,
    UnstructuredExcelLoader, JSONLoader, UnstructuredHTMLLoader,
    UnstructuredEmailLoader, UnstructuredEmailLoader
)
import fitz 
from unstructured.partition.pptx import partition_pptx
from logger import custom_logger
from exception.custom_exception import CustomDocumentException

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt",".pptx", '.csv','.md','.xml',
    '.xlsx','.json','.xml','.html','.htm','.eml','.msg','.jpg','.jpeg','.png'} 

# Map extensions to their respective loaders
# later to be moved onto config file
EXTENSION_LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": lambda path: TextLoader(path, encoding="utf-8"),
    ".pptx": lambda path: UnstructuredPowerPointLoader(path, mode='paged'),
    ".csv": lambda path: CSVLoader(path),
    ".md": lambda path: UnstructuredMarkdownLoader(path),
    ".xml": lambda path: UnstructuredXMLLoader(path),
    ".xlsx": lambda path: UnstructuredExcelLoader(path),
    ".json": lambda path: JSONLoader(path),
    ".html": lambda path: UnstructuredHTMLLoader(path),
    ".htm": lambda path: UnstructuredHTMLLoader(path),
    ".eml": lambda path: UnstructuredEmailLoader(path),
    ".msg": lambda path: UnstructuredEmailLoader(path)
}

log = custom_logger.CustomLogger().get_logger(__name__)

def load_documents(paths: Iterable[Path]) -> List[Document]:
    """Load docs using appropriate loader based on extension."""
    docs: List[Document] = []
    try:
        for p in paths:
            log.info("Loading file", path=str(p))
            ext = p.suffix.lower()
            if ext in EXTENSION_LOADER_MAP:
                log.info("Loading file", path=str(p), extension=ext)
                loader_cls = EXTENSION_LOADER_MAP[ext]
                loader = loader_cls(p)  # type: ignore
                docs.extend(loader.load())
            else:
                log.warning("Unsupported file skipped during loading", path=str(p), extension=ext)
        log.info("Documents loaded", count=len(docs))
        return docs
    except Exception as e:
        log.error("Failed loading documents", error=str(e))
        raise CustomDocumentException("Error loading documents", e) from e

def concat_for_analysis(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
        parts.append(f"\n--- SOURCE: {src} ---\n{d.page_content}")
    return "\n".join(parts)

def concat_for_comparison(ref_docs: List[Document], act_docs: List[Document]) -> str:
    left = concat_for_analysis(ref_docs)
    right = concat_for_analysis(act_docs)
    return f"<<REFERENCE_DOCUMENTS>>\n{left}\n\n<<ACTUAL_DOCUMENTS>>\n{right}"

# ---------- Helpers ----------
class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

def read_pdf_via_handler(handler, path: str) -> str:
    if hasattr(handler, "read_pdf"):
        return handler.read_pdf(path)  # type: ignore
    if hasattr(handler, "read_"):
        return handler.read_(path)  # type: ignore
    raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")

if __name__ == "__main__":
    print("This is a utility module, not meant to be run directly.")
    # fake loader to test load document, I wnat to load .pptx file  
    from tempfile import TemporaryDirectory
    from pathlib import Path
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        sample_pptx = Path("data\dummy_data\suel_1234.pptx")  # Ensure this file exists for testing
        dest_path = tmp_path / "suel_1234.pptx"
        dest_path.write_bytes(sample_pptx.read_bytes())
        loaded_docs = load_documents([dest_path])
        print(f"Loaded {len(loaded_docs)} documents.")
        for doc in loaded_docs:
            print(f"Document from {doc.metadata.get('source')}, content length: {len(doc.page_content)}")