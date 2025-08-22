from __future__ import annotations 
import re 
import uuid 

from pathlib import Path 
from datetime import datetime, timezone 
from zoneinfo import ZoneInfo 
from typing import Iterable, List 
from logger import custom_logger
from exception.custom_exception import CustomDocumentException 

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"} 
log = custom_logger.CustomLogger().get_logger(__name__)
# ----------------------------- #
# Helpers (file I/O + loading)  #
# ----------------------------- #

def generate_session_id(prefix: str = 'session') -> str:
    """Generate a unique session ID."""
    ist = ZoneInfo("Asia/Kolkata")
    return f"{prefix}_{datetime.now(ist).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def save_uploaded_files(uploaded_files: Iterable, target_dir: Path) -> List[Path]:
    """Save uploaded files to the target directory."""
    try:
        target_dir.mkdir(parents=True, exist_ok=True) 
        saved: List[Path] = [] 
        for uf in uploaded_files: 
            name = getattr(uf, 'name','file')
            ext = Path(name).suffix.lower()  
            if ext not in SUPPORTED_EXTENSIONS: 
                log.warning('Unsupported file skipped', filename=name) 
                continue 
            
            # Clean file name (only alphanum, dash, underscore)
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]','_', Path(name).stem.lower())
            fname = f'{safe_name}_{uuid.uuid4().hex[:8]}{ext}' 
            fname = f'{uuid.uuid4().hex[:8]}{ext}' 
            out = target_dir / fname 
            with open(out, 'wb') as f:
                if hasattr(uf, 'read'):
                    f.write(uf.read())
                else: 
                    f.write(uf.getbuffer()) # fallbase
            saved.append(out)
            log.info('File saved for ingestion', uploaded=name, saved_as=str(out))
        return saved
    except Exception as e: 
        log.error('Failed to save uploaded files', error=str(e), dir=str(target_dir))
        raise CustomDocumentException("Failed to save uploaded files", e) from e 