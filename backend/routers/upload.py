import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.responses import UploadListItem, UploadResponse
from backend.rag.chroma_client import get_context_collection, get_voice_collection
from backend.rag.ingest import ingest_document
from backend.utils.text_processing import extract_text_from_file

router = APIRouter()

_upload_registry: dict[str, dict] = {}


@router.post("/upload/voice", response_model=UploadResponse)
async def upload_voice_sample(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    description: str = Form(default=""),
):
    content = await file.read()
    text = extract_text_from_file(content, file.filename or "unknown.txt")
    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty or unreadable")

    file_id = str(uuid.uuid4())
    collection = get_voice_collection(user_id)
    chunks_stored = await ingest_document(text, file_id, file.filename or "", collection)

    _upload_registry[file_id] = {
        "file_id": file_id,
        "filename": file.filename or "",
        "upload_type": "voice",
        "user_id": user_id,
        "chunk_count": chunks_stored,
        "uploaded_at": time.time(),
        "description": description,
    }

    return UploadResponse(
        file_id=file_id,
        filename=file.filename or "",
        chunks_stored=chunks_stored,
    )


@router.post("/upload/context", response_model=UploadResponse)
async def upload_context_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    description: str = Form(default=""),
):
    content = await file.read()
    text = extract_text_from_file(content, file.filename or "unknown.txt")
    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty or unreadable")

    file_id = str(uuid.uuid4())
    collection = get_context_collection(user_id)
    chunks_stored = await ingest_document(text, file_id, file.filename or "", collection)

    _upload_registry[file_id] = {
        "file_id": file_id,
        "filename": file.filename or "",
        "upload_type": "context",
        "user_id": user_id,
        "chunk_count": chunks_stored,
        "uploaded_at": time.time(),
        "description": description,
    }

    return UploadResponse(
        file_id=file_id,
        filename=file.filename or "",
        chunks_stored=chunks_stored,
    )


@router.get("/uploads/{user_id}", response_model=list[UploadListItem])
async def list_uploads(user_id: str):
    items = [
        UploadListItem(**v)
        for v in _upload_registry.values()
        if v["user_id"] == user_id
    ]
    return sorted(items, key=lambda x: x.uploaded_at, reverse=True)


@router.delete("/uploads/{file_id}")
async def delete_upload(file_id: str, user_id: str):
    record = _upload_registry.get(file_id)
    if not record or record["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Upload not found")

    if record["upload_type"] == "voice":
        collection = get_voice_collection(user_id)
    else:
        collection = get_context_collection(user_id)

    chunk_ids = [f"{file_id}_chunk_{i}" for i in range(record["chunk_count"])]
    try:
        collection.delete(ids=chunk_ids)
    except Exception:
        pass

    del _upload_registry[file_id]
    return {"status": "deleted", "file_id": file_id}
