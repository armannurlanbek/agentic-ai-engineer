import tiktoken

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
ENCODING = tiktoken.encoding_for_model("gpt-4o")


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def split_into_sentences(text: str) -> list[str]:
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s.strip()]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens > chunk_size:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            sentences = split_into_sentences(para)
            sent_chunk: list[str] = []
            sent_tokens = 0

            for sent in sentences:
                st = count_tokens(sent)
                if sent_tokens + st > chunk_size and sent_chunk:
                    chunks.append(" ".join(sent_chunk))
                    overlap_sents = []
                    overlap_tokens = 0
                    for s in reversed(sent_chunk):
                        ot = count_tokens(s)
                        if overlap_tokens + ot > overlap:
                            break
                        overlap_sents.insert(0, s)
                        overlap_tokens += ot
                    sent_chunk = overlap_sents
                    sent_tokens = overlap_tokens

                sent_chunk.append(sent)
                sent_tokens += st

            if sent_chunk:
                chunks.append(" ".join(sent_chunk))
        else:
            if current_tokens + para_tokens > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                overlap_text = current_chunk[-1] if current_chunk else ""
                ot = count_tokens(overlap_text)
                if ot <= overlap:
                    current_chunk = [overlap_text]
                    current_tokens = ot
                else:
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(para)
            current_tokens += para_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def extract_text_from_file(content: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext in ("txt", "md"):
        return content.decode("utf-8", errors="replace")

    if ext == "pdf":
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == "docx":
        import io
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    return content.decode("utf-8", errors="replace")
