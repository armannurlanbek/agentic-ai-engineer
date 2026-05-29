from backend.rag.embeddings import embed_texts
from backend.utils.text_processing import chunk_text


async def ingest_document(
    text: str,
    file_id: str,
    filename: str,
    collection,
    extra_metadata: dict | None = None,
) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0

    ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
    base_meta = extra_metadata or {}
    metadatas = [
        {**base_meta, "file_id": file_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    embeddings = embed_texts(chunks)

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)
