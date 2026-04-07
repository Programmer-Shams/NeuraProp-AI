"""Document chunker — splits documents into embedding-sized chunks."""

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """A single chunk of text ready for embedding."""

    content: str
    chunk_index: int
    metadata: dict


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    document_id: str | None = None,
    source: str | None = None,
) -> list[Chunk]:
    """
    Split text into overlapping chunks for embedding.

    Uses a sentence-aware splitting strategy:
    1. Split on paragraph boundaries first
    2. Then split long paragraphs on sentence boundaries
    3. Merge small chunks to meet minimum size
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[Chunk] = []
    current_chunk = ""
    chunk_index = 0

    for para in paragraphs:
        # If adding this paragraph would exceed chunk_size, finalize current chunk
        if current_chunk and len(current_chunk) + len(para) + 2 > chunk_size:
            chunks.append(Chunk(
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                metadata={"document_id": document_id, "source": source},
            ))
            chunk_index += 1

            # Keep overlap from end of current chunk
            if chunk_overlap > 0:
                overlap_text = current_chunk[-chunk_overlap:]
                # Don't break mid-word
                space_idx = overlap_text.find(" ")
                if space_idx > 0:
                    overlap_text = overlap_text[space_idx + 1:]
                current_chunk = overlap_text + "\n\n"
            else:
                current_chunk = ""

        # If a single paragraph exceeds chunk_size, split on sentences
        if len(para) > chunk_size:
            sentences = _split_sentences(para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        chunk_index=chunk_index,
                        metadata={"document_id": document_id, "source": source},
                    ))
                    chunk_index += 1
                    current_chunk = ""
                current_chunk += sentence + " "
        else:
            current_chunk += para + "\n\n"

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(Chunk(
            content=current_chunk.strip(),
            chunk_index=chunk_index,
            metadata={"document_id": document_id, "source": source},
        ))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex."""
    # Split on sentence-ending punctuation followed by space or end
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]
