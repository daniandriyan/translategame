"""
FastAPI Server - REST API untuk Emulator Game Translator
Backend service untuk Flutter frontend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import os
import shutil
from pathlib import Path
import uuid
import json

# Import core modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rom_loader import ROMLoader, ROMInfo
from core.text_extractor import TextExtractor, TextEntry
from core.text_injector import TextInjector
from core.patch_builder import PatchBuilder
from translators.g4f_translator import G4FTranslator
from translators.ollama_translator import OllamaTranslator
from translators.hf_translator import HFTranslator
from translators.cache import TranslationCache
from translators.queue_manager import QueueManager
from utils.project_manager import ProjectManager
from config import APP_INFO, TRANSLATION_CONFIG

# Setup FastAPI app
app = FastAPI(
    title=APP_INFO["name"],
    description="REST API for Emulator Game Translator",
    version=APP_INFO["version"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Global State ===
class AppState:
    def __init__(self):
        self.current_rom_path: Optional[str] = None
        self.current_rom_info: Optional[ROMInfo] = None
        self.extracted_texts: List[TextEntry] = []
        self.queue_manager: Optional[QueueManager] = None
        self.cache = TranslationCache()
        self.project_manager = ProjectManager()
        
        # Init translators
        self.translators = {}
        primary = TRANSLATION_CONFIG["primary_provider"]
        if primary == "g4f":
            self.translators["g4f"] = G4FTranslator()
        elif primary == "ollama":
            self.translators["ollama"] = OllamaTranslator()
        elif primary == "huggingface":
            self.translators["huggingface"] = HFTranslator()
        
        for provider in TRANSLATION_CONFIG["fallback_providers"]:
            if provider not in self.translators:
                if provider == "g4f":
                    self.translators["g4f"] = G4FTranslator()
                elif provider == "ollama":
                    self.translators["ollama"] = OllamaTranslator()
                elif provider == "huggingface":
                    self.translators["huggingface"] = HFTranslator()

state = AppState()

# === Upload Directory ===
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# === Pydantic Models ===
class TranslationRequest(BaseModel):
    texts: List[str]
    source_lang: str = "auto"
    target_lang: str = "Indonesian"

class TranslationEntry(BaseModel):
    original: str
    translated: str
    offset: int
    is_translated: bool
    needs_review: bool = False

class TextUpdate(BaseModel):
    index: int
    translated_text: str

class ExportRequest(BaseModel):
    format: str = "json"  # json, xdelta, ips
    output_path: Optional[str] = None

# === API Endpoints ===

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "app": APP_INFO["name"],
        "version": APP_INFO["version"]
    }

@app.get("/api/status")
async def get_status():
    """Get app status"""
    return {
        "rom_loaded": state.current_rom_info is not None,
        "rom_info": {
            "game_title": state.current_rom_info.game_title if state.current_rom_info else None,
            "emulator_type": state.current_rom_info.emulator_type if state.current_rom_info else None,
            "region": state.current_rom_info.region if state.current_rom_info else None,
        } if state.current_rom_info else None,
        "texts_count": len(state.extracted_texts),
        "translated_count": sum(1 for t in state.extracted_texts if t.is_translated),
    }

@app.post("/api/rom/upload")
async def upload_rom(file: UploadFile = File(...)):
    """Upload ROM file"""
    try:
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_name
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load ROM
        loader = ROMLoader()
        rom_info = loader.load_rom(str(file_path))
        
        if not rom_info.is_valid:
            raise HTTPException(status_code=400, detail=rom_info.error_message)
        
        # Save state
        state.current_rom_path = str(file_path)
        state.current_rom_info = rom_info
        
        logger.info(f"ROM uploaded and loaded: {rom_info.game_title}")
        
        return {
            "status": "success",
            "rom_info": {
                "game_title": rom_info.game_title,
                "emulator_type": rom_info.emulator_type,
                "region": rom_info.region,
                "file_size": rom_info.file_size,
                "file_name": rom_info.file_name,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading ROM: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rom/extract")
async def extract_texts():
    """Extract texts from loaded ROM"""
    try:
        if not state.current_rom_info:
            raise HTTPException(status_code=400, detail="No ROM loaded")
        
        # Read ROM data
        loader = ROMLoader()
        rom_data = loader.load_rom(state.current_rom_path).is_valid and loader.read_rom_data()
        
        # Extract texts
        extractor = TextExtractor()
        texts = extractor.extract_from_rom(rom_data, state.current_rom_info.emulator_type)
        extractor.filter_texts(min_length=3)
        
        # Save to state
        state.extracted_texts = extractor.extracted_texts
        
        stats = extractor.get_stats()
        
        return {
            "status": "success",
            "texts_count": stats["total_texts"],
            "texts": [
                {
                    "original": t.original_text,
                    "translated": t.translated_text,
                    "offset": t.offset,
                    "is_translated": t.is_translated,
                    "needs_review": t.needs_review,
                }
                for t in state.extracted_texts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting texts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_texts(background_tasks: BackgroundTasks, request: Optional[TranslationRequest] = None):
    """Start translation"""
    try:
        if not state.extracted_texts:
            raise HTTPException(status_code=400, detail="No texts to translate")
        
        # Get pending texts
        pending = [t for t in state.extracted_texts if not t.is_translated]
        
        if not pending:
            return {
                "status": "already_translated",
                "message": "All texts already translated"
            }
        
        # Create queue manager
        state.queue_manager = QueueManager(
            translators=state.translators,
            cache=state.cache
        )
        
        # Add texts
        texts_to_translate = [t.original_text for t in pending]
        state.queue_manager.add_texts(texts_to_translate)
        
        # Start translation in background
        def on_complete(results):
            # Update texts with results
            for i, entry in enumerate(pending):
                if i < len(results):
                    entry.translated_text = results[i]
                    entry.is_translated = True
        
        state.queue_manager.on_complete = on_complete
        state.queue_manager.start()
        
        return {
            "status": "started",
            "texts_count": len(texts_to_translate)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting translation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/translate/progress")
async def get_translation_progress():
    """Get translation progress"""
    if not state.queue_manager or not state.queue_manager.is_running:
        total = len(state.extracted_texts)
        translated = sum(1 for t in state.extracted_texts if t.is_translated)
        
        return {
            "is_running": False,
            "total": total,
            "translated": translated,
            "progress": (translated / total * 100) if total > 0 else 0
        }
    
    progress = state.queue_manager.get_progress()
    return progress

@app.get("/api/texts")
async def get_texts():
    """Get all extracted texts"""
    return {
        "texts": [
            {
                "original": t.original_text,
                "translated": t.translated_text,
                "offset": t.offset,
                "is_translated": t.is_translated,
                "needs_review": t.needs_review,
            }
            for t in state.extracted_texts
        ]
    }

@app.put("/api/texts/{index}")
async def update_text(index: int, update: TextUpdate):
    """Update single text translation"""
    try:
        if index < 0 or index >= len(state.extracted_texts):
            raise HTTPException(status_code=404, detail="Text index out of range")
        
        entry = state.extracted_texts[index]
        entry.translated_text = update.translated_text
        entry.is_translated = True
        entry.needs_review = True
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def export_patch(request: ExportRequest):
    """Export translation patch"""
    try:
        if not state.extracted_texts:
            raise HTTPException(status_code=400, detail="No texts to export")
        
        translated = [t for t in state.extracted_texts if t.is_translated]
        
        if not translated:
            raise HTTPException(status_code=400, detail="No translated texts")
        
        # Generate output path
        output_path = request.output_path or str(
            UPLOAD_DIR / f"{state.current_rom_info.game_title}_translation.{request.format}"
        )
        
        patch_builder = PatchBuilder()
        
        if request.format == "json":
            success = patch_builder.create_json_patch(translated, output_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create patch")
        
        return {
            "status": "success",
            "output_path": output_path,
            "texts_count": len(translated)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting patch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inject")
async def inject_to_rom():
    """Inject translated texts to ROM"""
    try:
        if not state.current_rom_info or not state.extracted_texts:
            raise HTTPException(status_code=400, detail="No ROM or texts")
        
        translated = [t for t in state.extracted_texts if t.is_translated]
        
        # Read original ROM
        with open(state.current_rom_path, 'rb') as f:
            rom_data = bytearray(f.read())
        
        # Inject texts
        injector = TextInjector()
        modified_rom = injector.inject_to_rom(
            rom_data,
            translated,
            state.current_rom_info.emulator_type
        )
        
        # Save modified ROM
        output_path = str(UPLOAD_DIR / f"{state.current_rom_info.game_title}_translated{Path(state.current_rom_path).suffix}")
        with open(output_path, 'wb') as f:
            f.write(modified_rom)
        
        stats = injector.get_stats()
        
        return {
            "status": "success",
            "output_path": output_path,
            "injected": stats["injected"],
            "failed": stats["failed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error injecting to ROM: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename:path}")
async def download_file(filename: str):
    """Download file from uploads"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(str(file_path), filename=file_path.name)

@app.post("/api/project/save")
async def save_project(output_path: Optional[str] = None):
    """Save project"""
    try:
        if not state.current_rom_info:
            raise HTTPException(status_code=400, detail="No ROM loaded")
        
        output_path = output_path or str(UPLOAD_DIR / f"{state.current_rom_info.game_title}_project.json")
        
        state.project_manager.create_project(state.current_rom_info, state.extracted_texts)
        success = state.project_manager.save_project(output_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save project")
        
        return {"status": "success", "output_path": output_path}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
