from backend.rag.embeddings import embed_query


async def query_collection(
    query_text: str,
    collection,
    n_results: int = 8,
    max_distance: float = 1.5,
) -> list[dict]:
    if collection.count() == 0:
        return []

    query_embedding = embed_query(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist <= max_distance:
            filtered.append({
                "text": doc,
                "source_file": meta.get("filename", ""),
                "collection": collection.name,
                "relevance_score": 1 - (dist / 2),
                "metadata": meta,
            })

    return filtered
